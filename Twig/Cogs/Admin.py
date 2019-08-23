import discord
from discord.ext import commands
from Twig.TwigCore import *


class Admin(commands.Cog, name='Админские'):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Admin(bot))
