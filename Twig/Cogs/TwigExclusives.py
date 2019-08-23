import discord
from discord.ext import commands
from Twig.TwigCore import *


class TwigExclusives(commands.Cog, name='Специальные'):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(TwigExclusives(bot))
