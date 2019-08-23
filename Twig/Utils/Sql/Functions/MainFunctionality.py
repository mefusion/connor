import aiosqlite
import time

DEFAULT_DB_FILENAME = 'twig-and-xp'


# Коннектор базы данных
async def connect_sqlite(filename):
    return await aiosqlite.connect(f'./Twig/Utils/Sql/Data/{str(filename)}.sqlite')


# Инициализатор БД
async def init_sql():
    con = await aiosqlite.connect(f'./Twig/Utils/Sql/Data/{DEFAULT_DB_FILENAME}.sqlite')

    await con.execute("CREATE TABLE IF NOT EXISTS data(user INTEGER, xp INTEGER, lastTimeEdited INTEGER)")
    await con.commit()

    await con.close()
    return print(f'[CORE:SQL] Database Twig/SQL/db/{DEFAULT_DB_FILENAME}.sqlite initialized!')


# Добавить нового пользователя в таблицу
async def add_user(user):
    called_at = int(time.time() - 300)
    con = await connect_sqlite(DEFAULT_DB_FILENAME)

    cur = await con.execute("INSERT INTO data VALUES(?, 0, ?)", (user, called_at))
    await con.commit()

    await cur.close()
    return await con.close()


# Удаляет пользователя из таблицы
async def del_user_form_data(user):
    con = await connect_sqlite(DEFAULT_DB_FILENAME)

    cur = await con.execute("DELETE FROM data WHERE user=%s" % user)
    await con.commit()

    await cur.close()
    await con.close()
    del con, cur


# Найти данные в таблице
async def fetch_data(fetch_this, where_is, where_val):
    con = await connect_sqlite(DEFAULT_DB_FILENAME)

    cur = await con.execute(f"SELECT %s FROM data where %s=%s" % (fetch_this, where_is, where_val))
    data = await cur.fetchall()
    new_data = []

    for elem in data:
        new_data.append(elem[0])

    data = new_data
    del new_data
    await cur.close()
    await con.close()
    del con, cur
    # Если данных не существует в БД, то возвращается None
    if len(data) <= 0:
        del data
        return None
    else:
        return data[0]


# Получит 5 пользователей, по возрастанию по очкам опыта
# Возвращает список вида ['user.id $$$ xp-balance']...
async def fetch_top5():
    con = await connect_sqlite(DEFAULT_DB_FILENAME)

    cur = await con.execute('SELECT user, xp FROM data ORDER BY xp DESC Limit 5')
    data = await cur.fetchall()

    temp_data = []

    for elem in data:
        temp_data.append(str(elem[0]) + ' $$$ ' + str(elem[1]))

    data = temp_data

    await cur.close()
    await con.close()
    del con, cur, temp_data

    return data


# Обновление каких-либо параметров в БД
async def update_data(update_this, update_to, where_is, where_val):
    con = await connect_sqlite(DEFAULT_DB_FILENAME)
    cur = await con.execute(f"UPDATE data SET %s=%s WHERE %s=%s" % (update_this, update_to, where_is, where_val))
    await con.commit()

    await cur.close()
    await con.close()
    del con, cur
