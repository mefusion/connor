import discord
from discord.ext import commands
from Saber.SaberCore import *
from Saber.Utils.Hugging import sendLove


class Fun(commands.Cog, name='Досуг'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='hug')
    @commands.cooldown(1, 10, BucketType.member)
    async def _hug(self, ctx, target: discord.User = None):

        """Обнимает всяких разных людишек с:"""

        if target is None:
            return await ctx.send("Упс, кажется вы забыли указать человека!")

        sender = str(ctx.author)
        msg = sendLove(target.mention, sender)
        return await ctx.send(msg)

    @commands.command(name="compare", aliases=('choose',))
    @commands.cooldown(1, 5, BucketType.user)
    async def _compare(self, ctx, *things: commands.clean_content):
        """Случайный выбор из списка

        Чтобы указать несколько вариантов, используйте двойные кавычки: "thing 1" ... "thing 5"
        """
        if len(things) < 2:
            return await ctx.send('Но ведь тут нет выбора \N{THINKING FACE}')
        elif len(things) > 250:
            return await ctx.send("Вы пытаетесь сравнить слишком многое...")

        return await ctx.send(embed=discord.Embed(
            title=f'Рандомайзер {len(things) * 3 * 1000}',
            colour=SECONDARY_COLOR,
            description=f'Думаю, лучший выбор - это **{random.choice(things)}**.',
            timestamp=datetime.datetime.utcnow()
        ).set_footer(
            text=f'Инициализировал {ctx.author}', icon_url=ctx.author.avatar_url
        ))

    @commands.command(name="gif")
    @commands.cooldown(1, 45, BucketType.user)
    async def _gif(self, ctx, *, query=None):

        """Находит всякие гифки"""

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

            del url, session, response, gif_choice, data, img_data
            return await msg.edit(content='', embed=embed)
        except:
            try:
                del url, session, response, gif_choice, data, img_data
            except:
                pass

            return await msg.edit(
                content=":x: Ошибка!\n"
                        "\N{SPIRAL NOTE PAD}И нет, мой создатель не имеет ни малейшего понятия как это исправить, все вопросы к создателям API Giphy."
            )


def setup(bot):
    bot.add_cog(Fun(bot))
