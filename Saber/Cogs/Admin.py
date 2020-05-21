import discord
from discord.ext import commands
from Saber.SaberCore import *
from ..Utils.Configurator import show_config


class Admin(commands.Cog, name='Админские'):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await ctx.bot.is_owner(ctx.author) or ctx.author.id in BOT_MAINTAINERS

def setup(bot):
    bot.add_cog(Admin(bot))
