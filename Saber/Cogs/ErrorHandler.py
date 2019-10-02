import discord
from discord.ext import commands
from Saber.SaberCore import *


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

        # ==== DISCORD PYTHON ERRORS ====

        if isinstance(error, commands.CommandNotFound):
            return await ctx.send('Что это вообще за команда? Я такую не знаю :(')

        elif isinstance(error, commands.DisabledCommand):
            return await ctx.send(f'Команда `{ctx.command}` отключена.')

        elif isinstance(error, commands.MissingPermissions):
            if BOT_IS_NO_PERMS_MSG_ENABLED is True:
                return await ctx.send(f':lock: У вас нет доступа к команде `{ctx.command}`')
            else:
                return

        elif isinstance(error, commands.errors.NotOwner):
            if BOT_IS_NO_PERMS_MSG_ENABLED is True:
                return await ctx.send(f':lock: У вас нет доступа к команде `{ctx.command}`')
            else:
                return

        elif isinstance(error, commands.BotMissingPermissions):
            if ctx.command.qualified_name == "ban":
                return await ctx.send(f":x: Мне недостатчно прав, чтобы это сделать.")

        elif isinstance(error, commands.CheckFailure):
            if BOT_IS_NO_PERMS_MSG_ENABLED is True:
                return await ctx.send(f':lock: У вас нет доступа к команде `{ctx.command}`')
            else:
                return

        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(embed=discord.Embed(
                title=':warning: Операция прервана!', description='Вы пропустили какой-то важный параметр для команды!',
                colour=WARNING_COLOR).set_footer(
                text='Узнать подробнее о команде: %shelp %s' % (BOT_PREFIX, ctx.command)))

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

        # Обрвботчики для конкретных случаев
        elif isinstance(error, commands.BadArgument):
            if ctx.command.qualified_name == 'xp':
                return await ctx.send(embed=discord.Embed(
                    title=':x: Произошла ошибка!', colour=ERROR_COLOR, description='Я не знаю такого пользователя.'))

            elif ctx.command.qualified_name == 'erole color':
                return await ctx.send(embed=discord.Embed(colour=ERROR_COLOR, description=':x: Роль не найдена.'))

        # ==== COOLDOWN CHECKS ====

        elif isinstance(error, commands.CommandOnCooldown):
            if ctx.message.author.id in BOT_MAINTAINERS or await ctx.bot.is_owner(ctx.message.author):
                await ctx.reinvoke()
                return
            return await ctx.send(
                f'Вы не можете использовать эту команду ещё **{round(error.retry_after, 2)}** секунд.')

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
