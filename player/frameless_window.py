# player/frameless_window.py

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QPoint, QRect
from PyQt6.QtGui import QPainter, QColor, QPixmap, QIcon

BORDER_WIDTH = 7

class FramelessWindow(QWidget):
    def __init__(self, title="Frameless", icon_path=None, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.drag_pos = None
        self.resizing = False
        self.resize_dir = None

        # Header bar
        self.title_bar = QWidget(self)
        self.title_bar.setObjectName("TitleBar")
        self.title_bar.setFixedHeight(32)
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(8, 2, 8, 2)
        self.icon_label = QLabel()
        if icon_path:
            self.icon_label.setPixmap(QPixmap(icon_path).scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        title_layout.addWidget(self.icon_label)
        self.title_label = QLabel(title)
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()

        # Buttons
        self.btn_min = QPushButton("-")
        self.btn_max = QPushButton("[]")
        self.btn_close = QPushButton("×")
        for btn in (self.btn_min, self.btn_max, self.btn_close):
            btn.setFixedSize(28, 28)
            btn.setStyleSheet("QPushButton { background: none; border: none; color: #aaf0fc; font-size: 18px; } QPushButton:hover { color: #22ffc6; }")
        self.btn_min.clicked.connect(self.showMinimized)
        self.btn_max.clicked.connect(self.toggle_max_restore)
        self.btn_close.clicked.connect(self.close)
        title_layout.addWidget(self.btn_min)
        title_layout.addWidget(self.btn_max)
        title_layout.addWidget(self.btn_close)

        # Main layout
        self.central_widget = QWidget()
        self.central_layout = QVBoxLayout(self.central_widget)
        self.central_layout.setContentsMargins(0, 0, 0, 0)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.title_bar)
        main_layout.addWidget(self.central_widget)

        # Style
        self.setStyleSheet("""
        #TitleBar {
            background: rgba(34, 43, 66, 200);
            border-top-left-radius: 16px;
            border-top-right-radius: 16px;
        }
        FramelessWindow {
            background: rgba(34, 43, 66, 180);
            border-radius: 20px;
        }
        """)

        # State
        self._is_maximized = False

    def setCentralWidget(self, widget):
        self.central_layout.addWidget(widget)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.pos()
            if self.title_bar.geometry().contains(pos):
                self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            else:
                self._detect_resize(event)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
        elif self.resizing:
            self._do_resize(event)
        else:
            self._update_cursor(event)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.drag_pos = None
        self.resizing = False
        self.resize_dir = None
        super().mouseReleaseEvent(event)

    def _detect_resize(self, event):
        pos = event.pos()
        rect = self.rect()
        self.resizing = False
        if pos.x() <= BORDER_WIDTH and pos.y() <= BORDER_WIDTH:
            self.resizing, self.resize_dir = True, "topleft"
        elif pos.x() >= rect.width() - BORDER_WIDTH and pos.y() <= BORDER_WIDTH:
            self.resizing, self.resize_dir = True, "topright"
        elif pos.x() <= BORDER_WIDTH and pos.y() >= rect.height() - BORDER_WIDTH:
            self.resizing, self.resize_dir = True, "bottomleft"
        elif pos.x() >= rect.width() - BORDER_WIDTH and pos.y() >= rect.height() - BORDER_WIDTH:
            self.resizing, self.resize_dir = True, "bottomright"
        elif pos.x() <= BORDER_WIDTH:
            self.resizing, self.resize_dir = True, "left"
        elif pos.x() >= rect.width() - BORDER_WIDTH:
            self.resizing, self.resize_dir = True, "right"
        elif pos.y() <= BORDER_WIDTH:
            self.resizing, self.resize_dir = True, "top"
        elif pos.y() >= rect.height() - BORDER_WIDTH:
            self.resizing, self.resize_dir = True, "bottom"

    def _do_resize(self, event):
        mouse = event.globalPosition().toPoint()
        geo = self.frameGeometry()
        x, y, w, h = geo.x(), geo.y(), geo.width(), geo.height()
        minw, minh = 320, 200
        dx = mouse.x() - x
        dy = mouse.y() - y

        if "left" in self.resize_dir:
            nx = min(mouse.x(), x + w - minw)
            nw = w + (x - nx)
            self.setGeometry(nx, y, nw, h)
        if "right" in self.resize_dir:
            nw = max(dx, minw)
            self.setGeometry(x, y, nw, h)
        if "top" in self.resize_dir:
            ny = min(mouse.y(), y + h - minh)
            nh = h + (y - ny)
            self.setGeometry(x, ny, w, nh)
        if "bottom" in self.resize_dir:
            nh = max(dy, minh)
            self.setGeometry(x, y, w, nh)

    def _update_cursor(self, event):
        pos = event.pos()
        rect = self.rect()
        if pos.x() <= BORDER_WIDTH and pos.y() <= BORDER_WIDTH:
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif pos.x() >= rect.width() - BORDER_WIDTH and pos.y() <= BORDER_WIDTH:
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif pos.x() <= BORDER_WIDTH and pos.y() >= rect.height() - BORDER_WIDTH:
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif pos.x() >= rect.width() - BORDER_WIDTH and pos.y() >= rect.height() - BORDER_WIDTH:
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif pos.x() <= BORDER_WIDTH or pos.x() >= rect.width() - BORDER_WIDTH:
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif pos.y() <= BORDER_WIDTH or pos.y() >= rect.height() - BORDER_WIDTH:
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def toggle_max_restore(self):
        if self._is_maximized:
            self.showNormal()
            self._is_maximized = False
        else:
            self.showMaximized()
            self._is_maximized = True

    def paintEvent(self, event):
        # Glassy background
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(34, 43, 66, 180))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 20, 20)
        super().paintEvent(event)
