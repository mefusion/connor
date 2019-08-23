import yaml

# Попытка получения конфигурации
try:
    # Подключение файла конфигурации
    __temp__ = open('./Config/master.yml', 'r', encoding='utf-8')
    # Загрузка данных из файла конфигурации
    master = yaml.safe_load(__temp__)
    cfg = master['CONFIG'.upper()]
    whitelist = master['whitelist'.upper()]
    IGNORED_CHANNELS = master['IGNORED_CHANNELS'.upper()]
    INITIAL_COGS = master['INITIAL_COGS'.upper()]
    # Удаление временных данных
    __temp__.close()
    del __temp__
    # Переменные данных конфигурации
    BOT_PREFIX = cfg['PREFIX']
    BOT_STATUS = cfg['STATUS']
    BOT_MAINTAINERS = cfg['MAINTAINERS']
    BOT_IS_NO_PERMS_MSG_ENABLED = cfg['SHOW_NO_PERMS_MESSAGES']
    MAIN_LOGS_CHANNEL = cfg['LOG_CHANNEL_ID']
    XP_LOGS_CHANNEL = cfg['XP_LOG_CHANNEL_ID']
except Exception as err:
    print(err)
