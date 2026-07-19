import sqlite3
import os

DATABASE_PATH = "data/bot.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_database():
    if not os.path.exists("data"):
        os.makedirs("data")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS survivors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            overos INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            timezone TEXT DEFAULT 'UTC',
            status TEXT DEFAULT 'Vivo',
            last_explore TIMESTAMP,
            health INTEGER DEFAULT 100
        )
    """)

    # Tabla que almacena los efectos de cada superviviente.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS survivor_effects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            survivor_id INTEGER NOT NULL,
            effect TEXT NOT NULL,
            created_at TEXT,
            progress INTEGER DEFAULT 0,
            

        FOREIGN KEY (survivor_id)
            REFERENCES survivors(id)
            ON DELETE CASCADE
    )
""")

    cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    survivor_id INTEGER NOT NULL,
    item TEXT NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,

    FOREIGN KEY (survivor_id)
    REFERENCES survivors(id)
    ON DELETE CASCADE,

    UNIQUE(survivor_id, item)
)
""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS active_effects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        survivor_id INTEGER NOT NULL,
        effect TEXT NOT NULL,
        duration INTEGER NOT NULL,

        FOREIGN KEY (survivor_id)
        REFERENCES survivors(id)
    )
    """)

    connection.commit()
    connection.close()
