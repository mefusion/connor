import asyncio
import asyncpg
import time

pool = None


async def initiate(actual_pool):
    global pool
    pool = actual_pool

    async with pool.acquire() as con:
        await con.execute(
            "CREATE TABLE IF NOT EXISTS public.xp (guild_id bigint, user_id bigint, balance integer, last_time_edited integer);")

        print("[POSTGRES] public.xp table initialized...")

        await con.execute(
            """CREATE TABLE IF NOT EXISTS public.infractions (inf_id bigint NOT NULL, 
                                                              guild_id bigint, 
                                                              user_id bigint, 
                                                              reason text, 
                                                              given_at timestamp DEFAULT NOW(), 
                                                              PRIMARY KEY (inf_id));""")

        print("[POSTGRES] public.infractions table initialized...")

    print("[POSTGRES] DBUtils initialized!")


class Infractions:
    def __init__(self):
        self.pool = None

    @staticmethod
    async def create(inf_type, guild_id, user_id, reason):
        pass


class Exp:
    def __init__(self):
        self.pool = None

    @staticmethod
    async def find_xp(guild_id, user_id):
        async with pool.acquire() as con:
            row = await con.fetchrow(
                f"SELECT balance FROM public.xp WHERE user_id={str(user_id)} AND guild_id={str(guild_id)};")

            if row is None:
                return None

            return row['balance']

    @staticmethod
    async def find_top_5(guild_id):
        async with pool.acquire() as con:
            row = await con.fetch(
                f"SELECT balance, user_id FROM public.xp WHERE guild_id={str(guild_id)} ORDER BY balance DESC LIMIT 5;")
            return row

    @staticmethod
    async def find_xp(guild_id, user_id):
        async with pool.acquire() as con:
            row = await con.fetchrow(
                f"SELECT balance FROM public.xp WHERE user_id={str(user_id)} AND guild_id={str(guild_id)};")

            if row is None:
                return None

            return row['balance']

    @staticmethod
    async def find_cooldown(guild_id, user_id):
        async with pool.acquire() as con:
            row = await con.fetchrow(
                f"SELECT last_time_edited FROM public.xp WHERE user_id={str(user_id)} AND guild_id={str(guild_id)};")

            if row is None:
                return None

            return row['last_time_edited']

    @staticmethod
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

    @staticmethod
    async def find_top_5(guild_id):
        async with pool.acquire() as con:
            row = await con.fetch(
                f"SELECT balance, user_id FROM public.xp WHERE guild_id={str(guild_id)} ORDER BY balance DESC LIMIT 5;")
            return row

    @staticmethod
    async def insert_into_db(guild_id, user_id, balance, timestamp=None):
        async with pool.acquire() as con:
            triggered_at = int(time.time())

            if timestamp is None:
                await con.execute(
                    f"INSERT INTO public.xp (guild_id, user_id, balance, last_time_edited) VALUES({str(guild_id)}, {str(user_id)}, {str(balance)}, {triggered_at - 500});")
            else:
                await con.execute(
                    f"INSERT INTO public.xp (guild_id, user_id, balance, last_time_edited) VALUES({str(guild_id)}, {str(user_id)}, {str(balance)}, {triggered_at});")

    @staticmethod
    async def delete_from_db(guild_id, user_id):
        async with pool.acquire() as con:
            await con.execute(f"DELETE FROM public.xp WHERE (user_id={str(user_id)} AND guild_id={str(guild_id)});")
