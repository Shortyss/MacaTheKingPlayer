from PyQt6.QtCore import pyqtSignal, Qt, QPointF
from PyQt6.QtGui import QCursor, QPolygonF, QPainter, QColor, QPen
from PyQt6.QtWidgets import QFrame, QPushButton, QWidget, QHBoxLayout


class AnimatedContainer(QFrame):
    mouse_left = pyqtSignal()

    def leaveEvent(self, event):
        self.mouse_left.emit()
        super().leaveEvent(event)

class TagButton(QPushButton):
    stateChanged = pyqtSignal(bool)

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._active = False
        self.setCheckable(True)
        self.toggled.connect(self.on_toggled)

    def isActive(self):
        return self._active

    def on_toggled(self, checked):
        self._active = checked
        self.setProperty("active", checked)
        self.style().polish(self)
        self.stateChanged.emit(checked)

class ClickableStar(QWidget):
    valueChanged = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(40, 40)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._value = 0.0

        # Tvar hvězdy jako polygon
        self.star_polygon = QPolygonF([
            QPointF(0.50, 0.00), QPointF(0.66, 0.30), QPointF(1.00, 0.30), QPointF(0.75, 0.55),
            QPointF(0.83, 0.90), QPointF(0.50, 0.70), QPointF(0.17, 0.90), QPointF(0.25, 0.55),
            QPointF(0.00, 0.30), QPointF(0.34, 0.30)
        ])
        # Škálování polygonu na velikost widgetu
        scaled_points = [QPointF(p.x() * self.width(), p.y() * self.height()) for p in self.star_polygon]
        self.star_polygon = QPolygonF(scaled_points)

    def setValue(self, value):
        if self._value != value:
            self._value = value
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        full_color = QColor("#ffd700")
        empty_color = QColor("#706800")

        pen = QPen(empty_color, 1.5)
        painter.setPen(pen)

        if self._value == 0:
            painter.setBrush(Qt.GlobalColor.transparent)
            painter.drawPolygon(self.star_polygon)
        elif self._value == 1.0:
            painter.setBrush(full_color)
            painter.drawPolygon(self.star_polygon)
        elif self._value == 0.5:
            w_half = self.width() // 2

            painter.save()
            painter.setClipRect(0, 0, w_half, self.height())
            painter.setBrush(full_color)
            painter.drawPolygon(self.star_polygon)
            painter.restore()

            painter.save()
            painter.setClipRect(w_half, 0, self.width() - w_half, self.height())
            painter.setBrush(Qt.GlobalColor.transparent)
            painter.drawPolygon(self.star_polygon)
            painter.restore()

    def mousePressEvent(self, event):
        if event.pos().x() < self.width() / 2:
            self.valueChanged.emit(0.5)
        else:
            self.valueChanged.emit(1.0)
        super().mousePressEvent(event)


class ClickableStarFilter(QWidget):
    ratingChanged = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rating = 0.0
        self.stars = []
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        for i in range(5):
            star = ClickableStar()
            star.valueChanged.connect(lambda val, index=i: self.on_star_clicked(index, val))
            self.stars.append(star)
            layout.addWidget(star)

    def on_star_clicked(self, index, value):
        new_rating = index + value
        if new_rating == self._rating:
            self._rating = 0.0
        else:
            self._rating = new_rating
        self.update_stars()
        self.ratingChanged.emit(self._rating)

    def update_stars(self):
        for i, star in enumerate(self.stars):
            value = max(0.0, min(1.0, self._rating - i))
            star.setValue(value)

    def setRating(self, rating):
        self._rating = float(rating)
        self.update_stars()


class StarRatingDisplay(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        self.star_widgets = []
        for _ in range(5):
            star = ClickableStar()
            star.setEnabled(False)
            layout.addWidget(star)
            self.star_widgets.append(star)

    def setRating(self, rating):
        val = round(float(rating) * 2) / 2
        for i, star_widget in enumerate(self.star_widgets):
            value = max(0.0, min(1.0, val - i))
            star_widget.setValue(value)

