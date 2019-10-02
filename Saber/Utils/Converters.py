import discord
from discord import HTTPException
from discord.ext.commands import UserConverter, BadArgument, Converter
import re

BOT = None


def init(actual_bot):
    global BOT
    BOT = actual_bot


class DiscordUser(Converter):

    def __init__(self, id_only=False) -> None:
        super().__init__()
        self.id_only = id_only

    async def convert(self, ctx, argument):
        user = None
        match = re.compile("<@!?([0-9]+)>").match(argument)
        if match is not None:
            argument = match.group(1)
        try:
            user = await UserConverter().convert(ctx, argument)
        except BadArgument:
            try:
                user = await BOT.fetch_user(
                    await RangedInt(min=20000000000000000, max=9223372036854775807).convert(ctx, argument))
            except (ValueError, HTTPException):
                pass

        if user is None or (self.id_only and str(user.id) != argument):
            raise BadArgument()
        return user


class RangedInt(Converter):

    def __init__(self, min=None, max=None) -> None:
        self.min = min
        self.max = max

    async def convert(self, ctx, argument) -> int:
        try:
            argument = int(argument)
        except ValueError:
            raise BadArgument()
        else:
            if self.min is not None and argument < self.min:
                raise BadArgument()
            elif self.max is not None and argument > self.max:
                raise BadArgument()
            else:
                return argument

# The whole converter was taken from Gear Bot, because I'm bad. Huge thanks to Gear Bot's developers and contributors
# Весь конвертер был взят из исходного кода Gear Bot, потому что я слишком глуп. Огомная благодарность всем разработчикам и контрибьюторам Gear Bot
# Gear Bot Repository: https://github.com/gearbot/GearBot
