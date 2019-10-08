import discord
from discord.ext import commands
from Saber.Utils.Logger import Log
import Saber.Utils.Sql.Functions.PostgresFunctions as Postgres
from ..Utils.Configurator import *


class XPManagement(commands.Cog, name="Управление XP"):
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        self.sessions = set()
        self.thisWords = ("this", "current", "here", "same", "здесь", "тут")

    async def cog_check(self, ctx):
        return await ctx.bot.is_owner(ctx.author)

    # ==== XP MANAGEMENT COMMANDS ==== #

    @commands.group(name='managexp', aliases=('mxp', 'axp'))
    async def _managexp(self, ctx):
        if ctx.invoked_subcommand is None:
            return await ctx.send('Вы не указали субкоманду.')

    @_managexp.command(name='add', aliases=('give',))
    async def postgres_setxp(self, ctx, guild_id, user: discord.User, adding_to_xp: int):
        message = await ctx.send(':repeat: Выполняю...')
        if guild_id in self.thisWords:
            guild_id = ctx.guild.id
        elif guild_id is None:
            return await message.edit(content="Параметр `guild` является обязательным.")
        elif user is None:
            return await message.edit(content="Параметр `user` является обязательным.")
        elif adding_to_xp is None:
            return await message.edit(content="Параметр `adding_to_xp` является обязательным.")

        # Проверка, если указан сам бот
        if user is self.bot.user:
            return await message.edit(content="Нет.")

        # Проверка, если указан любой другой бот
        elif user.bot is True:
            return await message.edit(content='Нет. Машинам нельзя сюда.')

        # Получаем текущий баланс юзера
        balance = await Postgres.find_xp(guild_id, user.id)

        if balance is None:
            return await message.edit(content=f':x: Этого пользователя нет в базе данных, изменить баланс невозможно.')

        updated_balance = int(balance) + int(adding_to_xp)

        if updated_balance > 350000:
            return await message.edit(content=f':x: Вы пытаетесь добавить слишком много опыта, ' +
                                              'баланс пользователя не должен превышать 350 тыс. опыта.')

        await Postgres.update_balance(guild_id, user.id, updated_balance)

        guildObj = self.bot.get_guild(guild_id)

        new_balance = await Postgres.find_xp(ctx.guild.id, user.id)
        await message.edit(
            content=f"\N{OK HAND SIGN} Баланс **{user}** успешно установлен на `{new_balance}` единиц опыта.")

        # Логируем
        log = Log(guildObj.id)
        log_text = await log.generate_log_data(
            _type='admin',
            text=f"**{ctx.author}** (`{ctx.author.id}`) установил баланс юзеру **{user}** (`{user.id}`) на `{new_balance}` единиц опыта."
        )
        await log.log_to((await get_xp_log_channel(guildObj.id)), log_text)

    @_managexp.command(name='set')
    async def _managexp_set(self, ctx, guild_id=None, user: discord.User = None, set_xp_to=None):
        message = await ctx.send(':repeat: Выполняю...')
        if guild_id in self.thisWords:
            guild_id = ctx.guild.id
        elif guild_id is None:
            return await message.edit(content="Параметр `guild` является обязательным.")
        elif user is None:
            return await message.edit(content="Параметр `user` является обязательным.")
        elif set_xp_to is None:
            return await message.edit(content="Параметр `set_xp_to` является обязательным.")

        # Проверка, если указан сам бот
        if user is self.bot.user:
            return await message.edit(content="Нет.")

        # Проверка, если указан любой другой бот
        elif user.bot is True:
            return await message.edit(content='Нет. Машинам нельзя сюда.')

        # Получаем текущий баланс юзера
        balance = await Postgres.find_xp(guild_id, user.id)

        # Отмена операции, если указаноого пользователя нет в БД
        if balance is None:
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
        await Postgres.update_balance(guild_id, user.id, set_xp_to)
        guildObj = self.bot.get_guild(guild_id)
        new_balance = await Postgres.find_xp(ctx.guild.id, user.id)

        await message.edit(
            content=f'\N{OK HAND SIGN} Баланс **{str(user)}** успешно установлен на `{str(new_balance)}` единиц опыта.'
        )

        # Логируем
        log = Log(guildObj.id)
        log_text = await log.generate_log_data(
            _type='admin',
            text=f"**{ctx.author}** (`{ctx.author.id}`) установил баланс юзеру **{user}** (`{user.id}`) на `{new_balance}` единиц опыта."
        )

        await log.log_to((await get_xp_log_channel(guildObj.id)), log_text)

    @_managexp.command(name='reset')
    async def _managexp_reset(self, ctx, guild=None, user: discord.User = None, *, reason=None):
        message = await ctx.send(':repeat: Выполняю...')
        if guild in self.thisWords:
            guild = ctx.guild.id
        elif guild is None:
            return await message.edit(content="Параметр `guild` является обязательным.")
        elif user is None:
            return await message.edit(content="Параметр `user` является обязательным.")

        if reason is None:
            reason = "Причина не указана."

        # Проверка, если указан сам бот
        if user is self.bot.user:
            return await message.edit(content="Нет.")

        # Проверка, если указан любой другой бот
        elif user.bot is True:
            return await message.edit(content='Нет. Машинам нельзя сюда.')

        # Получаем текущий баланс пользователя, None - если нет в БД
        current_xp = await Postgres.find_xp(guild, user.id)

        # Отмена операции, если указаноого пользователя нет в БД
        if current_xp is None:
            return await message.edit(content=f':x: Этого пользователя нет в базе данных, изменить баланс невозможно.')

        # Рофлан-провека
        if int(current_xp) <= 1:
            return await message.edit(
                content=f':thinking: Вы и правда хотите сбросить баланс человеку, у которого на счету нет очков опыта?')

        # Превращаем значение аргумента в целочисленное значение
        set_xp_to = 0

        # Применяем изменения, если проверки пройдены успешно
        await Postgres.update_balance(guild, user.id, set_xp_to)
        guildObj = self.bot.get_guild(guild)
        new_balance = await Postgres.find_xp(ctx.guild.id, user.id)

        if new_balance >= 0:
            await message.edit(
                content=f':ok_hand: Баланс пользователя **{str(user)}** сброшен: `{reason}`'
            )
        else:
            await message.edit(
                content=f':x: Что-то пошло не так...'
            )

        # Логируем
        log = Log(guildObj.id)
        log_text = await log.generate_log_data(
            _type='admin',
            text=f"**{ctx.author}** (`{ctx.author.id}`) сбросил баланс юзеру **{user}** (`{user.id}`): `{reason}`"
        )

        await log.log_to((await get_xp_log_channel(guildObj.id)), log_text)

    @_managexp.command(name='add_user', aliases=('force_add_user',))
    @commands.is_owner()
    async def _managexp_add_user(self, ctx, guild=None, user: discord.User = None):
        message = await ctx.send(':repeat: Выполняю...')

        if guild in self.thisWords:
            guild = ctx.guild.id
        elif guild is None:
            return await message.edit(content="Параметр `guild` обязателен.")
        elif user is None:
            return await message.edit(content="Параметр `user` обязателен.")

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
        user_object = await Postgres.find_xp(guild, user.id)

        # Отмена операции, если указанный пользователь есть в БД
        if user_object is not None:
            return await message.edit(content=f':x: Этот пользователь уже существует в базе данных.')

        # Добавляем пользователя в базу
        await Postgres.insert_into_db(guild, user.id, 0)
        await message.edit(content=f"\N{OK HAND SIGN} **{user}** успешно внесён в базу данных сервера `{guild}`.")

        # Логируем
        guildObj = self.bot.get_guild(guild)

        log = Log(guildObj.id)
        log_text = await log.generate_log_data(
            _type='admin',
            text=f"**{ctx.author}** (`{ctx.author.id}`) внёс юзера **{user}** (`{user.id}`) в базу данных."
        )

        await log.log_to((await get_xp_log_channel(guildObj.id)), log_text)

    @_managexp.command(name='del_user')
    @commands.is_owner()
    async def _managexp_del_user(self, ctx, guild=None, user: discord.User = None):
        message = await ctx.send(':repeat: Выполняю...')

        if guild in self.thisWords:
            guild = ctx.guild.id
        elif guild is None:
            return await message.edit(content="Параметр `guild` обязателен.")
        elif user is None:
            return await message.edit(content="Параметр `user` обязателен.")

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
        user_object = await Postgres.find_xp(guild, user.id)

        # Отмена операции, если указанный пользователь есть в БД
        if user_object is None:
            return await message.edit(content=f':x: Этого пользовател и так нет в базе данных.')

        # Удаляем пользователя из базы данных
        await Postgres.delete_from_db(guild, user.id)

        # Логируем
        guildObj = self.bot.get_guild(guild)

        log = Log(guildObj.id)
        log_text = await log.generate_log_data(
            _type='admin',
            text=f"**{ctx.author}** (`{ctx.author.id}`) удалил юзера **{user}** (`{user.id}`) из базы данных."
        )

        await log.log_to((await get_xp_log_channel(guildObj.id)), log_text)
        await message.edit(content=f"\N{OK HAND SIGN} **{user}** успешно удалён из базы данных сервера `{guild}`.")

    @_managexp.command(name='force_del_user')
    @commands.is_owner()
    async def _managexp_force_del_user(self, ctx, guild_id: int = None, user_id: int = None):
        message = await ctx.send(':repeat: Выполняю...')

        if guild_id in self.thisWords:
            guild_id = ctx.guild.id
        elif guild_id is None:
            return await message.edit(content="Параметр `guild` обязателен.")
        elif guild_id is None:
            return await message.edit(content="Параметр `user` обязателен.")

        # Проверяем, если пользователь вообще был указан
        if user_id is None:
            return await message.edit(content='Вы не указали пользователя.')

        # Получаем текущий баланс пользователя, None - если нет в БД
        user_object = await Postgres.find_xp(guild_id, user_id)

        # Отмена операции, если указанный пользователь есть в БД
        if user_object is None:
            return await message.edit(content=f':x: Этого пользовател и так нет в базе данных.')

        # Удаляем пользователя из базы данных
        await Postgres.delete_from_db(guild_id, user_id)

        # Логируем
        guildObj = self.bot.get_guild(guild_id)

        log = Log(guildObj.id)
        log_text = await log.generate_log_data(
            _type='admin',
            text=f"**{ctx.author}** (`{ctx.author.id}`) удалил юзера **{user_id}** из базы данных."
        )

        await log.log_to((await get_xp_log_channel(guildObj.id)), log_text)
        await message.edit(
            content=f"\N{OK HAND SIGN} **{user_id}** успешно удалён из базы данных сервера `{guild_id}`.")

    @_managexp_force_del_user.error
    async def _managexp_force_del_user_handler(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            return await ctx.send(
                ":x: Ошибка! При использовании этой команды вы должны указывать только целочисленные аргументы.")


def setup(bot):
    bot.add_cog(XPManagement(bot))
