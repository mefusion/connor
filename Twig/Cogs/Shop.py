from Twig.TwigCore import *
import discord
from discord.ext import commands
from Twig.Utils.Sql.Functions.MainFunctionality import fetch_data, update_data
from Twig.Utils.ShopGen import get_roles_shop_list
from Twig.Utils.Logger import Log


class Shop(commands.Cog, name='Магазин'):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='shop', brief='Магазинчик всякого')
    @commands.guild_only()
    async def _shop(self, ctx):
        if ctx.invoked_subcommand is None:
            return await ctx.send(
                f'Укажите категорию магазина (`{BOT_PREFIX}shop roles` или `{BOT_PREFIX}shop things`)')

    @_shop.command(name='roles', brief='Магазин ролей')
    @commands.guild_only()
    # @commands.cooldown(1, 15, BucketType.user)
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

    @_shop.command(name="things")
    @commands.guild_only()
    # @commands.cooldown(1, 15, BucketType.user)
    async def _shop_things(self, ctx):
        return await ctx.send('На данный момент в этом отделе пусто.')

    @_shop.group(name="buy")
    @commands.guild_only()
    # @commands.cooldown(1, 25, BucketType.user)
    async def _shop_buy(self, ctx):
        if ctx.invoked_subcommand is None:
            return await ctx.send(
                f'Укажите категорию магазина (`{BOT_PREFIX}shop roles` или `{BOT_PREFIX}shop things`)')

    @_shop_buy.command(name="roles")
    @commands.guild_only()
    # @commands.cooldown(1, 25, BucketType.user)
    async def _shop_buy_roles(self, ctx, itemId=None):
        # Проверяем, если пользователь не указал код товара
        if itemId is None:
            return await ctx.send(f'Вы не указали код товара!')

        message = await ctx.send(
            embed=discord.Embed(description=':repeat: Обработка запроса...', colour=SECONDARY_COLOR))

        # Проверяем, было ли указано число или что-то другое
        try:
            itemId = int(itemId)
        except ValueError:
            return await message.edit(embed=discord.Embed(description=':x: Код товара должен быть целым числом!',
                                                          colour=ERROR_COLOR))
        # Первый этап проверок пройден, второй
        author = ctx.author
        guild = ctx.guild
        balance = await fetch_data('xp', 'user', author.id)

        # Проверяем, есть ли пользователь в базе данных
        if balance is None:
            return await message.edit(embed=discord.Embed(description=":x: Вас нет в базе данных!",
                                                          colour=ERROR_COLOR))

        # Получаем конфигурацию наград
        priceList = get_roles_shop_list(guild.id)

        # Проверяем наличие конфигурации
        if priceList is None:
            return await message.edit(embed=discord.Embed(description=':x: Файл-конфигурации с ценами не найден.',
                                                          colour=ERROR_COLOR))

        # Проверяем, существует ли указанный код товара
        if itemId > len(priceList) or itemId < 1:
            return await message.edit(embed=discord.Embed(description=':x: Неизвестный код товара.', colour=ERROR_COLOR))

        # Основной цикл
        # reward - номер награды по порядку,
        # rewardParams - параметры этой награды
        for reward, rewardParams in priceList.items():
            rewardItemId = int(rewardParams['SHOP_ID'])
            rewardRole = discord.utils.get(ctx.guild.roles, id=rewardParams['ROLE'])
            rewardPrice = int(rewardParams['PRICE'])

            # Если найденный элемент соотв. тому ID, который указал пользователь
            if itemId == rewardItemId:
                # Получаем предыдущую роль-награду, с помощью цикла
                for prevReward, prevRewardParams in priceList.items():
                    prevRewardItemId = int(prevRewardParams['SHOP_ID'])

                    # Проверяем, если это первая покупка
                    if itemId == 1 or itemId < 1:
                        pass
                    # Основная проверка наличия предыдущей награды
                    elif prevRewardItemId == (rewardItemId - 1):
                        prevRewardRole = discord.utils.get(ctx.guild.roles, id=prevRewardParams['ROLE'])

                        # Сама проверка наличия предыдущей роли-награды
                        if prevRewardRole not in author.roles:
                            return await message.edit(embed=discord.Embed(
                                description=f':x: Для покупки {rewardRole.mention}, необходимо иметь {prevRewardRole.mention}',
                                colour=ERROR_COLOR
                            ))

                # Проверяем, достаточно ли пользователю опыта для покупки данной роли
                if balance < rewardPrice:
                    return await message.edit(embed=discord.Embed(
                        description=f':x: Вам не хватает **{rewardPrice - balance} опыта**.', colour=ERROR_COLOR))

                # Проверяем, если у пользователя уже есть данная роль-награда
                elif rewardRole in author.roles:
                    return await message.edit(
                        embed=discord.Embed(description=':warning: У вас уже есть эта роль!', colour=WARNING_COLOR))

                # Списываем сумму с баланса
                updatedBalance = int(balance - rewardPrice)
                await update_data('xp', updatedBalance, 'user', author.id)
                # Добавляем роль
                await author.add_roles(rewardRole)

                # Логируем
                LogData = f':shopping_cart: **Покупка ролей**\n\n'
                LogData += f'**Покупатель:** {author} (`{author.id}`)\n'
                LogData += f'**Покупка:** {rewardRole.mention} (`{rewardRole.id}`)\n'
                LogData += f'**Стоимость:** {rewardPrice} опыта'
                await Log(log_data=LogData, log_type='success').send(self.bot, XP_LOGS_CHANNEL)

                # Информируем
                return await message.edit(embed=discord.Embed(
                    title='Наслаждайтесь!',
                    description=f"Вы успешно купили {rewardRole.mention}!",
                    colour=rewardRole.color))


def setup(bot):
    bot.add_cog(Shop(bot))
