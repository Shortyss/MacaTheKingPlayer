
from PyQt6.QtCore import Qt, pyqtSignal, QUrl
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QLabel, QVBoxLayout, QWidget, QCheckBox, QGraphicsOpacityEffect, \
    QFrame, QTextEdit

from player.utils import resource_path
from .constants import get_placeholder_poster
from player.library.custom_widgets import ClickableStarFilter, StarRatingDisplay, TagButton
from player.library.flow_layout import FlowLayout


class FilmCard(QFrame):
    hover_triggered = pyqtSignal(bool, 'QVariant')
    play_film_requested = pyqtSignal(dict)

    def __init__(self, film_data, parent=None, player_window=None):
        super().__init__(parent)
        self.film_data = film_data
        self.player_window = player_window
        self.select_mode = False

        self.setObjectName("FilmCard")
        self.setFrameShape(QFrame.Shape.NoFrame)
        scale = 0.9
        self.setFixedSize(int(230 * scale), int(380 * scale))

        self.front_widget = self._create_front_widget()

        content_layout = QVBoxLayout(self)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(self.front_widget)

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        self.setOpacity(1.0)

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

    def _create_front_widget(self):
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")
        main_vbox = QVBoxLayout(widget)
        main_vbox.setContentsMargins(10, 8, 10, 9)
        main_vbox.setSpacing(4)

        self.checkbox = QCheckBox()
        self.checkbox.setVisible(False)
        main_vbox.addWidget(self.checkbox, alignment=Qt.AlignmentFlag.AlignLeft)

        self.title_label = QLabel(self.film_data.get("title", "???"))
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setWordWrap(True)
        self.title_label.setFixedHeight(40)
        main_vbox.addWidget(self.title_label)

        self.year_label = QLabel(str(self.film_data.get("year", "")))
        self.year_label.setObjectName("yearLabel")
        self.year_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_vbox.addWidget(self.year_label)

        main_vbox.addStretch(1)

        scale = 0.9
        poster_w = int(175 * scale)
        poster_h = int(225 * scale)
        self.poster_label = QLabel()
        self.poster_label.setFixedSize(poster_w, poster_h)
        self.poster_label.setScaledContents(True)
        pixmap_path = resource_path(self.film_data.get("poster") or get_placeholder_poster())
        pix = QPixmap(pixmap_path).scaled(
            poster_w, poster_h,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        if pix.isNull():
            print(f"[KINGPLAYER WARNING] Nepodařilo se načíst obrázek: {pixmap_path}")
        self.poster_label.setPixmap(pix)
        main_vbox.addWidget(self.poster_label, alignment=Qt.AlignmentFlag.AlignCenter)
        main_vbox.addStretch(1)
        self.rating_widget = StarRatingDisplay()
        self.rating_widget.setRating(self.film_data.get("rating", 0))
        main_vbox.addWidget(self.rating_widget)
        return widget

    def _create_back_widget(self):
        back_widget = QWidget()
        main_layout = QVBoxLayout(back_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(8)

        # Název filmu
        title = QLabel(self.film_data.get('title', '???'))
        title.setObjectName("backSideTitle")
        title.setWordWrap(True)
        main_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        # Přehrávač traileru NEBO Plakát
        trailer_url = self.film_data.get('trailer_url')
        self.web_view = None

        if trailer_url and 'youtube.com' in trailer_url:
            video_id = trailer_url.split('v=')[-1].split('&')[0]

            embed_url = f"https://www.youtube.com/embed/{video_id}?autoplay=1&mute=1&loop=1&controls=0"

            self.web_view = QWebEngineView()
            self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
            self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False)
            self.web_view.setUrl(QUrl(embed_url))

            main_layout.addWidget(self.web_view, stretch=1)
        else:
            poster = QLabel()
            poster.setAlignment(Qt.AlignmentFlag.AlignCenter)
            pixmap_path = resource_path(self.film_data.get("poster") or get_placeholder_poster())
            pix = QPixmap(pixmap_path)
            poster.setPixmap(
                pix.scaled(450, 500, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            main_layout.addWidget(poster, stretch=1)

        # Hlavní ovládací tlačítka
        controls_layout = QHBoxLayout()
        btn_play = QPushButton(self.tr("Přehrát film"))
        btn_play.clicked.connect(lambda: self.play_film_requested.emit(self.film_data))
        controls_layout.addWidget(btn_play)

        btn_mute = QPushButton()
        if self.web_view:
            btn_mute = QPushButton()
            btn_mute.setObjectName("muteButton")
            btn_mute.setIcon(QIcon(resource_path("assets/icons/mute.svg")))
            btn_mute.setCheckable(True)
            btn_mute.setChecked(True)
            # Funkce pro přepnutí zvuku a ikony
            def toggle_mute(muted):
                if self.web_view:
                    url = self.web_view.url().toString()
                    if muted:
                        self.web_view.page().setAudioMuted(True)
                    else:
                        new_url = url.replace("mute=1", "mute=0")
                        self.web_view.setUrl(QUrl(new_url))
                        self.web_view.page().setAudioMuted(False)
                    icon_path = resource_path("assets/icons/mute.svg") if muted else resource_path("assets/icons/unmute.svg")
                    btn_mute.setIcon(QIcon(icon_path))

            btn_mute.toggled.connect(toggle_mute)
            controls_layout.addWidget(btn_mute)

        main_layout.addLayout(controls_layout)

        # Informační sekce
        rating_widget = ClickableStarFilter()
        rating_widget.setRating(self.film_data.get('rating', 0))
        main_layout.addWidget(rating_widget, 0, Qt.AlignmentFlag.AlignCenter)

        country_label = QLabel(f"<b>{self.tr('Země:')}</b> {self.film_data.get('country', 'N/A')}")
        country_label.setObjectName("backSideLabel")
        main_layout.addWidget(country_label)

        genres_text = self.film_data.get('genres', '')
        if genres_text:
            genre_layout = FlowLayout(spacing=5)
            for genre in genres_text.split(','):
                genre_tag = TagButton(genre.strip())
                genre_tag.setEnabled(False)
                genre_layout.addWidget(genre_tag)
            main_layout.addLayout(genre_layout)

        # Popis filmu
        overview = QTextEdit()
        overview.setObjectName("overviewText")
        overview.setText(self.film_data.get('overview', self.tr('Popis není k dispozici.')))
        overview.setReadOnly(True)
        main_layout.addWidget(overview, stretch=1)

        # Tlačítka Upravit a Smazat
        edit_delete_layout = QHBoxLayout()
        btn_edit = QPushButton(self.tr("Upravit"))
        btn_delete = QPushButton(self.tr("Smazat"))
        edit_delete_layout.addStretch()
        edit_delete_layout.addWidget(btn_edit)
        edit_delete_layout.addWidget(btn_delete)
        main_layout.addLayout(edit_delete_layout)

        # Slovník interaktivních prvků pro hlavní okno
        interactive_widgets = {
            "rating_widget": rating_widget,
            "edit_button": btn_edit,
            "delete_button": btn_delete
        }
        return back_widget, interactive_widgets

    def update_data(self, film_data, select_mode=False):
        self.film_data = film_data

        new_title = film_data.get("title", "???")
        if self.title_label.text() != new_title:
            self.title_label.setText(new_title)

        new_year = str(film_data.get("year", ""))
        if self.year_label.text() != new_year:
            self.year_label.setText(new_year)

        pixmap_path = resource_path(film_data.get("poster") or get_placeholder_poster())
        pix = QPixmap(pixmap_path).scaled(
            175, 225,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.poster_label.setPixmap(pix)

        self.rating_widget.setRating(film_data.get("rating", 0))

        if self.select_mode != select_mode:
            self.select_mode = select_mode
            self.checkbox.setVisible(self.select_mode)
            self.checkbox.setChecked(False)

