# main.py

import sys
from PyQt6.QtWidgets import QApplication
from player.video_player import PlayerWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    player_window = PlayerWindow()
    player_window.show()
    sys.exit(app.exec())