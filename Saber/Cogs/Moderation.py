import discord
from discord.ext import commands
from ..Utils.Converters import DiscordUser
from Saber.SaberCore import BOT_MAINTAINERS
from ..Utils.ModLogs import ModLog
from ..Utils.Configurator import get_mod_log_channel


class Moderation(commands.Cog, name='Модерация'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ban")
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, target: discord.Member = None, *, reason: commands.clean_content = None):
        """Выдаёт баны"""
        if target is None:
            return await ctx.send("Вы должны указать участника сервера.")
        elif reason is None:
            reason = "Причина не указана."

        await target.ban(reason=f"[Модератор {ctx.author.id}]: {reason}")
        await ctx.send(f":ok_hand: {target} забанен: `{reason}`")

        message = await ModLog(ctx.guild).generate_message(
            initiator=ctx.author.id, punished=target.id,
            reason=reason, action='ban'
        )
        await ModLog(ctx.guild).inform(await get_mod_log_channel(ctx.guild.id), message)

    @commands.command(name="forceban", aliases=("fban",))
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def force_ban(self, ctx, target: commands.clean_content = None, *, reason: commands.clean_content = None):
        """Выдаёт баны по ID"""
        if target is None:
            return await ctx.send("Вы должны указать ID пользователя.")
        elif reason is None:
            reason = "Причина не указана."

        await ctx.guild.ban(discord.Object(id=target), reason=f"[Модератор {ctx.author.id}]: {reason}")
        await ctx.send(f":ok_hand: {target} забанен: `{reason}`")

        message = await ModLog(ctx.guild).generate_message(
            initiator=ctx.author.id, punished=target,
            reason=reason, action='ban'
        )
        await ModLog(ctx.guild).inform(await get_mod_log_channel(ctx.guild.id), message)

    @commands.command(name="kick")
    @commands.bot_has_permissions(kick_members=True)
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, target: discord.Member = None, *, reason: commands.clean_content = None):
        """Кикает с сервера"""
        if target is None:
            return await ctx.send("Вы должны указать участника сервера.")
        elif reason is None:
            reason = "Причина не указана."

        await target.kick(reason=f"[Модератор {ctx.author.id}]: {reason}")
        await ctx.send(f":ok_hand: {target} кикнут: `{reason}`")

        message = await ModLog(ctx.guild).generate_message(
            initiator=ctx.author.id, punished=target,
            reason=reason, action='kick'
        )
        await ModLog(ctx.guild).inform(await get_mod_log_channel(ctx.guild.id), message)

    @commands.command(name="purge")
    @commands.bot_has_permissions(manage_messages=True, read_message_history=True)
    @commands.has_permissions(manage_messages=True, read_message_history=True)
    async def purge(self, ctx, amount=10):
        """Очистка сообщений в текущем канале"""
        amount = int(amount)

        if amount < 2 or amount > 2000:
            return await ctx.send(":warning: Вы можете очистить минимум 2 и максимум 2000 сообщений.")

        deleted_messages = await ctx.channel.purge(limit=amount)
        await ctx.send(f"\U00002705 Успешно удалено `{len(deleted_messages)}` сообщений.", delete_after=30)

        message = await ModLog(ctx.guild).generate_message(
            initiator=ctx.author.id, action='purge',
            additional=len(deleted_messages), channel=ctx.channel
        )
        await ModLog(ctx.guild).inform(await get_mod_log_channel(ctx.guild.id), message)

    @commands.command(name="clear", aliases=("clean",))
    @commands.bot_has_permissions(manage_messages=True, read_message_history=True)
    @commands.has_permissions(manage_messages=True, read_message_history=True)
    async def clear(self, ctx, target: DiscordUser = None, amount=None):
        """Очистка чьих-либо сообщений"""
        amount = int(amount)

        if amount < 2 or amount > 2000:
            return await ctx.send(":warning: Вы можете очистить минимум 2 и максимум 2000 сообщений.")

        def msgcheck(msg):
            if target:
                return msg.author.id == target.id
            return True

        deleted_messages = await ctx.channel.purge(limit=amount, check=msgcheck)
        await ctx.send(f"\U00002705 Успешно удалено `{len(deleted_messages)}` сообщений.", delete_after=30)

        message = await ModLog(ctx.guild).generate_message(
            initiator=ctx.author.id, punished=target.id,
            additional=len(deleted_messages), action='clear'
        )
        await ModLog(ctx.guild).inform(await get_mod_log_channel(ctx.guild.id), message)


def setup(bot):
    bot.add_cog(Moderation(bot))
