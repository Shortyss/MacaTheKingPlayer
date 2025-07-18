import os
import sys
import mpv
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QApplication

os.environ["LC_NUMERIC"] = "C"
os.environ["QT_QPA_PLATFORM"] = "wayland"

class MpvPlayer(QMainWindow):
    def __init__(self, video_path):
        super().__init__()
        self.setWindowTitle("MacaTheKingPlayer")
        self.resize(800, 600)

        self.mpv_widget = QWidget(self)
        self.setCentralWidget(self.mpv_widget)

        self.layout = QVBoxLayout(self.mpv_widget)
        self.play_pause_button = QPushButton("Play/Pause", self)
        self.stop_button = QPushButton("Stop", self)
        self.layout.addWidget(self.play_pause_button)
        self.layout.addWidget(self.stop_button)

        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        self.stop_button.clicked.connect(self.stop)

        self.mpv = None
        self.video_path = video_path
        self.initialize_mpv()

    def initialize_mpv(self):
        try:
            self.mpv = mpv.MPV(
                vo='x11',
                hwdec='auto',
                log_handler=print,
                loglevel='info'
            )
            self.mpv.play(self.video_path)
        except Exception as e:
            print(f"Chyba při inicializaci MPV: {e}")
            sys.exit(1)

    def toggle_play_pause(self):
        if not self.mpv:
            print("MPV není inicializováno.")
            return
        try:
            if self.mpv.pause:
                self.mpv.pause = False
                self.play_pause_button.setText("Pause")
            else:
                self.mpv.pause = True
                self.play_pause_button.setText("Play")
        except mpv.ShutdownError:
            print("MPV core byl ukončen.")
            self.mpv = None

    def stop(self):
        if not self.mpv:
            print("MPV není inicializováno.")
            return
        try:
            self.mpv.command('stop')
            self.play_pause_button.setText("Play")
        except mpv.ShutdownError:
            print("MPV core byl ukončen.")
            self.mpv = None

    def closeEvent(self, event):
        if self.mpv:
            try:
                self.mpv.terminate()
            except mpv.ShutdownError:
                pass
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = MpvPlayer('/run/media/maca/Filmy a Serialy/Komedie/Taxi 2.mp4')
    player.show()
    sys.exit(app.exec())