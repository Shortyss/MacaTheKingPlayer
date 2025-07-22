
import os
import sys

import dbus
from PyQt6.QtCore import Qt
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QApplication

from player.playlist import init_settings_table
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
    preheat_chromium()
    app.setStyle("Fusion")
    player_window = PlayerWindow()
    init_settings_table()
    sleep_inhibitor = InhibitSleep()
    player_window.show()
    sys.exit(app.exec())