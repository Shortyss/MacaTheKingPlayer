import sys
from PyQt6.QtWidgets import QApplication, QListWidget, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

class TestPlaylist(QListWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() or event.source() == self:
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        # Pro externí soubory
        if event.mimeData().hasUrls():
            files = [url.toLocalFile() for url in event.mimeData().urls()]
            for file in files:
                self.addItem(file)
            event.acceptProposedAction()
        else:
            # Vnitřní přesun – nech defaultní chování
            super().dropEvent(event)

class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Drag & Drop Playlist")
        self.resize(400, 400)
        layout = QVBoxLayout(self)
        self.playlist = TestPlaylist()
        layout.addWidget(self.playlist)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = TestWindow()
    w.show()
    sys.exit(app.exec())
