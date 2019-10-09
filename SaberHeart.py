import asyncio
import discord
from discord.ext import commands
import Saber.SaberCore as Saber
from Saber.Utils.Logger import OldLog
import Saber.Utils.Sql.DBConnector as DBConnector
import Saber.Utils.ModLogs as ModLogs
import Saber.Utils.Logger as Logger
import errno
import Saber.Utils.Converters as Converters
import Saber.Utils.ShopGen as Shop
import yaml
import os
import traceback
import sys


async def get_prefix(client, message):
    try:
        with open(f'./Config/{message.guild.id}/guildSettings.yml', 'r', encoding='utf-8') as prefixes_cfg:
            prefixes = yaml.safe_load(prefixes_cfg)
            return commands.when_mentioned_or(*prefixes['PREFIX'])(client, message)
    except Exception as error:
        raise error


bot = commands.AutoShardedBot(command_prefix=get_prefix)


@bot.event
async def on_ready():
    # Инициализация БД
    await DBConnector.initialize()

    # Загружаются коги
    for extension in Saber.INITIAL_COGS:
        try:
            bot.load_extension(extension)
            print(f'[COGS] Cog {extension} has been loaded!')
        except Exception as e:
            print(f'Failed to load extension {extension} because {e}', file=sys.stderr)
            traceback.print_exc()

    # Информируется мэинтэйнер
    await OldLog(log_data=':wave: Бот включен.').send(bot, Saber.MAIN_LOGS_CHANNEL)
    await bot.change_presence(activity=Saber.DEFAULT_STATUS)
    return print(f'[CORE] Logged in as {bot.user.name}#{bot.user.discriminator}')


@bot.event
async def on_resumed():
    await OldLog(log_data='\N{INFORMATION SOURCE} Соединение было потеряно и успешно восстановлено.').send(
        bot, Saber.MAIN_LOGS_CHANNEL)
    return print(f'[CORE] Connection resumed.')


@bot.event
async def on_guild_join(guild):
    if not os.path.exists(os.path.dirname(f'./Config/{guild.id}/guildSettings.yml')):
        try:
            print("[CORE] New guild, creating guildSetting.yml file...")
            os.makedirs(os.path.dirname(f'./Config/{guild.id}/guildSettings.yml'))

            with open(f'./Config/{guild.id}/guildSettings.yml', 'w+', encoding='utf-8') as guildSettingsFile:
                yaml.dump(Saber.DEFAULT_CONFIG, guildSettingsFile)

            print("[CORE] guildSettings.yml file was created!")
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise
        except Exception as generics:
            raise generics


if __name__ == '__main__':
    # Инициализация ютилек, требующих клиент бота
    Converters.init(bot)
    ModLogs.init(bot)
    Logger.init(bot)
    Shop.init(bot)

Saber.authorize(bot)
