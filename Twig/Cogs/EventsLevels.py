import discord
import random
import datetime
from discord.ext import commands
from Twig.TwigCore import BOT_PREFIX, IGNORED_CHANNELS, XP_LOGS_CHANNEL, SECONDARY_COLOR
from Twig.Utils.Sql.Functions.MainFunctionality import *


class EventsLevels(commands.Cog, name='Уровни'):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    @commands.guild_only()
    async def on_message(self, message):
        member = message.author

        if message.guild is None:
            return
        if message.content.startswith(BOT_PREFIX):
            return
        if member.id == self.bot.user.id:
            return
        if member.bot:
            return
        if message.channel.name in IGNORED_CHANNELS:
            return

        # Подготавливаем эмбед сообщение
        temp_embed = discord.Embed(colour=SECONDARY_COLOR)

        # Проверяем, если пользователь лишён возможность иметь опыт
        role = discord.utils.get(message.guild.roles, name="noXP")
        if role in member.roles:
            del role
            return
        del role

        # Проверяем есть ли пользователь в таблице
        user = await fetch_data('xp', 'user', member.id)
        if user is None:
            await add_user(member.id)
            temp_embed.description = f'Пользователь не был найден в базе данных, но успешно добавлен.'

        triggered_at = int(time.time())

        # Получаем верменную метку, когда пользователь получал опыт
        cooldown_stamp = int(await fetch_data('lastTimeEdited', 'user', member.id))

        # Если прошло недостатоно времени (90 секунд) - отменяем процесс
        if triggered_at - cooldown_stamp < 90:
            return

        log_chan = self.bot.get_channel(XP_LOGS_CHANNEL)
        temp_embed.set_author(name=f"{message.author} ({message.author.id})", icon_url=message.author.avatar_url)

        # Получаем текущий баланс
        current_xp = await fetch_data('xp', 'user', member.id)
        temp_embed.add_field(name="Предыдущий баланс", value=current_xp)

        # Генерируем бонус очков опыта
        bonus_xp = random.randint(2, 5)
        updated_xp = current_xp + bonus_xp

        # Добавляем очки опыта
        await update_data('xp', updated_xp, 'user', member.id)
        temp_embed.add_field(name="Добавлено очков", value=bonus_xp)
        del bonus_xp, updated_xp, user

        # Изменяем данные о том, когда менялся баланс
        await update_data('lastTimeEdited', triggered_at, 'user', member.id)
        del triggered_at

        new_xp = await fetch_data('xp', 'user', member.id)
        temp_embed.add_field(name='Обновлённый баланс', value=new_xp)
        temp_embed.timestamp = datetime.datetime.utcnow()

        log_chan = self.bot.get_channel(XP_LOGS_CHANNEL)
        return await log_chan.send(embed=temp_embed)


def setup(bot):
    bot.add_cog(EventsLevels(bot))
