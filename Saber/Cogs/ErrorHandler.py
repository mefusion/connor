import discord
from discord.ext import commands
import traceback
import sys
from Saber.SaberCore import MAIN_LOGS_CHANNEL, ERROR_COLOR, BOT_IS_NO_PERMS_MSG_ENABLED, BOT_MAINTAINERS


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        log = self.bot.get_channel(MAIN_LOGS_CHANNEL)
        log_embed = discord.Embed(colour=ERROR_COLOR, title=':x: Ошибка!')
        """Это событие вызывается, когда случаются ошибки во время использования команд.
        ctx   : Context
        error : Exception"""

        # Это предотвращает обработку ошибок для команд, с локальным обработчиками
        if hasattr(ctx.command, 'on_error'):
            return

        error = getattr(error, 'original', error)

        # Все типы ошибок, внутри ignored - будут игнорироваться обработчиком
        is_ignore_enabled = False
        ignored = commands.UserInputError

        if is_ignore_enabled:
            if isinstance(error, ignored):
                return

        async def send_here(message):
            await ctx.send(message)

        async def send_here_no_perms():
            if BOT_IS_NO_PERMS_MSG_ENABLED is True:
                await ctx.send(f':lock: У вас нет доступа к команде `{ctx.command}`')
            else:
                return

        # ==== DISCORD PYTHON ERRORS ====

        if isinstance(error, commands.CommandNotFound):
            return

        elif isinstance(error, commands.DisabledCommand):
            return await ctx.send(f'Команда `{ctx.command}` отключена.')

        elif isinstance(error, commands.MissingPermissions):
            return await send_here_no_perms()

        elif isinstance(error, commands.MissingRequiredArgument):
            return await send_here(
                ":warning: Вы пропустили какой-то важный аргумент.\n"
                f"\N{SPIRAL NOTE PAD} Синтаксис команды: "
                f"`{ctx.prefix}{ctx.command.qualified_name} {ctx.command.signature}`"
            )

        elif isinstance(error, commands.BadArgument):
            if ctx.command.qualified_name == 'xp':
                return await ctx.send(embed=discord.Embed(
                    title=':x: Произошла ошибка!',
                    colour=ERROR_COLOR,
                    description='Я не знаю такого пользователя.')
                )

            elif ctx.command.qualified_name == 'erole color':
                return await send_here(":x: Неизвестная роль.")

        elif isinstance(error, commands.errors.NotOwner):
            return await send_here_no_perms()

        elif isinstance(error, commands.BotMissingPermissions):
            return await ctx.send(f":x: Мне недостатчно прав, чтобы это сделать.")

        elif isinstance(error, commands.CheckFailure):
            return await send_here_no_perms()

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(
                    embed=discord.Embed(title=':x: Ошибка!', colour=ERROR_COLOR,
                                        description=f'Команду `{ctx.command}` нельзя использовать в ЛС'))
                return await log.send(
                    embed=discord.Embed(
                        title=':x: Ошибка!', colour=ERROR_COLOR, description=f'{str(error)}').add_field(
                        name='Пытался использовать в ЛС', value=str(ctx.author) + ' (' + str(ctx.author.id) + ')')
                )
            except:
                pass

        elif isinstance(error, discord.Forbidden):
            return await ctx.send(":x: Мне недостаточно прав, чтобы выполнить это действие.")

        # ==== COOLDOWN CHECKS ====

        elif isinstance(error, commands.CommandOnCooldown):
            if ctx.message.author.id in BOT_MAINTAINERS or await ctx.bot.is_owner(ctx.message.author):
                await ctx.reinvoke()
                return
            return await ctx.send(
                f'Вы не можете использовать эту команду ещё **{round(error.retry_after, 2)}** секунд.')

        # Я знаю, что это выглядит просто ужасно, но мне же как-то нужно получать ошибка в самом Discord...
        log_embed.add_field(name='Краткое описание', value=str(error), inline=False)
        log_embed.add_field(name='Сервер', value=f'{ctx.guild.name} (`{ctx.guild.id}`)')
        log_embed.add_field(name='Автор сообщения', value=f'{ctx.author} (`{ctx.author.id}`)')
        await log.send(embed=log_embed)
        log_embed.clear_fields()
        await ctx.send(':x: Произошла непредвиденная ошибка, разработчик уже знает о ней.')
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
