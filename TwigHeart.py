import discord
from discord.ext import commands
from Twig.TwigCore import *
from Twig.Utils.Logger import Log

bot = commands.AutoShardedBot(command_prefix=commands.when_mentioned_or(BOT_PREFIX))


@bot.event
async def on_ready():
    print(f'[CORE] The bot is ready for duty!')
    await Log(log_data=':wave: Я уже работаю!').send(bot, MAIN_LOGS_CHANNEL)
    return print(f'[CORE] Logged in as {bot.user.name}#{bot.user.discriminator}')


@bot.event
async def on_disconnect():
    await Log(log_data=':warning: Соединение потеряно!', log_type='warning').send(bot, MAIN_LOGS_CHANNEL)
    return print(f'[CORE] Connection lost!')


@bot.event
async def on_resumed():
    await Log(log_data=':repeat: Соединение восстановлено.').send(bot, MAIN_LOGS_CHANNEL)
    return print(f'[CORE] Connection resumed.')


@bot.command()
@commands.is_owner()
async def close(ctx):
    await ctx.send('Disconnecting...')
    return await bot.close()


bot.run(BOT_TOKEN)
