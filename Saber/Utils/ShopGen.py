from Saber.Utils.CustomErrors import SaberErrors
import yaml

BOT = None


def init(bot):
    global BOT
    BOT = bot


async def get_roles_shop_list(guild_id):
    try:
        with open(f'./Config/Guilds/{guild_id}/guildSettings.yml', 'r', encoding='utf-8') as __temp__:
            # Загрузка данных из файла конфигурации
            shop = yaml.safe_load(__temp__)
            # Выгружаем
            __temp__.close()
            # Получаем данные о всех ролях
            shop = shop['ROLE_REWARDS']
            return shop
    except FileNotFoundError:
        # Возвращаем None, если проблема с обнаружением файла
        return None
    except KeyError:
        raise SaberErrors.BadGuildConfiguration(
            f"Something is wrong in the configuration of guild {guild_id}, level ROLE_REWARDS.")
