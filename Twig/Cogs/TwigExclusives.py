import discord
from discord.ext import commands
from Twig.TwigCore import *


class TwigExclusives(commands.Cog, name='Специальные'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="schedule", aliases=('расписание',))
    @commands.is_owner()
    async def _schedule(self, ctx, day):
        """Расписание создателя бота лол"""
        msg = await ctx.send("Открываю дневник...")

        if day.lower() in ('monday', 'понедельник', 'пн'):
            return await msg.edit(
                content=
                "\N{HAMMER AND WRENCH} **Понедельник** "
                "```\n"
                "1. null \n"
                "2. Репетитор: обществознание \n"
                "3. Алгебра \n"
                "4. Алгебра \n"
                "5. Обществознание \n"
                "6. Обществознание \n"
                "7. Репетитор: обществознание \n"
                "```"
            )

        elif day.lower() in ('tuesday', 'вторник', 'вт'):
            return await msg.edit(
                content=
                "\N{HAMMER AND WRENCH} **Вторник** "
                "```\n"
                "1. Русский \n"
                "2. Русский \n"
                "3. Информатика \n"
                "4. География \n"
                "5. Астрономия \n"
                "6. Английский \n"
                "7. Английский \n"
                "```"
            )

        elif day.lower() in ('wednesday', 'среда', 'ср'):
            return await msg.edit(
                content=
                "\N{HAMMER AND WRENCH} **Среда** "
                "```\n"
                "1. Обществознание \n"
                "2. Право \n"
                "3. Геометрия \n"
                "4. Геометрия \n"
                "5. ОПД \n"
                "6. Физика \n"
                "7. Физика \n"
                "8. ЭК по обществу \n"
                "```"
            )

        elif day.lower() in ('thursday', 'четверг', 'чт'):
            return await msg.edit(
                content=
                "\N{HAMMER AND WRENCH} **Четверг**"
                "```\n"
                "1. Репетитор: русский \n"
                "2. Репетитор: русский \n"
                "3. Биология \n"
                "4. Биология \n"
                "5. ОБЖ \n"
                "6. Репетитор: информатика \n"
                "```"
            )

        elif day.lower() in ('friday', 'пятница', 'пт'):
            return await msg.edit(
                content=
                "\N{HAMMER AND WRENCH} **Пятница"
                "```\n"
                "1. Алгебра \n"
                "2. Алгебра \n"
                "3. ЭК по русскому \n"
                "4. Химия \n"
                "5. Химия \n"
                "6. null \n"
                "7. Английский \n"
                "```"
            )

        elif day.lower() in ('saturday', 'суббота', 'сб'):
            return await msg.edit(
                content=
                "\N{HAMMER AND WRENCH} **Суббота** "
                "```\n"
                "1. null \n"
                "2. Экономика \n"
                "3. История \n"
                "4. История \n"
                "```"
            )

        else:
            return await msg.edit(content="каво")


def setup(bot):
    bot.add_cog(TwigExclusives(bot))
