import discord
from discord.ext import commands
import Saber.SaberCore as Saber
from Saber.Utils.Logger import Log
from Saber.Utils.Sql.Functions.MainFunctionality import init_sql
import Saber.Utils.ModLogs as ModLogs
import errno
import Saber.Utils.Converters as Converters
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

Converters.init(bot)
ModLogs.init(bot)


@bot.event
async def on_ready():
    # Инициализация БД
    await init_sql()
    print(f'[CORE] The bot is ready for duty!')
    await Log(log_data=':wave: Я уже работаю!').send(bot, Saber.MAIN_LOGS_CHANNEL)
    await bot.change_presence(activity=Saber.DEFAULT_STATUS)
    return print(f'[CORE] Logged in as {bot.user.name}#{bot.user.discriminator}')


@bot.event
async def on_resumed():
    await Log(log_data='\N{INFORMATION SOURCE} Соединение было потеряно и успешно восстановлено.').send(
        bot, Saber.MAIN_LOGS_CHANNEL)
    return print(f'[CORE] Connection resumed.')


@bot.event
async def on_guild_join(guild):
    if not os.path.exists(os.path.dirname(f'./Config/{guild.id}/guildSettings.yml')):
        try:
            print("[CORE] New guild, creating guildSetting.yml file...")
            os.makedirs(os.path.dirname(f'./Config/{guild.id}/guildSettings.yml'))

            guildSettingsTemp = dict(

                PREFIX=Saber.DEFAULT_PREFIX,

                MOD_LOGS=dict(
                    CHANNE=0
                ),

                WELCOMER=dict(
                    ENABLED=False,
                    CHANNEL=0,
                    MESSAGE_LIVES=20,
                    LOGGING=dict(
                        MOD_ACTIONS=0
                    )
                )
            )

            with open(f'./Config/{guild.id}/guildSettings.yml', 'w+', encoding='utf-8') as guildSettingsFile:
                yaml.dump(guildSettingsTemp, guildSettingsFile)

            del guildSettingsTemp
            print("[CORE] guildSettings.yml file was created!")
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
        except Exception as generics:
            raise generics


if __name__ == '__main__':
    for extension in Saber.INITIAL_COGS:
        try:
            bot.load_extension(extension)
            print(f'[CORE] Cog {extension} has been loaded!')
        except Exception as e:
            print(f'Failed to load extension {extension} because {e}', file=sys.stderr)
            traceback.print_exc()

Saber.authorize(bot)
