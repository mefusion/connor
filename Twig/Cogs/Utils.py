import discord
from discord.ext import commands
from Twig.TwigCore import *


class Utils(commands.Cog, name='Разное'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='userinfo', aliases=['info'])
    @commands.cooldown(1, 10, type=BucketType.user)
    async def _userinfo(self, ctx, user: discord.User = None):
        if user is None:
            user = member = ctx.author
            user = await self.bot.fetch_user(user.id)
        else:
            member = None if ctx.guild is None else ctx.guild.get_member(user.id)

        embed = discord.Embed()

        if user.bot is True:
            bot_or_not = 'Да'
        else:
            bot_or_not = 'Нет'

        if user.id in BOT_MAINTAINERS:
            embed.description = ':heart: Этот пользователь поддерживает моё существование!'

        embed.colour = DEFAULT_COLOR
        embed.set_thumbnail(url=user.avatar_url)
        embed.add_field(name='Имя пользователя', value=f'{user.name}#{user.discriminator}')
        embed.add_field(name='Идентификатор', value=str(user.id))
        embed.add_field(name='Бот?', value=bot_or_not)
        embed.add_field(name='Ссылка на аватар', value=f'[Перейти по ссылке]({user.avatar_url})')

        if member is not None:
            embed.colour = member.top_role.colour

            member_status = str(member.status)

            if member_status == 'online':
                member_status = 'В сети'
            elif member_status == 'dnd':
                member_status = 'Не беспокоить'
            elif member_status == 'idle':
                member_status = 'Нет на месте'
            elif member_status == 'offline':
                member_status = 'Не в сети'

            embed.add_field(name='Статус', value=member_status)

            if member.activity is not None:
                if member.activity.type == discord.ActivityType.playing:
                    embed.add_field(name='Активность', value=f'Играет в {member.activity.name}')
                elif member.activity.type == discord.ActivityType.streaming:
                    embed.add_field(name='Активность', value=f'Стримит {member.activity.name}')
                elif member.activity.type == discord.ActivityType.watching:
                    embed.add_field(name='Активность', value=f'Смотрит {member.activity.name}')
                elif member.activity.type == discord.ActivityType.listening:
                    embed.add_field(name='Активность', value=f'Слушает {member.activity.title}')
                else:
                    embed.add_field(name='Активность', value='Неизвестно')

            embed.add_field(name='Присоединился в',
                            value=f'`{member.joined_at.strftime("%Y-%m-%d %H:%M:%S.%f %Z%z")} (UTC)`', inline=False)

        embed.add_field(name='Аккаунт создан в',
                        value=f'`{user.created_at.strftime("%Y-%m-%d %H:%M:%S.%f %Z%z")} (UTC)`', inline=False)

        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Utils(bot))
