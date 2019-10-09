import asyncio
import asyncpg
import yaml
import time
import Saber.Utils.Sql.DBUtils as DBUtils

pool = None

with open('./Config/master.yml', 'r', encoding='utf-8') as DB_CONF:
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
    print("[POSTGRES] Pool connection initialized!")
    await DBUtils.initiate(pool)
    print("[POSTGRES] Database initialized!")
