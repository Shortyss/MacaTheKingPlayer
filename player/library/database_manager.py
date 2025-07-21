import sqlite3


class DatabaseManager:
    def __init__(self, db_name="king_player_library.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS films (
                filepath TEXT PRIMARY KEY, 
                title TEXT, 
                year TEXT,
                rating REAL, 
                poster TEXT, 
                overview TEXT, 
                genres TEXT, 
                runtime INTEGER,
                trailer_url TEXT,
                country TEXT 
            )""")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS library_paths (path TEXT PRIMARY KEY)")
        self.conn.commit()

    def add_or_update_film(self, film_data):
        self.cursor.execute(
            """INSERT OR REPLACE INTO films 
               (filepath, title, year, rating, poster, overview, genres, runtime, trailer_url, country) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                film_data.get('filepath'), film_data.get('title'),
                film_data.get('year'), float(film_data.get('rating', 0)),
                film_data.get('poster'), film_data.get('overview'),
                film_data.get('genres'), film_data.get('runtime'),
                film_data.get('trailer_url'), film_data.get('country')
            )
        )
        self.conn.commit()

    def delete_film(self, filepath):
        self.cursor.execute("DELETE FROM films WHERE filepath = ?", (filepath,));
        self.conn.commit()

    def delete_films(self, filepaths):
        data_to_delete = [(path,) for path in filepaths]
        self.cursor.executemany("DELETE FROM films WHERE filepath = ?", data_to_delete)
        self.conn.commit()

    def get_all_films(self):
        self.cursor.execute("SELECT * FROM films")
        return [dict(row) for row in self.cursor.fetchall()]

    def add_library_path(self, path):
        self.cursor.execute("INSERT OR IGNORE INTO library_paths (path) VALUES (?)", (path,))
        self.conn.commit()

    def remove_library_path(self, path):
        self.cursor.execute("DELETE FROM library_paths WHERE path = ?", (path,))
        self.conn.commit()

    def get_library_paths(self):
        self.cursor.execute("SELECT path FROM library_paths")
        return [row['path'] for row in self.cursor.fetchall()]

    def close(self): self.conn.close()

