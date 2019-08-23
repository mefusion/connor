from Twig.TwigCore import *
import discord
from discord.ext import commands
from Twig.Utils.Sql.Functions.MainFunctionality import fetch_data


class Shop(commands.Cog, name='Магазин'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='shop', brief='Магазинчик всякого')
    async def _shop(self, ctx):
        return await ctx.send(f'У меня обед, хватит ломиться.')


def setup(bot):
    bot.add_cog(Shop(bot))
