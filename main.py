# main.py

import sys

import dbus
from PyQt6.QtWidgets import QApplication

from player.playlist import init_settings_table
from player.video_player import PlayerWindow

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
    app.setStyle("Fusion")
    player_window = PlayerWindow()
    init_settings_table()
    sleep_inhibitor = InhibitSleep()
    player_window.show()
    sys.exit(app.exec())