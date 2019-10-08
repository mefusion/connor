import asyncio
import asyncpg
import yaml
import time

# Инициализация

with open('./Config/master.yml', 'r', encoding='utf-8') as DB_CONF:
    pool = None
    DB_CONF_DATA = yaml.safe_load(DB_CONF)['DATABASE_INFO']
    credentials = dict(
        user=str(DB_CONF_DATA['USER']),
        password=str(DB_CONF_DATA['PASSWORD']),
        database=str(DB_CONF_DATA['DATABASE']),
        host=str(DB_CONF_DATA['HOST'])
    )


async def initialize():
    global pool
    pool = await asyncpg.create_pool(**credentials, command_timeout=60)

    async with pool.acquire() as con:
        await con.execute(
            "CREATE TABLE IF NOT EXISTS public.xp (guild_id bigint, user_id bigint, balance integer, last_time_edited integer);")

    print("[POSTGRES] Database initialized!")


# Основные методы утильки

async def find_xp(guild_id, user_id):
    async with pool.acquire() as con:
        row = await con.fetchrow(
            f"SELECT balance FROM public.xp WHERE user_id={str(user_id)} AND guild_id={str(guild_id)};")

        if row is None:
            return None

        return row['balance']


async def find_cooldown(guild_id, user_id):
    async with pool.acquire() as con:
        row = await con.fetchrow(
            f"SELECT last_time_edited FROM public.xp WHERE user_id={str(user_id)} AND guild_id={str(guild_id)};")

        if row is None:
            return None

        return row['last_time_edited']


async def update_balance(guild_id, user_id, new_bal, timestamp=None):
    async with pool.acquire() as con:

        if timestamp is None:
            await con.execute(
                f"UPDATE public.xp SET balance={str(new_bal)} WHERE user_id={str(user_id)} AND guild_id={str(guild_id)};")
        else:
            await con.execute(
                f"UPDATE public.xp SET balance={str(new_bal)} WHERE user_id={str(user_id)} AND guild_id={str(guild_id)};")
            await con.execute(
                f"UPDATE public.xp SET last_time_edited={str(timestamp)} WHERE user_id={str(user_id)} AND guild_id={str(guild_id)};")


async def find_top_5(guild_id):
    async with pool.acquire() as con:
        row = await con.fetch(
            f"SELECT balance, user_id FROM public.xp WHERE guild_id={str(guild_id)} ORDER BY balance DESC LIMIT 5;")
        return row


async def insert_into_db(guild_id, user_id, balance, timestamp=None):
    async with pool.acquire() as con:
        triggered_at = int(time.time())

        if timestamp is None:
            await con.execute(
                f"INSERT INTO public.xp (guild_id, user_id, balance, last_time_edited) VALUES({str(guild_id)}, {str(user_id)}, {str(balance)}, {triggered_at - 500});")
        else:
            await con.execute(
                f"INSERT INTO public.xp (guild_id, user_id, balance, last_time_edited) VALUES({str(guild_id)}, {str(user_id)}, {str(balance)}, {triggered_at});")


async def delete_from_db(guild_id, user_id):
    async with pool.acquire() as con:
        await con.execute(f"DELETE FROM public.xp WHERE (user_id={str(user_id)} AND guild_id={str(guild_id)});")
