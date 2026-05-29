import sqlite3


DB_NAME = "memory.db"


def create_database():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    # Chats table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_number TEXT,
        role TEXT,
        message TEXT
    )
    """)

    # Customer state table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customer_state (
        user_number TEXT PRIMARY KEY,
        model_name TEXT,
        size_ft TEXT,
        dimension_space TEXT,
        material TEXT,
        uparna_color TEXT,
        dotar_color TEXT,
        extra_requirements TEXT,
        showcase_sent INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

def save_message(user_number, role, message):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO chats (user_number, role, message)
    VALUES (?, ?, ?)
    """, (user_number, role, message))

    conn.commit()
    conn.close()


def get_recent_messages(user_number, limit=10):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
    SELECT role, message
    FROM chats
    WHERE user_number=?
    ORDER BY id DESC
    LIMIT ?
    """, (user_number, limit))

    messages = cursor.fetchall()

    conn.close()

    return list(reversed(messages))

def get_last_product(user_number):

    conn = sqlite3.connect("memory.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT message
        FROM chats
        WHERE user_number = ?
        AND role = 'assistant'
        ORDER BY id DESC
        LIMIT 10
    """, (user_number,))

    rows = cursor.fetchall()

    conn.close()

    for row in rows:

        message = row[0].lower()

        if "ganpati" in message:
            return "ganpati"

        elif "laxmi" in message:
            return "laxmi"

        elif "bail" in message or "ox" in message:
            return "ox"

    return None

def get_customer_state(user_number):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        model_name,
        size_ft,
        dimension_space,
        material,
        uparna_color,
        dotar_color,
        extra_requirements,
        showcase_sent
    FROM customer_state
    WHERE user_number = ?
    """, (user_number,))

    row = cursor.fetchone()

    conn.close()

    if not row:
        return None

    return {
        "model_name": row[0],
        "size_ft": row[1],
        "dimension_space": row[2],
        "material": row[3],
        "uparna_color": row[4],
        "dotar_color": row[5],
        "extra_requirements": row[6],
        "showcase_sent": bool(row[7])
    }


def save_customer_state(
    user_number,
    model_name=None,
    size_ft=None,
    dimension_space=None,
    material=None,
    uparna_color=None,
    dotar_color=None,
    extra_requirements=None,
    showcase_sent=None
):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR REPLACE INTO customer_state (
        user_number,
        model_name,
        size_ft,
        dimension_space,
        material,
        uparna_color,
        dotar_color,
        extra_requirements,
        showcase_sent
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_number,
        model_name,
        size_ft,
        dimension_space,
        material,
        uparna_color,
        dotar_color,
        extra_requirements,
        showcase_sent
    ))

    conn.commit()
    conn.close()


def reset_customer_state(user_number):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM customer_state
    WHERE user_number = ?
    """, (user_number,))

    conn.commit()
    conn.close()