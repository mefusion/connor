import discord
from discord.ext import commands
import datetime as dt

BOT = None


def init(actual_bot):
    global BOT
    BOT = actual_bot


class ModLog:
    def __init__(self, guild, embed=False) -> None:
        super().__init__()
        self.embed = embed
        self.guild = guild
        self.bot = BOT

    async def generate_message(self, initiator=None, punished=None, action=None, channel=None, additional=None, reason=None):
        if initiator is not None:
            initiator = self.bot.get_user(initiator)

        if punished is not None:
            punished = await self.bot.fetch_user(punished)

        if reason is None:
            reason = 'Причина не указана.'

        punished_at = dt.datetime.utcnow().strftime('UTC: %H:%M:%S')

        if action == 'ban':
            return f"[`{punished_at}`] " \
                   f"Модератор **{initiator}** (`{initiator.id}`) забанил " \
                   f"**{punished}** (`{punished.id}`): `{reason}`"
        elif action == 'kick':
            return f"[`{punished_at}`] " \
                   f"Модератор **{initiator}** (`{initiator.id}`) кикнул " \
                   f"**{punished}** (`{punished.id}`): `{reason}`"
        elif action == 'purge':
            return f"[`{punished_at}`] " \
                   f"Модератор **{initiator}** (`{initiator.id}`) очистил `{additional}` сообщений " \
                   f"в канале #{channel}"
        elif action == 'clear':
            return f"[`{punished_at}`] " \
                   f"Модератор **{initiator}** (`{initiator.id}`) очистил `{additional}` сообщений " \
                   f"у пользователя **{punished}** (`{punished.id}`)"
        else:
            return f"[`{punished_at}`] Модератор **{initiator}** (`{initiator.id}`) что-то сделал..."

    async def inform(self, channel, text, embed=False):
        log = discord.utils.get(self.guild.text_channels, name=channel)

        if log is None:
            return print(
                f"[MODLOGS: {self.guild.name}] Couldn't find a channel named as #{channel}, ignoring...")  # Отменяем процесс логирования, если канал не найден

        await log.send(text)
