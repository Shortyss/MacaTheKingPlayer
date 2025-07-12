from PyQt6.QtWidgets import QApplication, QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt

class DragDropList(QListWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setMinimumSize(400, 300)

    def dragEnterEvent(self, event):
        print("DRAG ENTER")
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        print("DRAG MOVE")
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        print("DROP!")
        if event.mimeData().hasUrls():
            files = [url.toLocalFile() for url in event.mimeData().urls()]
            for f in files:
                self.addItem(QListWidgetItem(f))
            event.accept()
        else:
            event.ignore()

app = QApplication([])
w = DragDropList()
w.show()
app.exec()
