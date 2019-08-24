from Twig.TwigCore import *
import discord
from discord.ext import commands
from Twig.Utils.Sql.Functions.MainFunctionality import fetch_data
from Twig.Utils.ShopGen import get_roles_shop_list


class Shop(commands.Cog, name='Магазин'):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='shop', brief='Магазинчик всякого')
    async def _shop(self, ctx):
        if ctx.invoked_subcommand is None:
            return await ctx.send(f'Укажите категорию магазина (`{BOT_PREFIX}shop roles` или `{BOT_PREFIX}shop things`)')

    @_shop.command(name='roles', brief='Магазин ролей')
    async def _shop_roles(self, ctx):
        # Получаем список ролей в магазине ролей
        ShopObj = get_roles_shop_list(ctx.guild.id)

        # Если файл не найден
        if ShopObj is None:
            return await ctx.send(':warning: Файл конфигурации магазина ролей для этого сервера не найден.')

        # Подготавливаем эмбед сообщение
        embed = discord.Embed(title=':shopping_cart: Магазин ролей', colour=SECONDARY_COLOR)
        embed.set_footer(text='Все покупки логируются! Если что-то пойдёт не так, сообщите администратору!')
        embed.description = ""

        # Проходимся по всем элемента наград-ролей
        for roleReward, rewardParams in ShopObj.items():
            # Получаем ID товараша
            itemId = rewardParams['SHOP_ID']
            # Получаем ID роли-товара
            roleId = rewardParams['ROLE']
            # Получаем стоимость
            itemPrice = rewardParams['PRICE']
            # Получаем роль, и удаляем ID роли
            role = discord.utils.get(ctx.guild.roles, id=roleId)
            del roleId
            # Добавляем данные в вывод
            embed.description += f"**Роль:** {role.mention}\n **Цена:** {itemPrice} очков опыта\n**Купить:** `{BOT_PREFIX}shop buy roles {itemId}` \n\n"

        # Выводим
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Shop(bot))
