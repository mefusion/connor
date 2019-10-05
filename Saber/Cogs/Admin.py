import discord
from discord.ext import commands
from Saber.SaberCore import *
from ..Utils.Configurator import show_config


class Admin(commands.Cog, name='Админские'):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await ctx.bot.is_owner(ctx.author) or ctx.author.id in BOT_MAINTAINERS

    # ==== ROLES MANAGEMENT COMMANDS ==== #

    @commands.command(name="guild-cfg")
    @commands.has_permissions(manage_guild=True)
    async def guild_cfg(self, ctx):
        current_conf = await show_config(ctx.guild.id)
        await ctx.send(f"Текущая конфигурация сервера: ```json\n{current_conf}\n```")
        del current_conf

    @commands.group(name="role-edit", aliases=("erole", "role_edit"))
    async def _erole(self, ctx):
        """Редактирование ролей"""
        if ctx.invoked_subcommand is None:
            return await ctx.send('Вы не указали субкоманду.')

    @_erole.command(name="color", aliases=("colour",))
    async def _erole_color(self, ctx, role: commands.RoleConverter = None, color: commands.ColourConverter = None):
        """Редактирование цвета роли"""
        if role is None:
            return await ctx.send(":x: Вы не указали роль.")
        elif color is None:
            return await ctx.send(
                embed=discord.Embed(colour=role.colour,
                                    description=f"{role.mention}\n↳ Текущий цвет: `{str(role.colour)}`"))
        else:
            await role.edit(colour=color)

            r_color_embed = discord.Embed(
                colour=color, description=f"Вы успешно изменили цвет для роли **{role}**!",
                reason=f"Изменено пользователем {ctx.author.id}")
            r_color_embed.set_footer(
                text=f"{ctx.author.name}#{ctx.author.discriminator} ({ctx.author.id})",
                icon_url=ctx.author.avatar_url)

            await ctx.send(embed=r_color_embed)


def setup(bot):
    bot.add_cog(Admin(bot))
