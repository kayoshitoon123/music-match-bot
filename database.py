import aiosqlite

DB="music_match.db"


async def init_db():

    async with aiosqlite.connect(DB) as db:

        await db.execute("""

        CREATE TABLE IF NOT EXISTS users(

        telegram_id INTEGER PRIMARY KEY,

        name TEXT,
        age INTEGER,
        city TEXT,

        role TEXT,
        looking TEXT,

        photo TEXT,
        beat TEXT,

        description TEXT

        )

        """)

        await db.execute("""

        CREATE TABLE IF NOT EXISTS likes(

        user_from INTEGER,
        user_to INTEGER

        )

        """)

        await db.commit()


async def add_user(data):

    async with aiosqlite.connect(DB) as db:

        await db.execute(
        "INSERT OR REPLACE INTO users VALUES(?,?,?,?,?,?,?,?,?)",
        data
        )

        await db.commit()


async def get_user(user_id):

    async with aiosqlite.connect(DB) as db:

        cursor=await db.execute(
        "SELECT * FROM users WHERE telegram_id=?",
        (user_id,)
        )

        return await cursor.fetchone()


async def delete_user(user_id):

    async with aiosqlite.connect(DB) as db:

        await db.execute(
        "DELETE FROM users WHERE telegram_id=?",
        (user_id,)
        )

        await db.commit()


async def get_candidates(user):

    async with aiosqlite.connect(DB) as db:

        if user[5]=="🎵 Все равно":

            cursor=await db.execute("""

            SELECT * FROM users

            WHERE city=?
            AND age BETWEEN ? AND ?
            AND telegram_id != ?

            """,(user[3],user[2]-4,user[2]+4,user[0]))

        else:

            cursor=await db.execute("""

            SELECT * FROM users

            WHERE city=?
            AND age BETWEEN ? AND ?
            AND role=?
            AND telegram_id != ?

            """,(user[3],user[2]-4,user[2]+4,user[5],user[0]))

        return await cursor.fetchall()


async def get_any(user):

    async with aiosqlite.connect(DB) as db:

        cursor=await db.execute(

        "SELECT * FROM users WHERE telegram_id != ?",
        (user[0],)

        )

        return await cursor.fetchall()


async def add_like(a,b):

    async with aiosqlite.connect(DB) as db:

        await db.execute(
        "INSERT INTO likes VALUES(?,?)",
        (a,b)
        )

        await db.commit()


async def check_match(a,b):

    async with aiosqlite.connect(DB) as db:

        cursor=await db.execute("""

        SELECT * FROM likes

        WHERE user_from=? AND user_to=?

        """,(b,a))

        return await cursor.fetchone()