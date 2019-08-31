import discord
from discord.ext import commands
from Twig.TwigCore import *
from Twig.Utils.Hugging import sendLove


class Utils(commands.Cog, name='Разное'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="gif")
    @commands.cooldown(1, 45, BucketType.user)
    async def _gif(self, ctx, *, query=None):
        if query is None:
            return await ctx.send(embed=discord.Embed(
                colour=ERROR_COLOR, description=':x: Вы не указали запрос поиска!')
            )

        msg = await ctx.send(":repeat: Выполняю поиск...")

        try:
            embed = discord.Embed()
            query = query.replace(" ", "+")
            url = f"http://api.giphy.com/v1/gifs/search?q={query}&api_key={GIPHY_API}&limit=10"
            session = aiohttp.ClientSession()
            response = await session.get(url)
            await session.close()
            gif_choice = random.randint(0, 9)
            data = json.loads(await response.text())
            img_data = {
                "original_url": data['data'][gif_choice]['images']['original']['url'],
                "title": data['data'][gif_choice]["title"],
                "url": data['data'][gif_choice]["url"]
            }
            embed.set_image(url=img_data['original_url'])
            embed.description = f"[→ {img_data['title']}]({img_data['original_url']})"
            embed.set_footer(text=f"Запрошено пользователем {str(ctx.author)}", icon_url=ctx.author.avatar_url)
            embed.timestamp = datetime.datetime.utcnow()
            url = session = response = gif_choice = data = img_data = None
            return await msg.edit(content='', embed=embed)
        except:
            return await msg.edit(content=":x: Ошибка!")

    @commands.command(name="ping", brief=CMD_INFO['PING'])
    @commands.cooldown(1, 15, BucketType.user)
    async def _ping(self, ctx):
        t1 = time.perf_counter()
        message = await ctx.send(":ping_pong:")
        t2 = time.perf_counter()
        rest = round((t2 - t1) * 1000)
        latency = round(self.bot.latency * 1000)

        return await message.edit(content='', embed=discord.Embed(
            colour=discord.Colour.blue(),
            description=f":heartbeat: HEARTBEAT: **{latency}мс** \n:incoming_envelope: REST: **{rest}мс**"))

    @commands.command(name='hug', brief=CMD_INFO['HUG'])
    @commands.cooldown(1, 10, BucketType.member)
    async def _hug(self, ctx, target: discord.User = None):
        sender = str(ctx.author)
        msg = sendLove(target.mention, sender)
        return await ctx.send(msg)

    @commands.command(name='botinfo', aliases=('about',), brief=CMD_INFO['BOTINFO'])
    @commands.cooldown(1, 15, BucketType.user)
    async def _botinfo(self, ctx):
        uptime = int(time.time() - BOT_STARTED_AT)
        uptime = time.strftime("%H h. %M m. %S s.", time.gmtime(uptime))
        uptime = uptime.replace("h.", "ч.").replace("m.", "мин.").replace("s.", "сек.")
        memberOfGuilds = str(len(self.bot.guilds))
        repo = git.Repo(".git")
        sha = repo.head.object.hexsha
        short_sha = repo.git.rev_parse(sha, short=7)

        embed = discord.Embed(
            title=f'{self.bot.user.name}',
            description='Привет! Я бот, меня зовут Твиг.\n\n',
            colour=SECONDARY_COLOR
        )
        embed.timestamp = datetime.datetime.utcnow()
        embed.description += f'Я использую `Python {sys.version[:5]}` и библиотеку `discord.py v{discord.__version__}`.\n'
        embed.description += f'А ещё я работаю на {memberOfGuilds} серверах!'
        embed.add_field(name='Версия', value=f'`{short_sha}`')
        embed.add_field(name='Аптайм', value=f'`{uptime}`')
        embed.add_field(name='GitHub', value=f'[Перейти по ссылке](https://github.com/runic-tears/twig)')

        return await ctx.send(embed=embed)

    @commands.command(name='userinfo', aliases=('info',), brief=CMD_INFO['USERINFO'])
    @commands.cooldown(1, 10, type=BucketType.user)
    async def _userinfo(self, ctx, user: discord.User = None):
        if user is None:
            user = member = ctx.author
            user = await self.bot.fetch_user(user.id)
        else:
            member = None if ctx.guild is None else ctx.guild.get_member(user.id)

        embed = discord.Embed()

        if user.id in BOT_MAINTAINERS:
            embed.description = '\N{HEAVY BLACK HEART} Это очень классный человек - мой создатель!'

        embed.colour = DEFAULT_COLOR
        embed.set_thumbnail(url=user.avatar_url)
        embed.add_field(name='Имя пользователя', value=f'{user.name}#{user.discriminator}')
        embed.add_field(name='Идентификатор', value=str(user.id))
        embed.add_field(name='Ссылка на аватар', value=f'[Перейти по ссылке]({user.avatar_url})')

        if member is not None:
            embed.colour = member.top_role.colour

            member_status = str(member.status)

            if member_status == 'online':
                member_status = 'В сети'
            elif member_status == 'dnd':
                member_status = 'Не беспокоить'
            elif member_status == 'idle':
                member_status = 'Нет на месте'
            elif member_status == 'offline':
                member_status = 'Не в сети'

            embed.add_field(name='Статус', value=member_status)

            if member.bot is not True:
                if member.activity is not None:
                    if member.activity.type == discord.ActivityType.playing:
                        embed.add_field(name='\N{VIDEO GAME} Играет в', value=f'{member.activity.name}', inline=False)
                    elif member.activity.type == discord.ActivityType.streaming:
                        embed.add_field(name='Стримит', value=f'{member.activity.name}', inline=False)
                    elif member.activity.type == discord.ActivityType.watching:
                        embed.add_field(name='\N{EYES} Смотрит', value=f'{member.activity.name}', inline=False)
                    elif member.activity.type == discord.ActivityType.listening:
                        track_url = f"https://open.spotify.com/track/{member.activity.track_id}"
                        embed.add_field(name='\N{MUSICAL NOTE} Слушает',
                                        value=f'[{member.activity.artist.replace(";", ",")} \N{EM DASH} {member.activity.title}]({track_url})',
                                        inline=False)
                    else:
                        embed.add_field(name='Неизвестный тип активности', value='\U00002753 Неизвестно', inline=False)

            embed.add_field(name='Присоединился в',
                            value=f'`{member.joined_at.strftime("%Y-%m-%d %H:%M:%S.%f %Z%z")} (UTC)`')

        embed.add_field(name='Аккаунт создан в',
                        value=f'`{user.created_at.strftime("%Y-%m-%d %H:%M:%S.%f %Z%z")} (UTC)`')

        return await ctx.send(embed=embed)

    # Взято из https://github.com/Rapptz/RoboDanny
    @commands.command(name="char", aliases=('charinfo',))
    async def _char(self, ctx, *, characters: str):
        def to_string(c):
            digit = f'{ord(c):x}'
            name = unicodedata.name(c, 'Такое имя не найдено')
            return f'`\\U{digit:>08}` \N{EM DASH} `\\N%s{name}%s` \N{EM DASH} {c}' % ("{", "}")

        msg = '\n'.join(map(to_string, characters))
        if len(msg) > 1900:
            return await ctx.send('Слишком длинное сообщение.')
        await ctx.send(embed=discord.Embed(colour=SECONDARY_COLOR, description=msg).set_author(
            name="Команда скопирована из бота Robo Danny", url="https://github.com/Rapptz/RoboDanny"))


def setup(bot):
    bot.add_cog(Utils(bot))
