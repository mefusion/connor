import discord
import Saber.Utils.Sql.Functions.PostgresFunctions as Postgres
from discord.ext import commands
from discord.ext.commands import BucketType
from Saber.SaberCore import BOT_PREFIX
from Saber.Utils.ShopGen import *
from Saber.SaberCore import SECONDARY_COLOR, ERROR_COLOR


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

    @_shop.group(name="buy")
    @commands.guild_only()
    @commands.cooldown(1, 25, BucketType.user)
    async def _shop_buy(self, ctx):
        if ctx.invoked_subcommand is None:
            return await ctx.send(
                f'Укажите категорию магазина (`roles` или `things`)')

    # TODO: Нужно закончить, добавить проверку наличия предыдущей роли
    @_shop_buy.command(name="roles")
    @commands.guild_only()
    @commands.cooldown(1, 25, BucketType.user)
    async def _shop_buy_roles(self, ctx, itemId=None):
        if itemId is None:
            return await ctx.send(":x: Вы не указали номер товара!")

        try:
            itemId = int(itemId)
        except ValueError:
            return await ctx.send(":x: Номер товара должен быть целочисленным значением!")

        msg = await ctx.send(":repeat: Выполняю...")

        e = discord.Embed(colour=SECONDARY_COLOR)
        user = ctx.author
        guild = ctx.guild
        member = guild.get_member(user.id)

        roles = await get_roles_shop_list(guild.id)
        user_balance = await Postgres.find_xp(ctx.guild.id, ctx.author.id)

        for key, value in roles.items():
            price = value['PRICE']

            if int(user_balance) < int(price):
                e.colour = ERROR_COLOR
                e.description = ":x: Ошибка! У вас недостаточно средств."
                return await msg.edit(embed=e, content="")

            shop_id = value['SHOP_ID']

            if itemId == shop_id:
                role = guild.get_role(value['ROLE'])
                new_balance = int(user_balance) - int(price)
                try:
                    await member.add_roles(role, reason="Покупка роли из магазина.")
                    await Postgres.update_balance(guild.id, user.id, new_balance)
                except:
                    return await msg.edit(content=":x: Ошибочка вышла :(")

                e.description = f"Вы успешно купили {role.mention}"
                e.colour = role.colour

                return await msg.edit(embed=e, content="")


def setup(bot):
    bot.add_cog(Shop(bot))
