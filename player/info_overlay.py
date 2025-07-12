from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer

class InfoOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setWindowFlags(Qt.WindowType.Widget)  # DŮLEŽITÉ: není to okno, neblokuje focus!

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label = QLabel("", self)
        self.label.setStyleSheet("""
            QLabel {
                background: rgba(0,0,0,170);
                color: #aaffbb;
                border-radius: 13px;
                font-size: 19px;
                padding: 14px 22px;
                border: 2px solid #41ffae;
                min-width: 80px;
                qproperty-alignment: AlignCenter;
                text-shadow: 0 0 4px #4f8, 0 0 12px #0ff;
            }
        """)
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide)

        self.hide()  # Začíná schovaný

    def show_message(self, text, timeout=1100):
        self.label.setText(text)
        self.adjustSize()
        self.show()
        self.raise_()
        self.move_to_corner()
        self.timer.start(timeout)

    def show_volume(self, percent, timeout=1200):
        text = f"🔊 {percent}%"
        self.show_message(text, timeout)

    def move_to_corner(self):
        if not self.parent():
            return
        parent_rect = self.parent().rect()
        my_size = self.sizeHint()
        margin = 30
        x = parent_rect.width() - my_size.width() - margin
        y = margin
        self.move(x, y)


