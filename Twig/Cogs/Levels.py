import discord
from discord.ext import commands
from Twig.TwigCore import *


class Levels(commands.Cog, name='Уровни'):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Levels(bot))
