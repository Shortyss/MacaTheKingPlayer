import locale
import os
import sys

import PyQt6.sip
import subprocess
from PyQt6.QtCore import Qt, QTranslator
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QApplication

from player.library.constants import LANGUAGES
from player.library.styles import get_main_stylesheet_fhd, get_main_stylesheet
from player.settings_manager import get_setting, init_settings_table

from player.video_player import PlayerWindow
from player.utils import resource_path

os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--use-gl=disabled'

def preheat_chromium():
    dummy = QWebEngineView()
    dummy.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
    dummy.hide()
    dummy.deleteLater()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    size = screen.size()
    width = size.width()

    if width <= 1920:
        stylesheet_template = get_main_stylesheet_fhd()
        print("Nastaven FHD styl")
    else:
        stylesheet_template = get_main_stylesheet()

    app.setStyleSheet(stylesheet_template)
    saved_lang_code = get_setting("language")
    lang_to_load = None
    if saved_lang_code:
        lang_to_load = saved_lang_code
    else:
        try:
            os_lang_code, _ = locale.getdefaultlocale()
            os_lang_short = os_lang_code.split('_')[0]
            if os_lang_short in LANGUAGES:
                lang_to_load = os_lang_short
        except Exception:
            pass

    translator = QTranslator()
    if lang_to_load and lang_to_load != "cs":
        filename = LANGUAGES[lang_to_load]
        path = resource_path(f"translations/{filename}.qm")
        if translator.load(path):
            app.installTranslator(translator)
            print(f"Překlad '{filename}.qm' úspěšně NAČTEN.")
        else:
            print(f"CHYBA: Překlad '{filename}.qm' se nepodařilo načíst.")
    else:
        print("Používá se výchozí jazyk (čeština).")

    preheat_chromium()
    app.setStyle("Fusion")
    player_window = PlayerWindow()
    init_settings_table()
    player_window.show()
    sys.exit(app.exec())