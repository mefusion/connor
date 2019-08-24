import yaml


def get_roles_shop_list(guild_id):
    try:
        # Подключение файла конфигурации
        __temp__ = open(f'./Config/Shops/{guild_id}.yml', 'r', encoding='utf-8')
    except FileNotFoundError:
        # Возвращаем None, если проблема с обнаружением файла
        return None
    else:
        # Загрузка данных из файла конфигурации
        shop = yaml.safe_load(__temp__)
        # Выгружаем
        __temp__.close()
        # Получаем данные о всех ролях
        shop = shop['ROLE_REWARDS']
        # Возвращаем объект
        return shop
