import discord
import random
import time
from discord.ext import commands
from Saber.SaberCore import BOT_PREFIX, IGNORED_CHANNELS, XP_LOGS_CHANNEL, SECONDARY_COLOR
import Saber.Utils.Sql.Functions.PostgresFunctions as Postgres
from ..Utils.Configurator import get_xp_log_channel, what_prefix
from ..Utils.Logger import Log


class EventsLevels(commands.Cog, name='Уровни'):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    @commands.guild_only()
    async def on_message(self, msg):
        msg = msg
        member = msg.author
        guild = msg.guild

        if guild is None:
            return
        if msg.content.startswith(await what_prefix(msg.guild.id)) or msg.content.startswith(self.bot.user.mention):
            return
        if member.id == self.bot.user.id:
            return
        if member.bot:
            return
        if msg.channel.name in IGNORED_CHANNELS:
            return

        # Подготавливаем эмбед сообщение
        temp_embed = discord.Embed(colour=SECONDARY_COLOR)

        # Проверяем, если пользователь лишён возможность иметь опыт
        role = discord.utils.get(msg.guild.roles, name="noXP")
        if role in member.roles:
            del role
            return
        del role

        # Проверяем есть ли пользователь в таблице
        user = await Postgres.find_xp(msg.guild.id, member.id)

        if user is None:
            await Postgres.insert_into_db(msg.guild.id, member.id, 0)
            temp_embed.set_author(name=f":new: {msg.author} ({msg.author.id})", icon_url=msg.author.avatar_url)

        triggered_at = int(time.time())

        # Получаем верменную метку, когда пользователь получал опыт
        cooldown_stamp = await Postgres.find_cooldown(msg.guild.id, member.id)

        # Если прошло недостатоно времени (75 секунд) - отменяем процесс
        if triggered_at - cooldown_stamp < 75:
            return

        # Получаем текущий баланс
        current_xp = await Postgres.find_xp(msg.guild.id, member.id)

        # Генерируем бонус очков опыта
        bonus_xp = random.randint(2, 5)
        updated_xp = current_xp + bonus_xp

        # Добавляем очки опыта
        await Postgres.update_balance(msg.guild.id, member.id, updated_xp, triggered_at)
        new_xp = await Postgres.find_xp(msg.guild.id, member.id)

        # Логируем
        log = Log(msg.guild.id)
        log_text = await log.generate_log_data(_type='xp', text=f"**{member}** (`{member.id}`) получил `{bonus_xp}` единиц опыта, новый баланс: `{new_xp}`")
        await log.log_to(channel=(await get_xp_log_channel(msg.guild.id)), text=log_text)

        # Возможно, это то ещё плацебо лол
        del new_xp, bonus_xp, updated_xp, user, current_xp, triggered_at, log


def setup(bot):
    bot.add_cog(EventsLevels(bot))
