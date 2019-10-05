import yaml
import discord
from discord.ext import commands


async def get_mod_log_channel(guild_id):
    try:
        with open(f'./Config/{guild_id}/guildSettings.yml', 'r', encoding='utf-8') as __temp_conf__:
            mod_log_channel_name = yaml.safe_load(__temp_conf__)['MOD_LOGS']['CHANNEL']
            return mod_log_channel_name
    except Exception as err:
        raise err


async def show_config(guild_id):
    try:
        with open(f'./Config/{guild_id}/guildSettings.yml', 'r', encoding='utf-8') as __temp_conf__:
            settings = yaml.safe_load(__temp_conf__)
            settings_temp = ""

            for setting, parameters in settings.items():
                settings_temp += f"{setting}: {parameters}\n\n"

            settings = settings_temp
            del settings_temp

            return str(settings)
    except Exception as err:
        raise err


async def get_whitelist():
    try:
        with open('./Config/master.yml', 'r', encoding='utf-8') as __temp_master__:
            return tuple(yaml.safe_load(__temp_master__)['WHITELIST'])
    except Exception as err:
        raise err


async def what_prefix(guild_id):
    try:
        # Подключение файла конфигурации префиксов
        with open(f'./Config/{guild_id}/guildSettings.yml', 'r', encoding='utf-8') as prefixes_cfg:
            _prefixes_cfg = yaml.safe_load(prefixes_cfg)['PREFIX']
            return _prefixes_cfg
    except Exception as err:
        raise err


# Попытка получения конфигурации
try:
    # Подключение файла конфигурации
    __temp__ = open('./Config/master.yml', 'r', encoding='utf-8')
    # Загрузка данных из файла конфигурации
    master = yaml.safe_load(__temp__)
    cfg = master['CONFIG'.upper()]
    # Получаем список игнорируемых каналов (не будет считаться уровень) и превращаем в кортеж
    IGNORED_CHANNELS = tuple(master['IGNORED_CHANNELS'])
    # Получаем список модулей, включаемых при загрузке и превращаем в кортеж
    INITIAL_COGS = tuple(master['INITIAL_COGS'])
    # Удаление временных данных
    __temp__.close()
    del __temp__
    # Переменные данных конфигурации
    BOT_PREFIX = cfg['PREFIX']
    BOT_STATUS = cfg['STATUS']
    BOT_MAINTAINERS = tuple(cfg['MAINTAINERS'])
    BOT_IS_NO_PERMS_MSG_ENABLED = cfg['SHOW_NO_PERMS_MESSAGES']
    MAIN_LOGS_CHANNEL = cfg['LOG_CHANNEL_ID']
    XP_LOGS_CHANNEL = cfg['XP_LOG_CHANNEL_ID']
    GIPHY_API = cfg['GIPHY_API_KEY']
    GENIUS_API_KEY = cfg['GENIUS_API_KEY']
    DEFAULT_STATUS = discord.Activity(
        name=BOT_STATUS + f' | {BOT_PREFIX}help', url="https://twitch.tv/defracted",
        type=discord.ActivityType.streaming)
except Exception as err:
    print(err)

