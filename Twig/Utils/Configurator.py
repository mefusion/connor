import yaml

# Попытка получения конфигурации
try:
    # Подключение файла конфигурации
    __temp__ = open('./Config/master.yml', 'r', encoding='utf-8')
    # Загрузка данных из файла конфигурации
    cfg = yaml.safe_load(__temp__)
    cfg = cfg['CONFIG']
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


# Попытка получения белого списка
try:
    # Подключение файла конфигурации
    __temp__ = open('./Config/master.yml', 'r', encoding='utf-8')
    # Загрузка данных из файла конфигурации
    whitelist = yaml.safe_load(__temp__)
    whitelist = whitelist['whitelist'.upper()]
    # Удаление временных данных
    __temp__.close()
    del __temp__
except Exception as err:
    print(err)

# Попытка получения белого списка
try:
    # Подключение файла конфигурации
    __temp__ = open('./Config/master.yml', 'r', encoding='utf-8')
    # Загрузка данных из файла конфигурации
    IGNORED_CHANNELS = yaml.safe_load(__temp__)
    IGNORED_CHANNELS = IGNORED_CHANNELS['ignored_channels'.upper()]
    # Удаление временных данных
    __temp__.close()
    del __temp__
except Exception as err:
    print(err)

# Попытка получения списка модулей, включаемых при запуске бота
try:
    # Подключение файла конфигурации
    __temp__ = open('./Config/master.yml', 'r', encoding='utf-8')
    # Загрузка данных из файла конфигурации
    INITIAL_COGS = yaml.safe_load(__temp__)
    INITIAL_COGS = INITIAL_COGS['INITIAL_COGS'.upper()]
    # Удаление временных данных
    __temp__.close()
    del __temp__
except Exception as err:
    print(err)