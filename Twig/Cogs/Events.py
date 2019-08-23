import discord
from discord.ext import commands
from Twig.TwigCore import *
from Twig.Utils.Logger import Log

command_attrs = {'hidden': True}


class Events(commands.Cog, name='События', command_attrs=command_attrs):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        log = Log()

        if guild.id not in whitelist:
            log.type = 'warning'
            log.data = ":warning: **Обнаружена попытка добавить меня!**\n\n"
            log.data += f"Сервер: **{guild.name}** (`{guild.id}`) (не находится в белом списке)\n"
            log.data += f"Владелец: **{guild.owner}** (`{guild.owner_id}`)"
            await log.send(self.bot)
            del log
            return await guild.leave()

        log.type = 'success'
        log.data = ":inbox_tray: **Новый сервер!**\n\n"
        log.data += f"Сервер: **{guild.name}** (`{guild.id}`)\n"
        log.data += f"Владелец: **{guild.owner}** (`{guild.owner_id}`)"
        return await log.send(self.bot)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        log = Log()
        log.type = 'error'
        log.data = ":outbox_tray: **Я покинул сервер.**\n\n"
        log.data += f"Сервер: **{guild.name}** (`{guild.id}`)\n"
        log.data += f"Владелец: **{guild.owner}** (`{guild.owner_id}`)"
        return await log.send(self.bot)


def setup(bot):
    bot.add_cog(Events(bot))
