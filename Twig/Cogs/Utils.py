import discord
from discord.ext import commands
from Twig.TwigCore import *


class Utils(commands.Cog, name='Разное'):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Utils(bot))
