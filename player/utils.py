import os
import sys
import subprocess
import shutil
import shlex

from PyQt6.QtCore import QTimer, QObject

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class InhibitSleep(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QTimer(self)
        self.timer.setInterval(30000)
        self.timer.timeout.connect(self.reset_screensaver)
        self.is_active = False
        self.start()

    def reset_screensaver(self):
        try:
            subprocess.call(['xdg-screensaver', 'reset'])
        except FileNotFoundError:
            self.stop()
        except Exception:
            pass

    def start(self):
        if not self.is_active:
            self.reset_screensaver()
            self.timer.start()
            self.is_active = True

    def stop(self):
        if self.is_active:
            self.timer.stop()
            self.is_active = False


def get_default_browser():
    try:
        output = subprocess.check_output(
            shlex.split('xdg-settings get default-web-browser'), text=True
        ).strip()
        if output.endswith('.desktop'):
            return output.split('.desktop')[0].replace('-browser', '')
    except Exception:
        return None
    return None

def open_url_safely(url):
    browser = get_default_browser()
    if browser:
        try:
            subprocess.Popen([browser, url])
            return
        except Exception:
            pass
    for b in ['firefox', 'brave', 'google-chrome', 'chromium', 'opera']:
        try:
            subprocess.Popen([b, url])
            return
        except Exception:
            continue
