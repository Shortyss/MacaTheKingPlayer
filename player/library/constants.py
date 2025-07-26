ALL_GENRES = (
    "Akční", "Dobrodružný", "Komedie", "Drama", "Fantasy", "Horor",
    "Sci-Fi", "Thriller", "Mysteriózní", "Romantický", "Animovaný",
    "Rodinný", "Krimi", "Válečný", "Historický", "Hudební", "Western"
)

PLACEHOLDER_POSTER = "assets/icons/KingPlayer6.png"
SUPPORTED_EXTS = ('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mpg', '.mpeg')


def _for_translator_tool_only():
    """
    Tato funkce se NIKDY NEVOLÁ.
    Její jediný účel je, aby nástroj pylupdate6 našel všechny tyto texty.
    """
    from PyQt6.QtCore import QCoreApplication

    # Používáme plný název, aby to pylupdate6 našel
    QCoreApplication.translate("Genres", "Akční")
    QCoreApplication.translate("Genres", "Dobrodružný")
    QCoreApplication.translate("Genres", "Komedie")
    QCoreApplication.translate("Genres", "Drama")
    QCoreApplication.translate("Genres", "Fantasy")
    QCoreApplication.translate("Genres", "Horor")
    QCoreApplication.translate("Genres", "Sci-Fi")
    QCoreApplication.translate("Genres", "Thriller")
    QCoreApplication.translate("Genres", "Mysteriózní")
    QCoreApplication.translate("Genres", "Romantický")
    QCoreApplication.translate("Genres", "Animovaný")
    QCoreApplication.translate("Genres", "Rodinný")
    QCoreApplication.translate("Genres", "Krimi")
    QCoreApplication.translate("Genres", "Válečný")
    QCoreApplication.translate("Genres", "Historický")
    QCoreApplication.translate("Genres", "Hudební")
    QCoreApplication.translate("Genres", "Western")


LANG_METADATA = {
    "cs": {"native_name": "Čeština", "icon": "assets/flags/cz.png"},
    "en": {"native_name": "English", "icon": "assets/flags/gb.svg"},
    "de": {"native_name": "Deutsch", "icon": "assets/flags/de.svg"},
    "fr": {"native_name": "Français", "icon": "assets/flags/fr.png"},
    "es": {"native_name": "Español", "icon": "assets/flags/es.png"},
    "pl": {"native_name": "Polski", "icon": "assets/flags/pl.png"},
    "ru": {"native_name": "Русский", "icon": "assets/flags/ru.png"},
    "zh": {"native_name": "中文", "icon": "assets/flags/cn.svg"},
    "eo": {"native_name": "Esperanto", "icon": "assets/flags/eo.png"},
    "isv": {"native_name": "Меджусловјанскы", "icon": "assets/flags/isv.svg"},
    "tlh": {"native_name": "tlhIngan Hol", "icon": "assets/flags/kli.png"}
}

# Slovník pro načítání správných .qm souborů v main.py
LANGUAGES = {
    "en": "english",
    "de": "german",
    "fr": "french",
    "es": "spanish",
    "pl": "polish",
    "ru": "russian",
    "zh": "chinese",
    "eo": "esperanto",
    "isv": "interslavic",
    "tlh": "klingon"
}