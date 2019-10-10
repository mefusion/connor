import discord
from Saber.Utils.Sql.DBUtils import Exp
from discord.ext import commands
from discord.ext.commands import BucketType
from Saber.SaberCore import BOT_PREFIX
from Saber.Utils.ShopGen import *
from Saber.SaberCore import SECONDARY_COLOR, ERROR_COLOR
from Saber.Utils.Configurator import what_prefix, get_shop_log_channel
from Saber.Utils.Logger import Log


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
        guild = ctx.guild
        roles = await get_roles_shop_list(ctx.guild.id)
        e = discord.Embed(color=SECONDARY_COLOR).set_footer(
            text=f"Чтобы купить роль, используйте команду {await what_prefix(guild.id)}shop buy roles <номер_товара>")

        for key, value in roles.items():
            shop_id = value['SHOP_ID']
            role = guild.get_role(value['ROLE'])
            price = value['PRICE']

            e.add_field(name=f"Товар #{shop_id}", value=f"Роль: {role.mention}\nЦена: {price}", inline=False)

        del guild, roles
        return await ctx.send(embed=e)

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
        guild = ctx.guild
        member = guild.get_member(ctx.author.id)

        roles = await get_roles_shop_list(guild.id)

        if itemId > len(roles) or itemId < 1:
            return await msg.edit(
                embed=discord.Embed(description=':x: Неизвестный код товара.', colour=ERROR_COLOR), content="")

        for key, value in roles.items():
            price = value['PRICE']
            shop_id = value['SHOP_ID']

            if itemId == shop_id:
                user_balance = await Exp.find_xp(guild.id, member.id)

                if user_balance is None:
                    return await msg.edit(content=":x: Вас нет в базе данных опыта! У вас просто нет баланса!")

                if int(user_balance) < int(price):
                    e.colour = ERROR_COLOR
                    e.description = ":x: Ошибка! У вас недостаточно средств."
                    return await msg.edit(embed=e, content="")

                role = guild.get_role(value['ROLE'])

                if role in member.roles:
                    e.colour = ERROR_COLOR
                    e.description = ":x: У вас уже есть эта роль!"
                    return await msg.edit(embed=e, content="")

                for prev_key, prev_value in roles.items():
                    prevRewardItemId = int(prev_value['SHOP_ID'])

                    if itemId == 1 or itemId < 1:
                        pass

                    elif prevRewardItemId == (shop_id - 1):
                        prev_role = guild.get_role(prev_value['ROLE'])

                        if prev_role not in member.roles:
                            e.description = f"Чтобы купить {role.mention}, необходимо иметь {prev_role.mention}"
                            e.colour = role.colour
                            return await msg.edit(content="", embed=e)

                new_balance = int(user_balance) - int(price)

                try:
                    await member.add_roles(role, reason="Покупка роли из магазина.")
                    await Exp.update_balance(guild.id, member.id, new_balance)
                except:
                    return await msg.edit(content=":x: Ошибочка вышла :(")

                await msg.edit(embed=discord.Embed(colour=role.colour, description=f"Вы успешно купили {role.mention}"),
                               content="")

                # Логируем
                log = Log(guild.id)
                log_text = await log.generate_log_data(
                    'xp',
                    f"**{member}** (`{member.id}`) купил роль {role.mention} (`{role.id}`), потратив `{price}` единиц опыта."
                )
                await log.log_to(await get_shop_log_channel(guild.id), log_text)
                del log, roles, guild, member


def setup(bot):
    bot.add_cog(Shop(bot))
