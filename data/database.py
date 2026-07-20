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

    # NUEVA TABLA (FASE 9): Sistema de Misiones
    # UNIQUE(survivor_id) para que solo tengan 1 misión activa a la vez.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            survivor_id INTEGER UNIQUE NOT NULL,
            quest_id TEXT NOT NULL,
            target TEXT NOT NULL,
            progress INTEGER DEFAULT 0,
            required INTEGER NOT NULL,
            status TEXT DEFAULT 'activa',

            FOREIGN KEY (survivor_id)
            REFERENCES survivors(id)
            ON DELETE CASCADE
        )
    """)

    # NUEVAS TABLAS (FASE 11): Estadísticas y Logros
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stats (
            survivor_id INTEGER PRIMARY KEY,
            explorations INTEGER DEFAULT 0,
            enemies_defeated INTEGER DEFAULT 0,
            quests_completed INTEGER DEFAULT 0,
            
            FOREIGN KEY (survivor_id)
            REFERENCES survivors(id)
            ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            survivor_id INTEGER NOT NULL,
            achievement_id TEXT NOT NULL,
            unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (survivor_id)
            REFERENCES survivors(id)
            ON DELETE CASCADE,
            
            UNIQUE(survivor_id, achievement_id)
        )
    """)

    # NUEVAS COLUMNAS (FASE 12): Sistema de Niveles y Experiencia
    try:
        cursor.execute("ALTER TABLE survivors ADD COLUMN level INTEGER DEFAULT 1")
    except sqlite3.OperationalError:
        pass  # La columna ya existe

    try:
        cursor.execute("ALTER TABLE survivors ADD COLUMN xp INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass  # La columna ya existe

    # NUEVAS COLUMNAS (SISTEMA DE EQUIPAMIENTO)
    try:
        cursor.execute(
            "ALTER TABLE survivors ADD COLUMN arma_equipada TEXT DEFAULT NULL"
        )
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute(
            "ALTER TABLE survivors ADD COLUMN armadura_equipada TEXT DEFAULT NULL"
        )
    except sqlite3.OperationalError:
        pass

    connection.commit()
    connection.close()
