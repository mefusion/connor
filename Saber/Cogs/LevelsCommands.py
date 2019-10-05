from Saber.SaberCore import *
import discord
from discord.ext import commands
from Saber.Utils.Sql.Functions.MainFunctionality import fetch_data, fetch_top5
import Saber.Utils.Sql.Functions.PostgresFunctions as Postgres
from ..Utils.Converters import DiscordUser


class LevelsCommands(commands.Cog, name='Опыт'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='leaders', aliases=('lb', 'leaderboard'),
                      brief='Топ пользователей по количеству опыта на счету')
    @commands.cooldown(1, 20, type=BucketType.user)
    async def _leaders(self, ctx):
        msg = await ctx.send("Выполняю...")
        data = await Postgres.find_top_5(ctx.guild.id)

        embed = discord.Embed(colour=SECONDARY_COLOR, title=f'ТОП-{len(data)} ЛИДЕРОВ')

        for i in range(len(data)):
            temp = data[i]
            balance = temp['balance']
            pos = i + 1
            user = await self.bot.fetch_user(temp['user_id'])
            embed.add_field(name=f'#{pos} - {user.name}', value=f'**{balance} опыта**', inline=False)

            if i == 0:
                embed.set_thumbnail(url=user.avatar_url)

        return await msg.edit(content="", embed=embed)

    @commands.command(name='xp', aliases=('balance', 'bal'), brief='Узнать баланс опыта')
    @commands.cooldown(1, 10, type=BucketType.user)
    async def _xp(self, ctx, user: DiscordUser = None):
        temp_embed = discord.Embed()

        if user is self.bot.user:
            return await ctx.send(f"У меня миллиарды квинтиллионов очков опыта, вы уже програли это сражение.")

        if user is None:
            user = ctx.author

        if user.bot is True:
            return await ctx.send('Нет. Машинам нельзя иметь уровень.')

        current_xp = await Postgres.find_xp(ctx.guild.id, user.id)

        if current_xp is None:
            return await ctx.send(embed=discord.Embed(
                colour=DEFAULT_COLOR, title='Ошибка',
                description='Этот пользователь не отправил ни одного сообщения с того момента, ' +
                            'как я появился на сервере, поэтому его нет в базе данных. \n\n' +
                            'Ему нужно отправить хотя бы одно сообщение, чтобы появится в ней.'))

        temp_embed.colour = 0x7289DA
        temp_embed.description = f'**{current_xp}** очков опыта'
        temp_embed.title = f'Баланс пользователя {str(user)}'
        temp_embed.set_thumbnail(url=user.avatar_url)
        temp_embed.set_footer(text=f'Запрашивает {ctx.author}', icon_url=ctx.author.avatar_url)

        await ctx.send(embed=temp_embed)
        return temp_embed.clear_fields()


def setup(bot):
    bot.add_cog(LevelsCommands(bot))
