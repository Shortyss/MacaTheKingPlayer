# tmdb_api.py
import locale

import requests
from tmdbv3api import TMDb, Movie, Search
import os


class TMDB_API:
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("API klíč pro TMDB chybí!")

        self.tmdb = TMDb()
        self.tmdb.api_key = api_key

        # --- ZJIŠTĚNÍ JAZYKA OS ---
        try:
            # Zjistíme jazyk systému, např. ('cs_CZ', 'UTF-8')
            lang_code, _ = locale.getdefaultlocale()
            # Převedeme ho na formát, kterému rozumí TMDB (např. 'cs-CZ')
            self.os_language = lang_code.replace('_', '-')
            print(f"DEBUG: Jazyk systému detekován jako: {self.os_language}")
        except Exception:
            # Pokud se detekce nepovede, použijeme angličtinu jako výchozí
            self.os_language = 'en-US'
            print(f"DEBUG: Nepodařilo se detekovat jazyk, používám výchozí: {self.os_language}")

        self.tmdb.language = self.os_language  # Nastavíme primární jazyk
        self.tmdb.debug = False

        self.poster_base_url = "https://image.tmdb.org/t/p/w500"
        self.movie_api = Movie()
        self.search_api = Search()

    def search_movie(self, title):
        # ... tato metoda zůstává beze změny ...
        search_response = self.search_api.movies(title)
        if search_response and search_response.results:
            return search_response.results[0]
        return None

    def get_movie_details(self, movie_id):
        """
        Získá detaily filmu. Primárně v jazyce OS, ale pro videa
        se v případě neúspěchu zeptá i na anglické verze.
        """
        # 1. Získáme hlavní detaily v jazyce OS
        self.tmdb.language = self.os_language
        details = self.movie_api.details(movie_id, append_to_response='videos')
        if not details:
            return None

        videos_results = []
        if hasattr(details, 'videos') and details.videos['results']:
            videos_results = details.videos['results']

        # 2. POKUD jsme nenašli videa v jazyce OS a jazyk OS NENÍ angličtina...
        if not videos_results and 'en' not in self.os_language:
            # ...provedeme záložní volání pro anglická videa.
            self.tmdb.language = 'en-US'
            videos_en_response = self.movie_api.videos(movie_id)
            self.tmdb.language = self.os_language  # Vrátíme jazyk zpět

            if hasattr(videos_en_response, 'results') and videos_en_response.results:
                videos_results = videos_en_response.results

        # 3. Zpracujeme nejlepší nalezená videa
        trailer_url = None
        if videos_results:
            videos_sorted = sorted(videos_results, key=lambda v: v.get('type') == 'Trailer', reverse=True)
            for video in videos_sorted:
                if video.get('site') == 'YouTube':
                    trailer_url = f"https://www.youtube.com/watch?v=KEY{video.get('key')}"
                    break

        # 4. Sestavíme finální data
        countries = [c['name'] for c in details.production_countries] if hasattr(details,
                                                                                 'production_countries') else []
        genres = [g['name'] for g in details.genres] if hasattr(details, 'genres') else []

        film_data = {
            'title': details.title,
            'year': details.release_date.split('-')[0] if details.release_date else '',
            'overview': details.overview,
            'runtime': details.runtime,
            'genres': ", ".join(genres),
            'country': ", ".join(countries),
            'poster': self.poster_base_url + details.poster_path if details.poster_path else None,
            'trailer_url': trailer_url
        }
        return film_data


def download_poster_and_get_path(poster_url, film_filepath):
    if not poster_url:
        return None

    try:
        response = requests.get(poster_url, stream=True)
        response.raise_for_status()

        base_name = os.path.splitext(os.path.basename(film_filepath))[0]
        local_filename = f"{base_name}.jpg"
        local_path = os.path.join("assets", "posters", local_filename)

        # Uložíme obrázek na disk
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"Plakát stažen a uložen do: {local_path}")
        return local_path

    except requests.exceptions.RequestException as e:
        print(f"Chyba při stahování plakátu: {e}")
        return None