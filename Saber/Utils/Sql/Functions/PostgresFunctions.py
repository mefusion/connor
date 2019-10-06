import asyncio
import asyncpg
import yaml
import time

with open('./Config/master.yml', 'r', encoding='utf-8') as DB_CONF:
    DB_CONF_DATA = yaml.safe_load(DB_CONF)['DATABASE_INFO']
    credentials = dict(
        user=str(DB_CONF_DATA['USER']),
        password=str(DB_CONF_DATA['PASSWORD']),
        database=str(DB_CONF_DATA['DATABASE']),
        host=str(DB_CONF_DATA['HOST'])
    )


async def do_connect():
    return await asyncpg.connect(**credentials)


async def do_close(con=None, cur=None):
    if con is not None:
        await con.close()
        # print("[POSTGRES] Connection closed")

    if cur is not None:
        await cur.close()
        # print("[POSTGRES] Cursor closed")


async def initialize():
    con = await do_connect()
    await con.execute(
        "CREATE TABLE IF NOT EXISTS public.xp (guild_id bigint, user_id bigint, balance integer, last_time_edited integer);")
    print("[POSTGRES] Database initialized!")
    await do_close(con)


async def find_xp(guild_id, user_id):
    con = await do_connect()
    row = await con.fetchrow(
        f"SELECT balance FROM public.xp WHERE user_id={str(user_id)} AND guild_id={str(guild_id)};")
    await do_close(con)

    if row is None:
        return None

    return row['balance']


async def find_cooldown(guild_id, user_id):
    con = await do_connect()
    row = await con.fetchrow(
        f"SELECT last_time_edited FROM public.xp WHERE user_id={str(user_id)} AND guild_id={str(guild_id)};")
    await do_close(con)

    if row is None:
        return None

    return row['last_time_edited']


async def update_balance(guild_id, user_id, new_bal, timestamp=None):
    con = await do_connect()

    if timestamp is None:
        await con.execute(
            f"UPDATE public.xp SET balance={str(new_bal)} WHERE user_id={str(user_id)} AND guild_id={str(guild_id)};")
    else:
        await con.execute(
            f"UPDATE public.xp SET balance={str(new_bal)} WHERE user_id={str(user_id)} AND guild_id={str(guild_id)};")
        await con.execute(
            f"UPDATE public.xp SET last_time_edited={str(timestamp)} WHERE user_id={str(user_id)} AND guild_id={str(guild_id)};")

    await do_close(con)


async def find_top_5(guild_id):
    con = await do_connect()
    row = await con.fetch(
        f"SELECT balance, user_id FROM public.xp WHERE guild_id={str(guild_id)} ORDER BY balance DESC LIMIT 5;")
    await do_close(con)
    return row


async def insert_into_db(guild_id, user_id, balance, timestamp=None):
    con = await do_connect()
    triggered_at = int(time.time())

    if timestamp is None:
        await con.execute(
            f"INSERT INTO public.xp (guild_id, user_id, balance, last_time_edited) VALUES({str(guild_id)}, {str(user_id)}, {str(balance)}, {triggered_at - 500});")
    else:
        await con.execute(
            f"INSERT INTO public.xp (guild_id, user_id, balance, last_time_edited) VALUES({str(guild_id)}, {str(user_id)}, {str(balance)}, {triggered_at});")

    await do_close(con)


async def delete_from_db(guild_id, user_id):
    con = await do_connect()
    await con.execute(f"DELETE FROM public.xp WHERE (user_id={str(user_id)} AND guild_id={str(guild_id)});")
    await do_close(con)
