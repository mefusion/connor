import discord
from discord.ext import commands
from Twig.TwigCore import *


class BotOwner(commands.Cog, name='Владелец бота'):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(BotOwner(bot))
