import discord
from discord.ext import commands
from Saber.SaberCore import *


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
                "1. Математика \n"
                "2. Математика \n"
                "3. Обществознание \n"
                "4. Обществознание \n"
                "5. null \n"
                "6. Химия \n"
                "```"
            )

        elif day.lower() in ('tuesday', 'вторник', 'вт'):
            return await msg.edit(
                content=
                "\N{HAMMER AND WRENCH} **Вторник** "
                "```\n"
                "1. Русский \n"
                "2. Русский \n"
                "3. Физика \n"
                "4. Физика \n"
                "5. Английский \n"
                "6. Английский \n"
                "```"
            )

        elif day.lower() in ('wednesday', 'среда', 'ср'):
            return await msg.edit(
                content=
                "\N{HAMMER AND WRENCH} **Среда** "
                "```\n"
                "1. Математика \n"
                "2. Математика \n"
                "3. География \n"
                "4. География \n"
                "```"
            )

        elif day.lower() in ('thursday', 'четверг', 'чт'):
            return await msg.edit(
                content=
                "\N{HAMMER AND WRENCH} **Четверг**"
                "```\n"
                "1. Математика \n"
                "2. Математика \n"
                "3. Литература \n"
                "4. Литература \n"
                "5. История \n"
                "6. История \n"
                "```"
            )

        elif day.lower() in ('friday', 'пятница', 'пт'):
            return await msg.edit(
                content=
                "\N{HAMMER AND WRENCH} **Пятница"
                "```\n"
                "1. Биология \n"
                "2. Физика \n"
                "3. Английский \n"
                "4. Информатика \n"
                "5. Информатика \n"
                "```"
            )

        elif day.lower() in ('saturday', 'суббота', 'сб'):
            return await msg.edit(
                content=
                "\N{HAMMER AND WRENCH} **Суббота** "
                "```\n"
                "1. ОРР \n"
                "2. ОРР \n"
                "3. Литература \n"
                "4. Физ-ра \n"
                "```"
            )

        else:
            return await msg.edit(content="каво")


def setup(bot):
    bot.add_cog(TwigExclusives(bot))
