import discord
from discord.ext import commands
from ..Utils.Converters import DiscordUser
from ..Utils.Logger import ModLog
from ..Utils.Configurator import get_mod_log_channel
from ..Utils.Sql.DBUtils import Infractions


class InfractionsManager(commands.Cog, name='Инфракции'):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="inf", aliases=("infraction",))
    async def inf(self, ctx):
        if ctx.invoked_subcommand is None:
            return await ctx.send('Вы не указали субкоманду.')

    # TODO: Читабельный вывод данных
    @inf.command(name="search")
    @commands.has_permissions(manage_messages=True, read_message_history=True)
    async def inf_search(self, ctx, user: DiscordUser):
        user = await self.bot.fetch_user(user.id)
        data = await Infractions.search(ctx.guild.id, user.id)

        await ctx.send(f"{str(data)}")

    @inf.command(name="info")
    @commands.has_permissions(manage_messages=True, read_message_history=True)
    async def inf_info(self, ctx, inf_id):
        try:
            int(inf_id)
        except ValueError:
            return await ctx.send(f"ID инфракции должен быть целочисленным значением")

        infraction = await Infractions.get(inf_id)

        if infraction is None:
            return await ctx.send(f":x: Инфракция `#{inf_id}` не найдена!")

        if infraction["guild_id"] != ctx.guild.id:
            return await ctx.send(":x: Вам нельзя просматривать данные инфракций с других серверов.")

        punished = await self.bot.fetch_user(infraction['user_id'])
        moderator = await self.bot.fetch_user(infraction['moderator_id'])

        e = discord.Embed(title=f"Инфракция #{infraction['inf_id']}")

        e.add_field(name="Наказанный", value=f"{punished} (`{punished.id}`)")
        e.add_field(name="Тип инфракции", value=f"{infraction['inf_type']}")
        e.add_field(name="Кем выдана", value=f"{moderator} (`{moderator.id}`)")
        e.add_field(name="Когда выдана", value=f"{infraction['given_at']}")
        e.set_thumbnail(url=punished.avatar_url)

        return await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(InfractionsManager(bot))
