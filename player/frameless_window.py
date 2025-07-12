import sys
from PyQt6.QtCore import Qt, QPoint, QRect
from PyQt6.QtGui import QMouseEvent, QCursor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QApplication


class FramelessWindow(QWidget):
    def __init__(self, title="Okno", parent=None):
        super().__init__(parent)

        # --- Základní nastavení okna ---
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # Umožní zakulacené rohy
        self.setStyleSheet("background-color: #2c3e50; border-radius: 10px;")

        # --- Atributy pro pohyb a změnu velikosti ---
        self.grip_size = 8
        self._moving = False
        self._resizing = False
        self._drag_position = QPoint()
        self._resize_edges = Qt.Edge(0)
        self._start_geometry = QRect()

        # --- Hlavní layout ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Okraje na nule, řešíme si je sami
        main_layout.setSpacing(0)

        # --- Titulkový pruh (Title Bar) ---
        self.title_bar = QWidget()
        self.title_bar.setFixedHeight(32)
        self.title_bar.setStyleSheet("""
            background-color: #34495e;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
            border-bottom: 1px solid #2c3e50;
        """)
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 5, 0)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #ecf0f1; font-weight: bold;")

        btn_close = QPushButton("×")
        btn_close.setFixedSize(22, 22)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c; color: white;
                border-radius: 11px; border: none; font-weight: bold;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        btn_close.clicked.connect(self.close)

        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        title_layout.addWidget(btn_close)

        # --- Oblast pro obsah (Content Area) ---
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(5, 5, 5, 5)

        # Sestavení okna
        main_layout.addWidget(self.title_bar)
        main_layout.addWidget(self.content_area, 1)  # 1 = roztáhne se

        # Zapnutí sledování myši, aby se kurzor měnil i bez kliknutí
        self.setMouseTracking(True)

    def setCentralWidget(self, widget: QWidget):
        """Vloží widget do oblasti pro obsah."""
        # Pokud už tam něco je, smažeme to
        if self.content_layout.count() > 0:
            old_widget = self.content_layout.takeAt(0).widget()
            if old_widget:
                old_widget.deleteLater()

        self.content_layout.addWidget(widget)
        # Zapneme sledování myši i na vloženém widgetu a jeho dětech
        widget.setMouseTracking(True)
        for child in widget.findChildren(QWidget):
            child.setMouseTracking(True)

    # ----------- LOGIKA PRO POHYB A ZMĚNU VELIKOSTI ----------

    def update_cursor_shape(self):
        """Mění tvar kurzoru, když se myš blíží k okrajům."""
        # Získáme pozici myši relativně k oknu
        pos = self.mapFromGlobal(QCursor.pos())
        edges = Qt.Edge(0)
        margin = self.grip_size

        if pos.x() < margin: edges |= Qt.Edge.LeftEdge
        if pos.x() > self.width() - margin: edges |= Qt.Edge.RightEdge
        if pos.y() < margin: edges |= Qt.Edge.TopEdge
        if pos.y() > self.height() - margin: edges |= Qt.Edge.BottomEdge

        self._resize_edges = edges

        if edges == (Qt.Edge.TopEdge | Qt.Edge.LeftEdge) or edges == (Qt.Edge.BottomEdge | Qt.Edge.RightEdge):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif edges == (Qt.Edge.TopEdge | Qt.Edge.RightEdge) or edges == (Qt.Edge.BottomEdge | Qt.Edge.LeftEdge):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif edges & (Qt.Edge.LeftEdge | Qt.Edge.RightEdge):
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif edges & (Qt.Edge.TopEdge | Qt.Edge.BottomEdge):
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        else:
            self.unsetCursor()

    def mousePressEvent(self, event: QMouseEvent):
        """Při kliknutí zjistí, jestli začínáme přesun nebo změnu velikosti."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._moving = False
            self._resizing = False

            # Zjistíme, jestli jsme na titulkovém pruhu pro přesun
            if self.title_bar.underMouse():
                self._moving = True
                # Uložíme si "offset" - pozici kliknutí relativně k pozici okna
                self._drag_position = event.globalPosition().toPoint() - self.pos()
                event.accept()
                return

            # Zjistíme, jestli jsme na okraji pro změnu velikosti
            if self._resize_edges != Qt.Edge(0):
                self._resizing = True
                # Uložíme si globální pozici a původní geometrii
                self._drag_position = event.globalPosition().toPoint()
                self._start_geometry = self.geometry()
                event.accept()
                return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Při pohybu myši buď přesouvá, mění velikost, nebo jen aktualizuje kurzor."""
        # Pokud přesouváme okno
        if self._moving:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            return

        # Pokud měníme velikost okna
        if self._resizing:
            global_pos = event.globalPosition().toPoint()
            delta = global_pos - self._drag_position
            new_geometry = QRect(self._start_geometry)

            if self._resize_edges & Qt.Edge.LeftEdge:
                new_geometry.setLeft(self._start_geometry.left() + delta.x())
            if self._resize_edges & Qt.Edge.RightEdge:
                new_geometry.setRight(self._start_geometry.right() + delta.x())
            if self._resize_edges & Qt.Edge.TopEdge:
                new_geometry.setTop(self._start_geometry.top() + delta.y())
            if self._resize_edges & Qt.Edge.BottomEdge:
                new_geometry.setBottom(self._start_geometry.bottom() + delta.y())

            self.setGeometry(new_geometry)

        # Pokud nic neděláme, jen aktualizujeme tvar kurzoru
        else:
            self.update_cursor_shape()

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Při puštění myši vše resetuje."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._moving = False
            self._resizing = False
            # Po puštění znovu zkontrolujeme kurzor
            self.update_cursor_shape()
        super().mouseReleaseEvent(event)


# --- Příklad použití, pokud bys chtěl spustit tento soubor samostatně ---
if __name__ == '__main__':
    app = QApplication(sys.argv)

    main_window = FramelessWindow(title="Moje Vlastní Okno")

    content_widget = QWidget()
    content_widget.setStyleSheet("background-color: #34495e; border-radius: 0px;")
    content_label = QLabel("Tady je můj obsah!", alignment=Qt.AlignmentFlag.AlignCenter)
    content_label.setStyleSheet("color: white; font-size: 24px;")
    content_layout = QVBoxLayout(content_widget)
    content_layout.addWidget(content_label)

    main_window.setCentralWidget(content_widget)
    main_window.resize(500, 300)
    main_window.show()

    sys.exit(app.exec())