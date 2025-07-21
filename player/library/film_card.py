from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QLabel, QVBoxLayout, QWidget, QCheckBox, QGraphicsOpacityEffect, \
    QFrame

from player.library.constants import PLACEHOLDER_POSTER
from player.library.custom_widgets import ClickableStarFilter, StarRatingDisplay


class FilmCard(QFrame):
    hover_triggered = pyqtSignal(bool, 'QVariant')

    def __init__(self, film_data, parent=None):
        super().__init__(parent)
        self.film_data = film_data
        self.select_mode = False

        self.setObjectName("filmCardContainer")  # Toto je teď vnější widget (okraj)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setFixedSize(230, 380)

        main_layout = QVBoxLayout(self)
        # Okraj nastavíme pomocí marginu vnějšího layoutu
        main_layout.setContentsMargins(3, 3, 3, 3)

        # Vytvoříme vnitřní widget pro obsah
        self.content_widget = QWidget(self)
        self.content_widget.setObjectName("filmCardContent")
        main_layout.addWidget(self.content_widget)

        self.front_widget = self._create_front_widget()

        # Obsah vložíme do vnitřního widgetu
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(self.front_widget)

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

    def setOpacity(self, opacity):
        self.opacity_effect.setOpacity(opacity)

    def enterEvent(self, event):
        if not self.select_mode:
            self.hover_triggered.emit(True, self)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self.select_mode:
            self.hover_triggered.emit(False, self)
        super().leaveEvent(event)

    def swap_widgets(self):
        new_index = 1 - self.stacked_widget.currentIndex()
        self.stacked_widget.setCurrentIndex(new_index)

    def show_front(self):
        self.stacked_widget.setCurrentIndex(0)

    def _create_front_widget(self):
        widget = QWidget()
        widget.setObjectName("filmCardContent")
        main_vbox = QVBoxLayout(widget)
        main_vbox.setContentsMargins(12, 12, 12, 12)
        main_vbox.setSpacing(10)

        self.checkbox = QCheckBox()
        self.checkbox.setVisible(False)
        main_vbox.addWidget(self.checkbox, alignment=Qt.AlignmentFlag.AlignLeft)

        self.title_label = QLabel(self.film_data.get("title", "???"))
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setWordWrap(True)
        self.title_label.setFixedHeight(48)
        main_vbox.addWidget(self.title_label)

        self.poster_label = QLabel()
        self.poster_label.setFixedSize(175, 225)
        self.poster_label.setScaledContents(True)
        pix = QPixmap(self.film_data.get("poster", PLACEHOLDER_POSTER)).scaled(175, 225,
                                                                               Qt.AspectRatioMode.KeepAspectRatio,
                                                                               Qt.TransformationMode.SmoothTransformation)
        self.poster_label.setPixmap(pix)
        main_vbox.addWidget(self.poster_label, alignment=Qt.AlignmentFlag.AlignCenter)
        main_vbox.addStretch(1)
        self.rating_widget = StarRatingDisplay()
        self.rating_widget.setRating(self.film_data.get("rating", 0))
        main_vbox.addWidget(self.rating_widget)
        return widget

    def _create_back_widget(self):
        """Vytvoří a vrátí widget pro zadní stranu a slovník s interaktivními prvky."""
        widget = QWidget()
        widget.setObjectName("filmCardContent")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        info_label = QLabel("Zde budou detaily filmu...")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label, 1)

        # Přidáváme klikací hvězdičky
        rating_widget = ClickableStarFilter()
        rating_widget.setRating(self.film_data.get('rating', 0))
        layout.addWidget(rating_widget, 0, Qt.AlignmentFlag.AlignCenter)

        # Přidáváme tlačítka
        button_layout = QHBoxLayout()
        btn_edit = QPushButton("Upravit")
        btn_delete = QPushButton("Smazat")
        button_layout.addWidget(btn_edit)
        button_layout.addWidget(btn_delete)
        layout.addLayout(button_layout)

        # Slovník obsahuje VŠECHNY tři klíče pro novou funkcionalitu
        interactive_widgets = {
            "edit_button": btn_edit,
            "delete_button": btn_delete,
            "rating_widget": rating_widget,
            "player": getattr(self, 'player', None),
        }
        return widget, interactive_widgets

    def update_data(self, film_data, select_mode=False):
        self.film_data = film_data

        if self.title_label.text() != film_data.get("title", "???"):
            self.title_label.setText(film_data.get("title", "???"))

        pix = QPixmap(self.film_data.get("poster", PLACEHOLDER_POSTER)).scaled(175, 225,
                                                                               Qt.AspectRatioMode.KeepAspectRatio,
                                                                               Qt.TransformationMode.SmoothTransformation)
        self.poster_label.setPixmap(pix)

        self.rating_widget.setRating(film_data.get("rating", 0))

        if self.select_mode != select_mode:
            self.select_mode = select_mode
            self.checkbox.setVisible(self.select_mode)
            self.checkbox.setChecked(False)

