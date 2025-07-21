import os
import re

from PyQt6.QtCore import pyqtSignal, QObject

from player.library.database_manager import DatabaseManager
from player.library.tmdb_api import download_poster_and_get_path, TMDB_API


class DeleteWorker(QObject):
    finished = pyqtSignal()
    def __init__(self, db_name, filepaths):
        super().__init__()
        self.db_name = db_name
        self.filepaths = filepaths

    def run(self):
        db = DatabaseManager(self.db_name)
        if self.filepaths:
            db.delete_films(self.filepaths)
        db.close()

        self.finished.emit()


def clean_title_for_search(filename):
    clean_name = os.path.splitext(filename.lower())[0]

    clean_name = re.sub(r'\(\d{4}\)', '', clean_name)

    # Odstraníme běžné "smetí"
    junk_patterns = [
        r'\b(1080p|720p|2160p|4k|bluray|brrip|web-dl|webrip|hdrip|dvdrip|x264|x265|hevc|aac|dts|ac3)\b',
        r'\b(cz|sk|en|dub|dabing|czdab|titulky|top|hd)\b',
        r'\[.*?\]'
    ]
    for pattern in junk_patterns:
        clean_name = re.sub(pattern, '', clean_name, flags=re.IGNORECASE)

    clean_name = re.sub(r'[._-]', ' ', clean_name)

    return " ".join(clean_name.split()).strip().capitalize()

class DataFetchingWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int, int, str)  # aktuální, celkem, název filmu
    film_updated = pyqtSignal(dict)

    def __init__(self, api_key, films_to_update):
        super().__init__()
        self.api_key = api_key
        self.films_to_update = films_to_update
        self.is_running = True

    def run(self):
        tmdb = TMDB_API(self.api_key)
        total = len(self.films_to_update)

        for i, film_data in enumerate(self.films_to_update):
            if not self.is_running:
                break

            query_title = clean_title_for_search(os.path.basename(film_data['filepath']))
            self.progress.emit(i + 1, total, query_title)

            search_result = tmdb.search_movie(query_title)
            if not search_result:
                continue

            details = tmdb.get_movie_details(search_result.id)
            if not details:
                continue

            # Stáhneme plakát a získáme LOKÁLNÍ cestu k němu
            local_poster_path = download_poster_and_get_path(details.get('poster'), film_data.get('filepath'))

            # Aktualizujeme původní slovník nově staženými daty
            film_data.update({
                'title': details.get('title'),
                'year': details.get('year'),
                'overview': details.get('overview'),
                'runtime': details.get('runtime'),
                'genres': details.get('genres'),
                'country': details.get('country'),
                'trailer_url': details.get('trailer_url'),
                'poster': local_poster_path if local_poster_path else film_data.get('poster')
            })

            self.film_updated.emit(film_data)

        self.finished.emit()

    def stop(self):
        self.is_running = False