import discord
from discord.ext import commands
from Twig.TwigCore import *
from Twig.Utils.Logger import Log


class BotOwner(commands.Cog, name='Владелец бота'):
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

    @commands.command(name='repeat', aliases=['mimic', 'copy'], hidden=True)
    @commands.is_owner()
    @commands.guild_only()
    async def do_repeat(self, ctx, *, inp: str):
        return await ctx.send(inp)

    @commands.command(name='restart')
    @commands.is_owner()
    async def __restart_bot__(self, ctx):
        await ctx.send(':gear: Перезагрузка...')
        log = Log()
        log.data = f':repeat: **Перезагрузка...**\n\n'
        log.data += f'Запрошено пользователем {ctx.author.name}#{ctx.author.discriminator} (`{ctx.author.id}`)'
        await log.send(self.bot)
        return await self.bot.close()

    @commands.command(name="pullv2")
    @commands.is_owner()
    async def pullv2(self, ctx):
        pull = subprocess.Popen(['git', 'pull', 'origin', 'master'],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)
        stdout, stderr = pull.communicate()

        if stderr is None:
            return await ctx.send('```yaml\n' + f'{stdout.decode("utf-8")}' + '\n```')
        else:
            return await ctx.send('```yaml\n' + f'{stderr.decode("utf-8")}' + '\n```')

    # @commands.command(aliases=['update'])
    # @commands.is_owner()
    # async def pull(self, ctx):
    #     message = await ctx.send(':repeat: Pulling from `origin` `master`...')
    #     repo = git.Repo('.git')
    #     assert not repo.bare
    #     repository = repo.remotes.origin
    #     repository.fetch()
    #     repository.pull()
    #     await message.edit(content='**✓** `origin` fetched & pulled successfully!')
    #     del repo, message, repository

    @commands.command(pass_context=True, hidden=True, name='eval')
    @commands.is_owner()
    async def _eval(self, ctx, *, body: str):
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
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

    # ==== GUILD COMMANDS ==== #

    @commands.group(name='guild', brief='Манипуляции с серверами, где я есть')
    async def _guild(self, ctx):
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
            log = Log()
            log.type = 'error'
            log.data = ':x: **Ошибка!**\n\n'
            log.data += f'{str(err)}'
            return await log.send(self.bot)

    # ==== COG COMMANDS ==== #

    @commands.group(name='cog')
    async def _cog(self, ctx):
        if ctx.invoked_subcommand is None:
            return await ctx.send('Вы не указали субкоманду (`load`, `unload`, `refresh`)')

    @_cog.command(name='load')
    async def _cog_load(self, ctx, *, cog: str):
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
    async def _cog_refresh(self, ctx, *, cog: str):
        cog = f'Twig.Cogs.{cog}'
        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ОШИБКА:`** {type(e).__name__} - {e}')
        else:
            await ctx.send(f'**`УСПЕХ`** -  Модуль `{cog}` успешно перезагружен!')


def setup(bot):
    bot.add_cog(BotOwner(bot))
