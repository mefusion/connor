import discord
from discord.ext import commands
from Saber.SaberCore import *


class Welcomer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Игнорируем ботов
        if member.bot:
            return

        # Получаем конфигурацию для сервера
        __temp__ = open(f"./Config/{member.guild.id}/guildSettings.yml", "r")
        guildSettings = yaml.safe_load(__temp__)
        __temp__.close()

        # Отменяем, если отключено
        if guildSettings['WELCOMER']['ENABLED'] is False:
            return

        # Получем канал для отправки сообщений
        welcommingChannel = guildSettings['WELCOMER']['CHANNEL']
        welcommingChannel = self.bot.get_channel(welcommingChannel)

        # Получаем кол.-во участников
        memCount = member.guild.member_count

        # Отправляем приветствие
        msg = await welcommingChannel.send(embed=discord.Embed(
            colour=0xFFFFFF,
            description=f'Хэй, **{member.name}**! Добро пожаловать к нам!'
        ).set_footer(text=f"Участник #{memCount}").set_author(name=f"{member}").set_thumbnail(url=member.avatar_url))

        return await msg.delete(delay=guildSettings['WELCOMER']['MESSAGE_LIVES'])


def setup(bot):
    bot.add_cog(Welcomer(bot))
