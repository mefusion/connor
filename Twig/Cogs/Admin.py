import discord
from discord.ext import commands
from Twig.TwigCore import *
from Twig.Utils.Logger import Log
from Twig.Utils.Sql.Functions.MainFunctionality import fetch_data, update_data, add_user, del_user, fetch_table


class Admin(commands.Cog, name='Админские'):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await ctx.bot.is_owner(ctx.author) or ctx.author.id in BOT_MAINTAINERS

    # ==== ROLES MANAGEMENT COMMANDS ==== #

    @commands.group(name="erole")
    async def _erole(self, ctx):
        if ctx.invoked_subcommand is None:
            return await ctx.send('Вы не указали субкоманду.')

    @_erole.command(name="color", aliases=("colour",))
    async def _erole_color(self, ctx, r: commands.RoleConverter = None, c: commands.ColourConverter = None):
        if r is None:
            return await ctx.send(":x: Вы не указали роль.")
        elif c is None:
            return await ctx.send(embed=discord.Embed(colour=r.colour, description=f"{r.mention}\n↳ Текущий цвет: `{str(r.colour)}`"))
        else:
            await r.edit(colour=c)

            r_color_embed = discord.Embed(
                colour=c, description=f"Вы успешно изменили цвет для роли **{r}**!",
                reason=f"Изменено пользователем {ctx.author.id}")
            r_color_embed.set_footer(
                text=f"{ctx.author.name}#{ctx.author.discriminator} ({ctx.author.id})",
                icon_url=ctx.author.avatar_url)

            await ctx.send(embed=r_color_embed)

    # ==== XP MANAGEMENT COMMANDS ==== #

    @commands.group(name='managexp', aliases=('mxp', 'axp'))
    async def _managexp(self, ctx):
        if ctx.invoked_subcommand is None:
            return await ctx.send('Вы не указали субкоманду.')

    @_managexp.command(name='fetch_users')
    async def _managexp_fetch_users(self, ctx):
        message = await ctx.send(':repeat: Пожалуйста ожидайте.')

        # Полуаем список пользователей
        data = await fetch_table()
        resulting_txt = "Список пользователей в БД: ```yaml\n"

        # Рассчитываем примерное время ожидание
        approx_waiting = len(data) * 2
        approx_waiting = round((approx_waiting / 60), 2)

        await message.edit(content=f':hourglass: Примерное время ожидания: **{approx_waiting}** минут...')

        # На случай, если реально много пользователей в БД
        if len(data) >= 35:
            resulting_txt = f"Список пользователей слишком длинный. \nВсего строк в таблице: **{len(data)}**"
            return await message.edit(content=resulting_txt)

        # Основной цикл
        for i in range(0, len(data)):
            # Получаем объект пользователя
            user = await self.bot.fetch_user(int(data[i]))
            # Ждём 2 секунды, дабы избежать дождь из ошибок 429
            await asyncio.sleep(2)
            # Добавляем полученные данные в сообщение
            resulting_txt = resulting_txt + str(user) + ' (' + str(user.id) + ')' + "\n"

        resulting_txt = f'Всего записей: **{len(data)}**\n' + resulting_txt + '```'

        # Если слишком много символов
        if len(resulting_txt) >= 1800:
            resulting_txt = f"Список пользователей слишком длинный. \nВсего строк в таблице: **{len(data)}**"
            return await message.edit(content=resulting_txt)

        await asyncio.sleep(0.01)
        return await message.edit(content=resulting_txt)

    @_managexp.command(name='add', aliases=('give',))
    async def _managexp_add(self, ctx, user: discord.User, adding_to_xp):
        message = await ctx.send(':repeat: Выполняю...')

        # Проверка, если указан сам бот
        if user is self.bot.user:
            return await message.edit(content="Нет.")

        # Проверка, если указан любой другой бот
        elif user.bot is True:
            return await message.edit(content='Нет. Машинам нельзя сюда.')

        # Получаем текущий баланс пользователя, None - если нет в БД
        current_xp = await fetch_data('xp', 'user', user.id)

        # Отмена операции, если указаноого пользователя нет в БД
        if current_xp is None:
            return await message.edit(content=f':x: Этого пользователя нет в базе данных, изменить баланс невозможно.')

        # Превращаем аргумент в целочисленную переменную
        adding_to_xp = int(adding_to_xp)

        # Проверяем, если аргумент добавляемого кол-ва опыта ниже или равно нулю
        if adding_to_xp <= 0:
            return await message.edit(content=f':warning: Вы пытаетесь добавить или удалить?!')

        # Прибавляем указнное количество опыта из команды к текущему балансу пользователя и сохраняем в переменной
        setting_to = current_xp + adding_to_xp
        del adding_to_xp, current_xp

        # Отменяем процесс, если указано больше 350 тыс. опыта
        if setting_to > 350000:
            return await message.edit(content=f':x: Вы пытаетесь добавить слишком много опыта, ' +
                                              'баланс пользователя не должен превышать 350 тыс. опыта.')

        # Применяем изменения, если все проверки пройдены успешно
        await update_data('xp', setting_to, 'user', user.id)

        # Логируем
        Log_Data = f':gear: **Админское изменение баланса**\n\n'
        Log_Data += f'Администратор **{ctx.author}** (`{ctx.author.id}`) изменил баланс ' \
                    f'пользователя **{user}** (`{user.id}`) на **{setting_to} опыта**.'

        await Log(log_data=Log_Data).send(self.bot, XP_LOGS_CHANNEL)

        # Сообщаем об изменениях
        return await message.edit(
            content=f':ok_hand: Вы успешно изменили баланс пользователю {str(user)} (`{user.id}`)')

    @_managexp.command(name='set')
    async def _managexp_set(self, ctx, user: discord.User, set_xp_to):
        message = await ctx.send(':repeat: Выполняю...')

        # Проверка, если указан сам бот
        if user is self.bot.user:
            return await message.edit(content="Нет.")

        # Проверка, если указан любой другой бот
        elif user.bot is True:
            return await message.edit(content='Нет. Машинам нельзя сюда.')

        # Получаем текущий баланс пользователя, None - если нет в БД
        current_xp = await fetch_data('xp', 'user', user.id)

        # Отмена операции, если указаноого пользователя нет в БД
        if current_xp is None:
            return await message.edit(content=f':x: Этого пользователя нет в базе данных, изменить баланс невозможно.')

        # Превращаем значение аргумента в целочисленное значение
        set_xp_to = int(set_xp_to)

        # Отменяем, если указано отрицательное значение опыта
        if set_xp_to < 0:
            return await message.edit(content=f':warning: Невозможно установить отрицательный баланс.')

        # Отменяем, если больше 350 тыс. опыта
        if set_xp_to > 350000:
            return await message.edit(content=f':x: Вы пытаетесь дать больше 350 тыс. очков опыта, так нельзя.')

        # Применяем изменения, если проверки пройдены успешно
        await update_data('xp', set_xp_to, 'user', user.id)

        # Логируем
        Log_Data = f':gear: **Админское изменение баланса**\n\n'
        Log_Data += f'Администратор **{ctx.author}** (`{ctx.author.id}`) изменил баланс ' \
                    f'пользователя **{user}** (`{user.id}`) на **{set_xp_to} опыта**.'

        await Log(log_data=Log_Data).send(self.bot, XP_LOGS_CHANNEL)

        # Сообщаем об изменениях
        return await message.edit(
            content=f':ok_hand: Вы успешно изменили баланс пользователю {str(user)} (`{user.id}`)')

    @_managexp.command(name='reset')
    async def _managexp_reset(self, ctx, user: discord.User):
        message = await ctx.send(':repeat: Выполняю...')

        # Проверка, если указан сам бот
        if user is self.bot.user:
            return await message.edit(content="Нет.")

        # Проверка, если указан любой другой бот
        elif user.bot is True:
            return await message.edit(content='Нет. Машинам нельзя сюда.')

        # Получаем текущий баланс пользователя, None - если нет в БД
        current_xp = await fetch_data('xp', 'user', user.id)

        # Отмена операции, если указаноого пользователя нет в БД
        if current_xp is None:
            return await message.edit(content=f':x: Этого пользователя нет в базе данных, изменить баланс невозможно.')

        # Рофлан-провека
        if int(current_xp) <= 1:
            return await message.edit(
                content=f':thinking: Вы и правда хотите сбросить баланс человеку, у которого на счету нет очков опыта? ')

        # Превращаем значение аргумента в целочисленное значение
        set_xp_to = 0

        # Применяем изменения, если проверки пройдены успешно
        await update_data('xp', set_xp_to, 'user', user.id)

        # Логируем
        Log_Data = f':gear: **Админское изменение баланса**\n\n'
        Log_Data += f'Администратор **{ctx.author}** (`{ctx.author.id}`) сбросил баланс ' \
                    f'пользователя **{user}** (`{user.id}`) на **{set_xp_to} опыта**.'

        await Log(log_data=Log_Data, log_type='warning').send(self.bot, XP_LOGS_CHANNEL)

        # Сообщаем об изменениях
        return await message.edit(
            content=f':ok_hand: Вы успешно сбросили баланс пользователю {str(user)} (`{user.id}`)')

    # ==== XP MANAGEMENT COMMANDS (BOT OWNER ONLY) ==== #

    @_managexp.command(name='add_user', aliases=('force_add_user',))
    @commands.is_owner()
    async def _managexp_add_user(self, ctx, user: discord.User = None):
        message = await ctx.send(':repeat: Выполняю...')

        # Проверяем, если пользователь вообще был указан
        if user is None:
            return await message.edit(content='Вы не указали пользователя.')

        # Проверка, если указан сам бот
        if user is self.bot.user:
            return await message.edit(content="Нет.")

        # Проверка, если указан любой другой бот
        elif user.bot is True:
            return await message.edit(content='Нет. Машинам нельзя сюда.')

        # Получаем текущий баланс пользователя, None - если нет в БД
        user_object = await fetch_data('user', 'user', user.id)

        # Отмена операции, если указанный пользователь есть в БД
        if user_object is not None:
            return await message.edit(content=f':x: Этот пользователь уже присутствует в базе данных.')

        # Добавляем пользователя в базу
        await add_user(user.id)

        # Логируем
        Log_Data = ':rotating_light: **Админское добавление пользователей**\n\n'
        Log_Data += f'Администратор **{ctx.author}** (`{ctx.author.id}`) принудительно добавляет пользователя '
        Log_Data += f'**{user}** (`{user.id}`) в базу данных.'

        await Log(log_data=Log_Data, log_type='warning').send(self.bot, XP_LOGS_CHANNEL)

        return await message.edit(
            content=f':ok_hand: Вы успешно внесли пользователя **{user}** (`{user.id}`) в базу данных.')

    @_managexp.command(name='del_user')
    @commands.is_owner()
    async def _managexp_del_user(self, ctx, user: discord.User = None):
        message = await ctx.send(':repeat: Выполняю...')

        # Проверяем, если пользователь вообще был указан
        if user is None:
            return await message.edit(content='Вы не указали пользователя.')

        # Проверка, если указан сам бот
        if user is self.bot.user:
            return await message.edit(content="Нет.")

        # Проверка, если указан любой другой бот
        elif user.bot is True:
            return await message.edit(content='Нет. Машинам нельзя сюда.')

        # Получаем текущий баланс пользователя, None - если нет в БД
        user_object = await fetch_data('user', 'user', user.id)

        # Отмена операции, если указанный пользователь есть в БД
        if user_object is None:
            return await message.edit(content=f':x: Этого пользовател и так нет в базе данных.')

        # Удаляем пользователя из базы данных
        await del_user(user.id)

        # Логируем
        Log_Data = ':wastebasket: **Админское удаление пользователей**\n\n'
        Log_Data += f'Администратор **{ctx.author}** (`{ctx.author.id}`) удаляет пользователя '
        Log_Data += f'**{user}** (`{user.id}`) из базы данных.'

        await Log(log_data=Log_Data, log_type='warning').send(self.bot, XP_LOGS_CHANNEL)

        return await message.edit(
            content=f':wastebasket: Вы успешно удалили пользователя **{user}** (`{user.id}`) из базы данных.')

    @_managexp.command(name='force_del_user')
    @commands.is_owner()
    async def _managexp_force_del_user(self, ctx, user=None):
        message = await ctx.send(':repeat: Выполняю...')

        # Проверяем, если пользователь вообще был указан
        if user is None:
            return await message.edit(content='Вы не указали ID пользователя.')

        # Получаем текущий баланс пользователя, None - если нет в БД
        user_object = await fetch_data('user', 'user', user)

        # Отмена операции, если указанный пользователь есть в БД
        if user_object is None:
            return await message.edit(content=f':x: Этого пользовател и так нет в базе данных.')

        # Удаляем пользователя из базы данных
        await del_user(user)

        # Логируем
        Log_Data = ':wastebasket: **Админское удаление пользователей**\n\n'
        Log_Data += f'Администратор **{ctx.author}** (`{ctx.author.id}`) принудительно удаляет '
        Log_Data += f'пользователя **{user}** из базы данных.'

        await Log(log_data=Log_Data, log_type='warning').send(self.bot, XP_LOGS_CHANNEL)

        return await message.edit(
            content=f':wastebasket: Вы успешно удалили пользователя **{user}** из базы данных.')


def setup(bot):
    bot.add_cog(Admin(bot))
