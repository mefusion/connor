import discord
from discord.ext import commands
from Saber.SaberCore import *
from ..Utils.Logger import OldLog
from ..Utils.Converters import DiscordMessageURL
from ..Utils.Configurator import get_whitelist
import Saber.Utils.Sql.Functions.PostgresFunctions as Postgres


class BotOwner(commands.Cog, name='Владелец бота', command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        self.sessions = set()

    async def cog_check(self, ctx):
        return await ctx.bot.is_owner(ctx.author)

    def cleanup_code(self, content):
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])
        return content.strip('` \n')

    @commands.command(name="mem")
    async def _mem(self, ctx):
        memInfo = psutil.Process(os.getpid()).memory_info()

        embed = discord.Embed(colour=SECONDARY_COLOR, title=f":rosette: Memory Usage | PID {os.getpid()}")
        embed.add_field(name="Resident Set Size", value=f"{round(memInfo.rss / 1e+6, 1)} МБ")
        embed.add_field(name="Virtual Memory Size", value=f"{round(memInfo.vms / 1e+6, 1)} МБ")

        del memInfo
        return await ctx.send(embed=embed)

    @commands.group(name="message", aliases=("msg", "✉"))
    @commands.guild_only()
    async def msg(self, ctx):
        if ctx.invoked_subcommand is None:
            return await ctx.send('Вы не указали субкоманду.')

    @msg.command(name="repeat", aliases=('mimic', 'copy'))
    async def msg_repeat(self, ctx, *, _input: str):
        await ctx.send(_input)

    @msg.command(name="edit")
    async def msg_edit(self, ctx, channel_id: int, message_id: int, *, _input: str = None):
        c = self.bot.get_channel(channel_id)

        if c is None:
            return await ctx.send(":x: Неизвестный канал.")

        m = await c.fetch_message(message_id)

        await m.edit(content=_input)

        e = discord.Embed(
            colour=SECONDARY_COLOR,
            description="\N{OK HAND SIGN} Сообщение отредактировано."
        ).add_field(
            name=f"Просмотреть",
            value=f"[Перейти по ссылке]({DiscordMessageURL(ctx.guild.id, channel_id, message_id).url})"
        )

        await ctx.send(embed=e)
        del e

    @commands.command(name='restart')
    async def __restart_bot__(self, ctx):
        await ctx.send(':gear: Перезагрузка...')
        log = OldLog()
        log.data = f':repeat: **Перезагрузка...**\n\n'
        log.data += f'Запрошено пользователем {ctx.author.name}#{ctx.author.discriminator} (`{ctx.author.id}`)'
        await log.send(self.bot)
        return await self.bot.close()

    @commands.command(name="pullv2", aliases=("update", "pull"))
    async def pullv2(self, ctx):
        pull = subprocess.Popen(['git', 'pull', 'origin', 'master'],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        stdout, stderr = pull.communicate()

        if stderr is None:
            return await ctx.send('```yaml\n' + f'{stdout.decode("utf-8")}' + '\n```')
        else:
            return await ctx.send('```yaml\n' + f'{stderr.decode("utf-8")}' + '\n```')

    @commands.command(pass_context=True, hidden=True, name='eval')
    @commands.is_owner()
    async def _eval(self, ctx, *, body: str):
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'msg': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')

    # ==== STATuS COMMANDS ==== #

    @commands.group(name="status")
    async def _status(self, ctx):
        """Манипулирование со статусом бота"""
        if ctx.invoked_subcommand is None:
            return await ctx.send('Вы не указали субкоманду.')

    @_status.command(name="reset")
    async def _status_reset(self, ctx):
        """Сбрасывает статус бота на статус по умолчанию"""
        stat = discord.Activity(name="Сбрасывание статуса...", type=discord.ActivityType.playing)
        await self.bot.change_presence(activity=stat)
        await asyncio.sleep(0.5)
        await self.bot.change_presence(activity=DEFAULT_STATUS)

        del stat
        return await ctx.send(":ok_hand: Статус успешно сброшен.")

    @_status.command(name="set")
    async def _status_set(self, ctx, stype, *, text):
        """Изменение статуса"""
        if (stype == 'playing') or (stype == '1'):
            playing_now = discord.Activity(name=str(text), type=discord.ActivityType.playing)
        elif (stype == 'watching') or (stype == '2'):
            playing_now = discord.Activity(name=str(text), type=discord.ActivityType.watching)
        elif (stype == 'listening') or (stype == '3'):
            playing_now = discord.Activity(name=str(text), type=discord.ActivityType.listening)
            # Немного сломано, нужно понять в чём проблема.
        elif (stype == 'streaming') or (stype == '4'):
            if " | " not in text:
                return await ctx.send("Ссылку обязательно нужно указать `<название> | <ссылка>`")
            text = text.split(" | ")
            playing_now = discord.Activity(name=str(text[0]), url=str(text[1]), type=discord.ActivityType.streaming)
        else:
            playing_now = discord.Activity(name=str(text), type=discord.ActivityType.playing)

        await self.bot.change_presence(activity=playing_now)

        del playing_now, text, stype
        return await ctx.send(":ok_hand: Статус успешно изменён.")

    # ==== GUILD COMMANDS ==== #

    @commands.group(name='guild')
    async def _guild(self, ctx):
        """Манипуляции с серверами, где я есть"""
        if ctx.invoked_subcommand is None:
            return await ctx.send('Вы не указали субкоманду (`leave`, `list`)')

    @_guild.command(name='list')
    async def _guild_list(self, ctx):
        guilds_ls = self.bot.guilds
        resulting_txt = "```xl\n"
        for i in range(len(guilds_ls)):
            resulting_txt = resulting_txt + "\n" + str(guilds_ls[i]) + " (" + str(guilds_ls[i].id) + ")"

        resulting_txt += "```"
        del guilds_ls
        return await ctx.send(resulting_txt)

    @_guild.command(name='leave')
    async def _guild_leave(self, ctx, guild_id):
        try:
            guild = self.bot.get_guild(int(guild_id))
            await guild.leave()
            await ctx.send(f"Я успешно покинул сервер **{guild.name}** (`{guild.id}`)")
        except Exception as err:
            await ctx.send('Произошла ошибка.')
            log = OldLog()
            log.type = 'error'
            log.data = ':x: **Ошибка!**\n\n'
            log.data += f'{str(err)}'
            return await log.send(self.bot)

    @_guild.command(name="whitelist")
    async def _guild_whitelist(self, ctx):
        guilds_whitelist = await get_whitelist()
        guilds_formatted = "# Белый список серверов:\n"

        for guild_id in guilds_whitelist:
            guilds_formatted += f"- {guild_id}\n"

        await ctx.send("```yaml\n" + guilds_formatted + "```")

    # ==== COG COMMANDS ==== #

    @commands.group(name='cog')
    async def _cog(self, ctx):
        if ctx.invoked_subcommand is None:
            return await ctx.send('Вы не указали субкоманду (`load`, `unload`, `refresh`)')

    @_cog.command(name='load')
    async def _cog_load(self, ctx, *, cog: str):
        if not cog == "jishaku":
            cog = f'Twig.Cogs.{cog}'
        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ОШИБКА:`** {type(e).__name__} - {e}')
        else:
            await ctx.send(f'**`УСПЕХ`** - Модуль `{cog}` успешно загружен!')

    @_cog.command(name='unload')
    async def _cog_unload(self, ctx, *, cog: str):
        cog = f'Twig.Cogs.{cog}'
        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ОШИБКА:`** {type(e).__name__} - {e}')
        else:
            await ctx.send(f'**`УСПЕХ`** - Модуль `{cog}` успешно выгружен!')

    @_cog.command(name='refresh')
    async def _cog_refresh(self, ctx, *, cog: commands.clean_content):
        cog = f'Twig.Cogs.{cog}'
        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ОШИБКА:`** {type(e).__name__} - {e}')
        else:
            await ctx.send(f'**`УСПЕХ`** -  Модуль `{cog}` успешно перезагружен!')

    @commands.group(name='master-cfg')
    async def _master_cfg(self, ctx):
        if ctx.invoked_subcommand is None:
            return await ctx.send(f"Вы не указали субкоманду, изучите `{ctx.prefix}help {ctx.command}`")

    @_master_cfg.command(name='edit')
    async def _master_cfg_edit(self, ctx, *, parameters: commands.clean_content = None):
        """Изменяет параметры конфигурации

        Аргумент должен иметь вид: <параметр> | <значение>
        """
        if parameters is None:
            return await ctx.send("Вы не указали параметры")
        return await ctx.send(f"In dev stage \nArguments were taken: `{parameters}` \n//TODO: Editing master.yml")


def setup(bot):
    bot.add_cog(BotOwner(bot))
