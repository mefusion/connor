import discord
from discord.ext import commands
from Twig.TwigCore import *
from Twig.Utils.Logger import Log

# Модули, которые загружаются при запуске клиента бота
initial_extensions = [
    'Twig.Cogs.Admin',
    'Twig.Cogs.BotOwner',
    'Twig.Cogs.Levels',
    'Twig.Cogs.TwigExclusives',
    'Twig.Cogs.Utils',
]

bot = commands.AutoShardedBot(command_prefix=commands.when_mentioned_or(BOT_PREFIX))

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)


@bot.event
async def on_ready():
    print(f'[CORE] The bot is ready for duty!')
    await Log(log_data=':wave: Я уже работаю!').send(bot, MAIN_LOGS_CHANNEL)
    playing_now = discord.Activity(name=BOT_STATUS + f' | {BOT_PREFIX}help',
                                   type=discord.ActivityType.playing)
    await bot.change_presence(activity=playing_now)
    del playing_now
    return print(f'[CORE] Logged in as {bot.user.name}#{bot.user.discriminator}')


@bot.event
async def on_disconnect():
    await Log(log_data=':warning: Соединение потеряно!', log_type='warning').send(bot, MAIN_LOGS_CHANNEL)
    return print(f'[CORE] Connection lost!')


@bot.event
async def on_resumed():
    await Log(log_data=':repeat: Соединение восстановлено.').send(bot, MAIN_LOGS_CHANNEL)
    return print(f'[CORE] Connection resumed.')


bot.run(BOT_TOKEN, bot=True, reconnect=True)
