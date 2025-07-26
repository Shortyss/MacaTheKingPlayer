import sqlite3

DB_PATH = "playlist.db"

def get_connection():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS playlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS playlist_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            playlist_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            position INTEGER NOT NULL,
            FOREIGN KEY(playlist_id) REFERENCES playlists(id)
        )
    """)
    con.commit()
    return con

def init_settings_table():
    with get_connection() as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        con.commit()


def set_setting(key, value):
    with get_connection() as con:
        cur = con.cursor()
        cur.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        con.commit()

def get_setting(key, default=None):
    with get_connection() as con:
        cur = con.cursor()
        cur.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = cur.fetchone()
        return row[0] if row else default

init_settings_table()