import discord
from discord.ext import commands
from Saber.SaberCore import *
from ..Utils.Converters import DiscordUser
import datetime as dt

genius = lyricsgenius.Genius(GENIUS_API_KEY)
genius.verbose = False
genius.remove_section_headers = True


class Utils(commands.Cog, name='Разное'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="acknowledgments", aliases=("благодарности",))
    @commands.cooldown(1, 10, BucketType.user)
    async def acknowledgments(self, ctx):
        e = discord.Embed()
        e.title = "Благодарности"
        e.colour = SECONDARY_COLOR
        e.description = "Бот существует благодаря этим разработкам! Да здравствует Open Source!"
        e.add_field(name="<:Python:624536559777087490> Python", value="[Узнать больше](https://python.org/)",
                    inline=False)
        e.add_field(name="\N{TABLE TENNIS PADDLE AND BALL} ZEIW",
                    value="[Узнать больше](https://zeiw.me/)", inline=False)
        e.add_field(name="<:Dpy:624536687959080962> discord.py",
                    value="[Узнать больше](https://github.com/Rapptz/discord.py/)", inline=False)
        e.add_field(name="<:bot:628238430706597898> R. Danny",
                    value="[Узнать больше](https://github.com/Rapptz/RoboDanny)", inline=False)
        e.add_field(name="<:bot:628238430706597898> Gear Bot",
                    value="[Узнать больше](https://github.com/gearbot/GearBot)", inline=False)

        await ctx.send(embed=e)

    @commands.command(name="ping", hidden=True)
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

    @commands.command(name='botinfo', aliases=('about',), brief=CMD_INFO['BOTINFO'])
    @commands.cooldown(1, 15, BucketType.user)
    async def _botinfo(self, ctx):
        uptime = int(time.time() - BOT_STARTED_AT)
        uptime = '{:02d} ч. {:02d} м. {:02d} с.'.format(uptime // 3600, (uptime % 3600 // 60), uptime % 60)
        short_sha = repo.git.rev_parse(repo.head.object.hexsha, short=7)
        last_changes = ''

        commits = repo.iter_commits('--all', max_count=3)

        for commit in commits:
            commit_msg = commit.message.replace('\n', ' ').replace('\r', '')
            if len(commit_msg) > 120:
                commit_msg = commit_msg[:120] + "..."
            last_changes += ("[`{0}`]({1}) {2} \n".format(
                commit.hexsha[:7],
                f"https://github.com/runic-tears/saber/commit/{commit.hexsha}",
                commit_msg
            ))

        embed = discord.Embed(colour=SECONDARY_COLOR)
        embed.add_field(name='Последние изменения', value=last_changes, inline=False)
        embed.add_field(name='Время работы', value=f'`{uptime}`')
        embed.add_field(name='Аккаунт создан в', value=self.bot.user.created_at.strftime("%d.%m.%Y %H:%M:%S (UTC)"))
        embed.add_field(name='GitHub', value=f'[Перейти по ссылке](https://github.com/runic-tears/saber)')
        embed.add_field(name='Python', value=f'<:Python:624536559777087490> `{sys.version[:5]}`')
        embed.add_field(name='discord.py', value=f'<:Dpy:624536687959080962> ` {discord.__version__}`')
        embed.add_field(name='Версия', value=f'`{short_sha}`')
        embed.set_author(name=f'{self.bot.user}', icon_url=self.bot.user.avatar_url)
        embed.timestamp = datetime.datetime.utcnow()

        await ctx.send(embed=embed)

        del embed

    @commands.command(name='userinfo', aliases=('info',), brief=CMD_INFO['USERINFO'])
    @commands.cooldown(1, 10, type=BucketType.user)
    async def _userinfo(self, ctx, user: DiscordUser = None):
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
        embed.add_field(name='ID', value=str(user.id))
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

            embed.add_field(name='Присоединился (UTC)',
                            value=f'{(dt.datetime.utcnow() - member.joined_at).days} days ago (`{member.joined_at.strftime("%Y-%m-%d %H:%M:%S.%f")}`)')

        embed.add_field(name='Аккаунт создан (UTC)',
                        value=f'{(dt.datetime.utcnow() - user.created_at).days} days ago (`{user.created_at.strftime("%Y-%m-%d %H:%M:%S.%f")}`)')

        await ctx.send(embed=embed)

        del embed

    @commands.command(name="server", aliases=("guildinfo", "serverinfo"))
    @commands.cooldown(1, 10, BucketType.user)
    async def serverinfo(self, ctx, *, guild=None):
        if guild is None:
            guild = ctx.guild
        elif guild is not None:
            try:
                int(guild)
            except ValueError:
                return await ctx.send(":x: ID сервера не может быть строкой.")

            guild = self.bot.get_guild(int(guild))

            if guild is None:
                return await ctx.send(":warning: Указан неизвестный сервер!")

        e = discord.Embed()
        e.set_author(name=f"{guild.name} ({guild.id})", icon_url=guild.icon_url)
        e.colour = guild.get_role(guild.roles[-1].id).colour
        e.add_field(name="Название сервера", value=guild.name)
        e.add_field(name="ID", value=guild.id)
        e.add_field(name="Регион", value=guild.region)

        info = []
        features = set(guild.features)
        all_features = {
            'PARTNERED': 'Partnered',
            'VERIFIED': 'Verified',
            'DISCOVERABLE': 'Server Discovery',
            'INVITE_SPLASH': 'Invite Splash',
            'VIP_REGIONS': 'VIP Voice Servers',
            'VANITY_URL': 'Vanity Invite',
            'MORE_EMOJI': 'More Emoji',
            'COMMERCE': 'Commerce',
            'LURKABLE': 'Lurkable',
            'NEWS': 'News Channels',
            'ANIMATED_ICON': 'Animated Icon',
            'BANNER': 'Banner'
        }

        for feature, label in all_features.items():
            if feature in features:
                info.append(f'\N{WHITE HEAVY CHECK MARK}: {label}')

        if info:
            e.add_field(name='Фичи', value='\n'.join(info))

        e.add_field(name="Владелец", value=guild.owner)
        e.add_field(name="Участников", value=guild.member_count)
        e.add_field(name="Текстовых каналов", value=str(len(guild.text_channels)))
        e.add_field(name="Сервер создан (UTC)",
                    value=f'{(dt.datetime.utcnow() - guild.created_at).days} days ago (`{guild.created_at.strftime("%Y-%m-%d %H:%M:%S.%f")}`)',
                    inline=False)

        await ctx.send(embed=e)
        del e

    # Взято из https://github.com/Rapptz/RoboDanny
    @commands.command(name="char", aliases=('charinfo',))
    async def _char(self, ctx, *, characters: str):
        """Выводит информацию о символах"""

        def to_string(c):
            digit = f'{ord(c):x}'
            name = unicodedata.name(c, 'Такое имя не найдено')
            return f'`\\U{digit:>08}` \N{EM DASH} `\\N%s{name}%s` \N{EM DASH} {c}' % ("{", "}")

        msg = '\n'.join(map(to_string, characters))
        if len(msg) > 1900:
            return await ctx.send('Слишком длинное сообщение.')
        await ctx.send(embed=discord.Embed(colour=SECONDARY_COLOR, description=msg).set_author(
            name="Команда скопирована из бота Robo Danny", url="https://github.com/Rapptz/RoboDanny"))

    @commands.command(name="lyrics")
    @commands.cooldown(1, 30, BucketType.user)
    async def _lyrics(self, ctx, *, query):
        """Поиск текстов на Genius

        Вы можете указать часть текста, имя исполнителя или название песни и т.п.
        """
        msg = await ctx.send("Начинаю поиск, ждите, это займёт время...")
        try:
            song = genius.search_song(query)

            await asyncio.sleep(0.25)

            if song.artist.lower() in ARTISTS_BLACKLIST:
                return await msg.edit(
                    content=":warning: Простите, но я вывожу тексты настоящих творцов, а не жалкое подобие искусства...")

            result = song.lyrics

            if len(result) >= 2000:
                result = result[:2020] + '\n\n*[...]*\n'

            await msg.edit(content="", embed=discord.Embed(
                colour=SECONDARY_COLOR,
                description=result
            ).set_footer(
                text=f'Команду инциализировал(а) {ctx.author}', icon_url=ctx.author.avatar_url
            ).set_author(
                name=f'{song.artist} — {song.title}', icon_url=song.song_art_image_url, url=song.url
            ).add_field(
                name='Ссылка на Genius', value=f'[Перейти по ссылке]({song.url})'
            ).set_thumbnail(
                url=song.song_art_image_url
            ))

            del song
        except Exception as err:
            await msg.delete()
            raise err


def setup(bot):
    bot.add_cog(Utils(bot))
