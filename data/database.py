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

    # 1. PRIMERO abrimos la conexión y creamos el cursor
    connection = get_connection()
    cursor = connection.cursor()

    # 2. LUEGO creamos la tabla principal (survivors)
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

    # 3. Y ahora sí, creamos las tablas que dependen de survivors
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

    # NUEVA TABLA (FASE 6): Almacena los datos del refugio de cada jugador.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shelters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            survivor_id INTEGER UNIQUE NOT NULL,
            level INTEGER DEFAULT 1,
            last_rest TIMESTAMP,

            FOREIGN KEY (survivor_id)
            REFERENCES survivors(id)
            ON DELETE CASCADE
        )
    """)

    # 4. Guardamos los cambios y cerramos
    connection.commit()
    connection.close()
