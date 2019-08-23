import discord
from discord.ext import commands
from Twig.TwigCore import *

command_attrs = {'hidden': True}


class Events(commands.Cog, name='События', command_attrs=command_attrs):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        pass


def setup(bot):
    bot.add_cog(Events(bot))
