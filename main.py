import locale
import os
import sys

import dbus
from PyQt6.QtCore import Qt, QTranslator
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QApplication

from player.library.constants import LANGUAGES
from player.settings_manager import get_setting, init_settings_table

from player.video_player import PlayerWindow

os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--use-gl=disabled'

def preheat_chromium():
    dummy = QWebEngineView()
    dummy.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
    dummy.hide()
    dummy.deleteLater()

class InhibitSleep:
    def __init__(self, appname="MacaTheKingPlayer"):
        self.bus = dbus.SessionBus()
        self.screensaver = self.bus.get_object("org.freedesktop.ScreenSaver", "/org/freedesktop/ScreenSaver")
        self.cookie = self.screensaver.Inhibit(appname, "Přehrávání filmu!", dbus_interface="org.freedesktop.ScreenSaver")

    def __del__(self):
        try:
            self.screensaver.UnInhibit(self.cookie, dbus_interface="org.freedesktop.ScreenSaver")
        except Exception:
            pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
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
    if lang_to_load and lang_to_load != "cs":  # Čeština je výchozí
        filename = LANGUAGES[lang_to_load]
        path = f"translations/{filename}.qm"
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
    sleep_inhibitor = InhibitSleep()
    player_window.show()
    sys.exit(app.exec())