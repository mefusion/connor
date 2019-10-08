from Saber.Utils.CustomErrors import SaberErrors
import yaml
from discord import Embed
from Saber.Utils.Configurator import what_prefix

BOT = None


def init(bot):
    global BOT
    BOT = bot


async def get_roles_shop_list(guild_id):
    try:
        with open(f'./Config/{guild_id}/guildSettings.yml', 'r', encoding='utf-8') as __temp__:
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


async def generate_roles_shop(guild_id):
    guild = BOT.get_guild(guild_id)
    roles = await get_roles_shop_list(guild_id)
    e = Embed(color=SECONDARY_COLOR).set_footer(
        text=f"Чтобы купить роль, используйте команду {await what_prefix(guild.id)}shop buy roles <номер_товара>")

    for key, value in roles.items():
        shop_id = value['SHOP_ID']
        role = guild.get_role(value['ROLE'])
        price = value['PRICE']

        e.add_field(name=f"Товар #{shop_id}", value=f"Роль: {role.mention}\nЦена: {price}", inline=False)

    del guild, roles
    return e
