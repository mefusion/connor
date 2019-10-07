import discord
from discord.ext import commands
from discord.ext.commands import BucketType
from Saber.SaberCore import BOT_PREFIX
from Saber.Utils.ShopGen import *


class Shop(commands.Cog, name='Магазин'):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='shop')
    @commands.guild_only()
    async def _shop(self, ctx):
        if ctx.invoked_subcommand is None:
            return await ctx.send(
                f'Укажите категорию магазина (`{BOT_PREFIX}shop roles` или `{BOT_PREFIX}shop things`)')

    @_shop.command(name='roles', brief='Магазин ролей')
    @commands.guild_only()
    @commands.cooldown(1, 15, BucketType.user)
    async def _shop_roles(self, ctx):
        embed = await generate_roles_shop(ctx.guild.id)
        return await ctx.send(embed=embed)

    @_shop.command(name="things", enabled=False)
    @commands.guild_only()
    @commands.cooldown(1, 15, BucketType.user)
    async def _shop_things(self, ctx):
        return await ctx.send('На данный момент в этом отделе пусто.')

    # TODO: Методы для валидации покупки
    @_shop.group(name="buy", enabled=False)
    @commands.guild_only()
    @commands.cooldown(1, 25, BucketType.user)
    async def _shop_buy(self, ctx):
        if ctx.invoked_subcommand is None:
            return await ctx.send(
                f'Укажите категорию магазина (`roles` или `things`)')

    @_shop_buy.command(name="roles", enabled=False)
    @commands.guild_only()
    @commands.cooldown(1, 25, BucketType.user)
    async def _shop_buy_roles(self, ctx, itemId=None):
        return await ctx.send("Naaah")


def setup(bot):
    bot.add_cog(Shop(bot))
