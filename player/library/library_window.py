import datetime
import os
from glob import glob
import sqlite3

from PyQt6.QtCore import Qt, pyqtSignal, QPointF, QRectF, QObject, QThread, QSize, QTimer, QPropertyAnimation, QRect, \
    QEasingCurve, QPoint, pyqtProperty, QVariantAnimation
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QGridLayout, QScrollArea, QFileDialog, QCheckBox, QGraphicsDropShadowEffect, QListWidget, QApplication, QFrame,
    QListWidgetItem, QListView, QGraphicsOpacityEffect, QStackedWidget
)
from PyQt6.QtGui import QPixmap, QCursor, QColor, QFont, QScreen, QPainter, QPen, QPolygonF, QBrush

from player.library.flow_layout import FlowLayout

PLACEHOLDER_POSTER = "assets/icons/KingPlayer6.png"
SUPPORTED_EXTS = ('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mpg', '.mpeg')
ALL_GENRES = (
    "Akční", "Dobrodružný", "Komedie", "Drama", "Fantasy", "Horor",
    "Sci-Fi", "Thriller", "Mysteriózní", "Romantický", "Animovaný",
    "Rodinný", "Krimi", "Válečný", "Historický", "Hudební", "Western"
)

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
        self.setProperty("active", checked) # Pro CSS stylování
        self.style().polish(self) # Aplikuje nový styl
        self.stateChanged.emit(checked)

class DatabaseManager:
    def __init__(self, db_name="king_player_library.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS films (filepath TEXT PRIMARY KEY, title TEXT, year TEXT, rating REAL, poster TEXT, overview TEXT, genres TEXT, runtime INTEGER)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS library_paths (path TEXT PRIMARY KEY)")
        self.conn.commit()

    def add_or_update_film(self, film_data):
        self.cursor.execute(
            "INSERT OR REPLACE INTO films (filepath, title, year, rating, poster) VALUES (?, ?, ?, ?, ?)",
            (film_data.get('filepath'), film_data.get('title'), film_data.get('year'),
             float(film_data.get('rating', 0)), film_data.get('poster')))
        self.conn.commit()

    def delete_film(self, filepath):
        self.cursor.execute("DELETE FROM films WHERE filepath = ?", (filepath,));
        self.conn.commit()

    def delete_films(self, filepaths):
        data_to_delete = [(path,) for path in filepaths]
        self.cursor.executemany("DELETE FROM films WHERE filepath = ?", data_to_delete)
        self.conn.commit()

    def get_all_films(self):
        self.cursor.execute("SELECT * FROM films")
        return [dict(row) for row in self.cursor.fetchall()]

    def add_library_path(self, path):
        self.cursor.execute("INSERT OR IGNORE INTO library_paths (path) VALUES (?)", (path,))
        self.conn.commit()

    def remove_library_path(self, path):
        self.cursor.execute("DELETE FROM library_paths WHERE path = ?", (path,))
        self.conn.commit()

    def get_library_paths(self):
        self.cursor.execute("SELECT path FROM library_paths")
        return [row['path'] for row in self.cursor.fetchall()]

    def close(self): self.conn.close()

class ClickableStar(QWidget):
    valueChanged = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(40, 40)  # Velikost hvězdy
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
            # Vypočítáme hodnotu pro každou hvězdu (0, 0.5, nebo 1)
            value = max(0.0, min(1.0, self._rating - i))
            star.setValue(value)


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


class FilmCard(QFrame):
    hover_triggered = pyqtSignal(bool, 'QVariant')

    def __init__(self, film_data, parent=None):
        super().__init__(parent)
        self.film_data = film_data
        self.select_mode = False

        # --- NOVÁ ČÁST S QStackedWidget ---
        self.stacked_widget = QStackedWidget(self)
        self.front_widget = self._create_front_widget()
        self.back_widget = self._create_back_widget()
        self.stacked_widget.addWidget(self.front_widget)
        self.stacked_widget.addWidget(self.back_widget)

        # Hlavní layout, který drží jen náš QStackedWidget
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.stacked_widget)
        # --- KONEC NOVÉ ČÁSTI ---

        self.setObjectName("filmCardContainer")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFixedSize(225, 360)

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
        """Přepne mezi přední (index 0) a zadní (index 1) stranou."""
        new_index = 1 - self.stacked_widget.currentIndex()
        self.stacked_widget.setCurrentIndex(new_index)

    def show_front(self):
        """Explicitně ukáže přední stranu."""
        self.stacked_widget.setCurrentIndex(0)

    def _create_front_widget(self):
        """Vytvoří a vrátí widget pro přední stranu (beze změny)."""
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
        """Vytvoří a vrátí widget pro zadní stranu (beze změny)."""
        widget = QWidget()
        widget.setObjectName("filmCardContent")
        layout = QVBoxLayout(widget)
        label = QLabel("TOTO JE ZADNÍ STRANA\n\n- Trailer\n- Popis\n- Hodnocení")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("background: #1c2538; color: white;") # Pro testování
        layout.addWidget(label)
        return widget

    def update_data(self, film_data, select_mode=False):
        """Aktualizuje data na kartě (beze změny)."""
        self.film_data = film_data
        self.title_label.setText(film_data.get("title", "???"))
        pix = QPixmap(self.film_data.get("poster", PLACEHOLDER_POSTER)).scaled(175, 225,
                                                                               Qt.AspectRatioMode.KeepAspectRatio,
                                                                               Qt.TransformationMode.SmoothTransformation)
        self.poster_label.setPixmap(pix)
        self.rating_widget.setRating(film_data.get("rating", 0))
        self.select_mode = select_mode
        self.checkbox.setVisible(self.select_mode)
        self.checkbox.setChecked(False)


class LibraryWindow(QWidget):
    def __init__(self, player_window=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Královská knihovna filmů – The King's Player")
        self.setWindowState(Qt.WindowState.WindowFullScreen)

        self.player_window = player_window
        self.select_mode = False
        self.card_widgets = []
        self.all_films = []
        self.films = []

        self.animation_container = None
        self.animated_card = None
        self.original_card = None
        self.active_hover_card = None
        self.original_fonts = {}
        self.queued_card = None

        self.scale_animation = None

        self.hover_enter_timer = QTimer(self)
        self.hover_enter_timer.setSingleShot(True)
        self.hover_enter_timer.setInterval(250)  # Zpoždění 250ms
        self.hover_enter_timer.timeout.connect(self._animate_card_in)

        self.filter_debounce_timer = QTimer(self)
        self.filter_debounce_timer.setSingleShot(True)
        self.filter_debounce_timer.setInterval(250)
        self.hover_enter_timer.timeout.connect(self._animate_card_in)

        self.db = DatabaseManager()
        self.setup_ui()
        self.setup_connections()
        self.load_films_from_db()
        self.load_library_paths_from_db()
        self.move_to_center_of_parent()

        QApplication.restoreOverrideCursor()
        self.setMouseTracking(True)

    def setup_ui(self):
        # --- Základní layout okna (zůstává stejný) ---
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(8)
        self.setStyleSheet(self.get_stylesheet())

        # --- Hlavní panel s filtry (zcela nová struktura) ---
        self.filter_panel = QWidget()
        self.filter_panel.setObjectName("filterPanel")
        filter_layout = QVBoxLayout(self.filter_panel)
        filter_layout.setContentsMargins(10, 15, 10, 15)
        filter_layout.setSpacing(20)  # Větší mezery mezi hlavními bloky

        # --- Blok 1: Rychlé filtry ---
        filter_layout.addWidget(QLabel("Základní filtry"))
        fast_filters_group = QFrame(self)
        fast_filters_group.setObjectName("groupBox")
        fast_filters_layout = QVBoxLayout(fast_filters_group)

        self.title_filter = QLineEdit()
        self.title_filter.setPlaceholderText("Hledat podle názvu...")
        fast_filters_layout.addWidget(self.title_filter)

        fast_filters_layout.addWidget(QLabel("Minimální hodnocení:"))
        self.rating_filter = ClickableStarFilter()
        fast_filters_layout.addWidget(self.rating_filter, alignment=Qt.AlignmentFlag.AlignCenter)

        filter_layout.addWidget(fast_filters_group)

        # --- Blok 2: Pokročilé filtry ---
        filter_layout.addWidget(QLabel("Pokročilé filtry"))
        adv_filters_group = QFrame(self)
        adv_filters_group.setObjectName("groupBox")
        adv_filters_layout = QVBoxLayout(adv_filters_group)

        # Rok vydání (vedle sebe)
        year_layout = QHBoxLayout()
        self.year_filter_from = QLineEdit()
        self.year_filter_from.setPlaceholderText("Rok od")
        self.year_filter_to = QLineEdit()
        self.year_filter_to.setPlaceholderText(f"Rok do ({datetime.date.today().year})")
        year_layout.addWidget(self.year_filter_from)
        year_layout.addWidget(QLabel("–"))
        year_layout.addWidget(self.year_filter_to)
        adv_filters_layout.addLayout(year_layout)

        # Ostatní filtry (zatím jako původní QLineEdit)
        self.length_filter = QLineEdit()
        self.length_filter.setPlaceholderText("Délka (min)...")
        adv_filters_layout.addWidget(self.length_filter)

        self.country_filter = QLineEdit()
        self.country_filter.setPlaceholderText("Země původu...")
        adv_filters_layout.addWidget(self.country_filter)

        adv_filters_layout.addWidget(QLabel("Žánry:"))
        self.genre_layout = FlowLayout(spacing=8)  # Použijeme náš nový layout
        self.genre_buttons = {}  # Slovník pro snadný přístup k tlačítkům

        for genre in ALL_GENRES:
            button = TagButton(genre)
            button.stateChanged.connect(self.apply_filters)  # Napojíme na filtr
            self.genre_layout.addWidget(button)
            self.genre_buttons[genre] = button

        adv_filters_layout.addLayout(self.genre_layout)
        filter_layout.addWidget(adv_filters_group)

        # --- Blok 3: Správa Knihovny ---
        filter_layout.addWidget(QLabel("Správa knihovny"))
        library_group = QFrame(self)
        library_group.setObjectName("groupBox")
        library_layout = QVBoxLayout(library_group)

        self.library_paths_list = QListWidget()
        library_layout.addWidget(self.library_paths_list)

        path_buttons_layout = QHBoxLayout()
        self.btn_add_path = QPushButton("Přidat složku")
        self.btn_remove_path = QPushButton("Odebrat")
        path_buttons_layout.addWidget(self.btn_add_path)
        path_buttons_layout.addWidget(self.btn_remove_path)
        library_layout.addLayout(path_buttons_layout)

        self.btn_scan_paths = QPushButton("Prohledat knihovnu")
        library_layout.addWidget(self.btn_scan_paths)

        filter_layout.addWidget(library_group)

        # --- Blok 4: Akce a Nastavení ---
        filter_layout.addWidget(QLabel("Akce s filmy"))
        actions_group = QFrame(self)
        actions_group.setObjectName("groupBox")
        actions_layout = QGridLayout(actions_group)  # GridLayout pro úhledné rozmístění 2x2

        self.btn_select_mode = QPushButton("Označit filmy")
        self.btn_add_files = QPushButton("Přidat soubory")
        self.btn_import = QPushButton("Nahrát data")
        self.btn_remove = QPushButton("Odebrat vybrané")

        actions_layout.addWidget(self.btn_select_mode, 0, 0)
        actions_layout.addWidget(self.btn_add_files, 0, 1)
        actions_layout.addWidget(self.btn_import, 1, 0)
        actions_layout.addWidget(self.btn_remove, 1, 1)

        filter_layout.addWidget(actions_group)

        # --- Ukončení ---
        filter_layout.addStretch(1)  # Odsune zbytek úplně dolů

        bottom_buttons_layout = QHBoxLayout()
        self.btn_toggle_fullscreen = QPushButton("Fullscreen")
        self.btn_back = QPushButton("Zpět na přehrávač")
        bottom_buttons_layout.addWidget(self.btn_toggle_fullscreen)
        bottom_buttons_layout.addWidget(self.btn_back)

        filter_layout.addLayout(bottom_buttons_layout)

        # --- Mřížka s filmy (zůstává stejná) ---
        grid_panel = QWidget()
        self.grid_layout = QGridLayout(grid_panel)
        self.grid_layout.setSpacing(12)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(grid_panel)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # --- Finální sestavení okna ---
        main_layout.addWidget(scroll, stretch=5)  # Dal jsem filmům trochu víc místa
        main_layout.addWidget(self.filter_panel, stretch=2)

    def setup_connections(self):
        self.btn_add_path.clicked.connect(self.add_library_path)
        self.btn_remove_path.clicked.connect(self.remove_library_path)
        self.btn_scan_paths.clicked.connect(self.scan_library_paths)
        self.btn_toggle_fullscreen.clicked.connect(self.toggle_fullscreen)
        self.btn_add_files.clicked.connect(self.add_selected_files)
        self.btn_select_mode.clicked.connect(self.toggle_select_mode)
        self.btn_back.clicked.connect(self.back_to_player)
        self.btn_remove.clicked.connect(self.remove_selected_films)
        self.rating_filter.ratingChanged.connect(self.apply_filters)
        self.title_filter.textChanged.connect(self.apply_filters)
        self.btn_import.clicked.connect(self.on_import_button_clicked)
        self.year_filter_from.textChanged.connect(self.apply_filters)
        self.year_filter_to.textChanged.connect(self.apply_filters)
        self.filter_debounce_timer.timeout.connect(self._execute_filters)

    def on_import_button_clicked(self):
        print("Funkce pro import dat bude implementována později.")

    def move_to_center_of_parent(self):
        parent = self.player_window
        if parent is not None:
            parent_geom = parent.geometry()
            my_geom = self.geometry()
            x = parent_geom.x() + (parent_geom.width() - my_geom.width()) // 2
            y = parent_geom.y() + (parent_geom.height() - my_geom.height()) // 2
            self.move(x, y)
        else:
            screen_geometry = self.screen().availableGeometry()
            self.move((screen_geometry.width() - self.width()) // 2, (screen_geometry.height() - self.height()) // 2)

    def load_films_from_db(self):
        self.all_films = self.db.get_all_films()
        self.apply_filters()

    def load_library_paths_from_db(self):
        self.library_paths_list.clear()
        paths = self.db.get_library_paths()
        self.library_paths_list.addItems(paths)

    def _execute_filters(self):
        # --- 1. Získáme hodnoty VŠECH filtrů JEN JEDNOU ---
        title_text = self.title_filter.text().lower()
        min_rating = self.rating_filter._rating
        try:
            year_from = int(self.year_filter_from.text())
        except ValueError:
            year_from = 0
        try:
            year_to = int(self.year_filter_to.text())
        except ValueError:
            year_to = datetime.date.today().year + 1

        # Zjistíme aktivní žánry PŘED cyklem
        selected_genres = {genre for genre, button in self.genre_buttons.items() if button.isActive()}

        # --- 2. Filtrujeme filmy ---
        filtered_films = []
        for film_data in self.all_films:
            # Podmínky pro title a rating
            title_ok = not title_text or title_text in film_data.get('title', '').lower()
            rating_ok = float(film_data.get('rating', 0)) >= min_rating

            # Podmínka pro rok
            film_year_str = film_data.get('year', '0')
            film_year = int(film_year_str) if film_year_str.isdigit() else 0
            year_ok = year_from <= film_year <= year_to

            # ZDE JE OPRAVENÁ A DOPLNĚNÁ LOGIKA PRO ŽÁNRY
            genre_ok = True
            if selected_genres:  # Tuto kontrolu děláme, jen pokud je nějaký žánr vybrán
                film_genres_str = film_data.get('genres') or ''
                film_genres = set(g.strip() for g in film_genres_str.split(','))
                if film_genres.isdisjoint(selected_genres):
                    genre_ok = False

            # Pokud vše platí, film přidáme
            if title_ok and rating_ok and year_ok and genre_ok:
                filtered_films.append(film_data)

        # --- 3. Aktualizujeme UI (logika s recyklací widgetů) ---
        self.films = filtered_films
        num_needed = len(self.films)
        num_available = len(self.card_widgets)

        for i in range(num_needed):
            film_data = self.films[i]
            if i < num_available:
                card = self.card_widgets[i]
                card.update_data(film_data, self.select_mode)
                card.show()

            else:
                row, col = divmod(i, 5)
                card = FilmCard(film_data)
                card.select_mode = self.select_mode
                card.hover_triggered.connect(self.on_card_hover_event)
                self.grid_layout.addWidget(card, row, col)
                self.card_widgets.append(card)

        for i in range(num_needed, num_available):
            self.card_widgets[i].hide()

    def apply_filters(self):
        self.filter_debounce_timer.start()


    def add_films_to_library(self, film_list):
        new_films_added = False
        current_filepaths = {f['filepath'] for f in self.all_films}
        for f in film_list:
            if f not in current_filepaths:
                film_data = {"title": os.path.splitext(os.path.basename(f))[0], "year": "", "rating": 0,
                             "poster": PLACEHOLDER_POSTER, "filepath": f}
                self.db.add_or_update_film(film_data)
                new_films_added = True
        if new_films_added:
            self.load_films_from_db()

    def add_selected_files(self):
        filepaths, _ = QFileDialog.getOpenFileNames(self, "Vyber filmy", os.path.expanduser("~"),
                                                    f"Video soubory ({' '.join(['*' + ext for ext in SUPPORTED_EXTS])})")
        if filepaths:
            self.add_films_to_library(filepaths)

    def scan_library_paths(self):
        all_files = []
        for i in range(self.library_paths_list.count()):
            dirpath = self.library_paths_list.item(i).text()
            for ext in SUPPORTED_EXTS:
                all_files.extend(glob(os.path.join(dirpath, f"**/*{ext}"), recursive=True))
        if all_files:
            self.add_films_to_library(all_files)

    def remove_selected_films(self):
        if not self.select_mode: return

        films_to_delete = [card.film_data for card in self.card_widgets if card.checkbox.isChecked()]
        if not films_to_delete: return

        filepaths_to_delete = [film['filepath'] for film in films_to_delete]

        self.btn_remove.setEnabled(False)
        self.btn_remove.setText("Mažu...")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        self.thread = QThread()
        self.worker = DeleteWorker(self.db.db_name, filepaths_to_delete)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.finished.connect(lambda: self.on_delete_finished(filepaths_to_delete))

        self.thread.start()

    def on_delete_finished(self, deleted_filepaths):
        QApplication.restoreOverrideCursor()
        self.btn_remove.setEnabled(True)
        self.btn_remove.setText("Odebrat vybrané")

        # Aktualizuj data v paměti a překresli UI
        filepaths_set = set(deleted_filepaths)
        self.all_films = [film for film in self.all_films if film['filepath'] not in filepaths_set]

        self.toggle_select_mode()
        self.apply_filters()

    def add_library_path(self):
        dirpath = QFileDialog.getExistingDirectory(self, "Vyber složku pro knihovnu", os.path.expanduser("~"))
        if dirpath:
            items = [self.library_paths_list.item(i).text() for i in range(self.library_paths_list.count())]
            if dirpath not in items:
                self.library_paths_list.addItem(dirpath)
                self.db.add_library_path(dirpath)

    def remove_library_path(self):
        selected_items = self.library_paths_list.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            self.db.remove_library_path(item.text())
            self.library_paths_list.takeItem(self.library_paths_list.row(item))

    def toggle_select_mode(self):
        self.select_mode = not self.select_mode
        for card in self.card_widgets:
            if card.isVisible():  # Ovlivníme jen viditelné karty
                card.select_mode = self.select_mode
                card.checkbox.setVisible(self.select_mode)

    def toggle_fullscreen(self):
        self.setWindowState(Qt.WindowState.WindowNoState if self.isFullScreen() else Qt.WindowState.WindowFullScreen)

    def back_to_player(self):
        self.db.close()
        if self.player_window:
            self.player_window.show()
            self.close()
        else:
            self.close()

    # V TŘÍDĚ LibraryWindow - PŘEPIŠ CELOU SADU ANIMAČNÍCH METOD

    def on_card_hover_event(self, entered, card):
        """Reaguje na signál z karty."""
        if entered:
            # Pokud je nějaká karta otevřená a najedeme na jinou
            if self.animation_container and self.original_card and self.original_card != card:
                # Dáme novou kartu do "fronty" a spustíme zavírání té staré.
                self.queued_card = card
                self._animate_card_out()
            # Pokud nic není otevřené, spustíme časovač pro otevření.
            elif not self.animation_container:
                self.active_hover_card = card
                self.hover_enter_timer.start()
        else:
            # Při opuštění malé karty zastavíme časovač
            self.hover_enter_timer.stop()

    def _animate_card_in(self):
        """Spustí animaci interaktivního widgetu."""
        if self.animation_container or not self.active_hover_card:
            return

        self.original_card = self.active_hover_card
        self.original_card.setOpacity(0.0)

        self.animation_container = AnimatedContainer(self)
        self.animation_container.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip)
        self.animation_container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.animation_container.setStyleSheet("""
            AnimatedContainer {
                background-color: #2d3950;
                border-radius: 38px;
                border: 3px solid #00fff7;
            }
        """)
        self.animation_container.mouse_left.connect(self._animate_card_out)

        self.animated_card = self.original_card._create_back_widget()
        container_layout = QVBoxLayout(self.animation_container)
        container_layout.setContentsMargins(15, 15, 15, 15)
        container_layout.addWidget(self.animated_card)

        self.original_fonts = {
            widget: widget.font()
            for widget in self.animated_card.findChildren(QWidget) if hasattr(widget, 'font')
        }

        self.start_geometry = QRect(self.original_card.mapToGlobal(QPoint(0, 0)), self.original_card.size())
        self.scale_factor = 2.8

        if not self.scale_animation:
            self.scale_animation = QVariantAnimation(self)
            self.scale_animation.setDuration(350)
            self.scale_animation.setEasingCurve(QEasingCurve.Type.InOutQuart)
            self.scale_animation.valueChanged.connect(self._update_animation_frame)

        try:
            self.scale_animation.finished.disconnect()
        except TypeError:
            pass

        self.scale_animation.setStartValue(1.0)
        self.scale_animation.setEndValue(self.scale_factor)
        self.scale_animation.setDirection(QPropertyAnimation.Direction.Forward)

        self.animation_container.show()
        self.scale_animation.start()

    def _update_animation_frame(self, scale):
        """Tato funkce se volá pro každý snímek animace, nyní je chytřejší."""
        if not self.animation_container: return

        # Výpočet geometrie zůstává stejný
        w = self.start_geometry.width() * scale
        h = self.start_geometry.height() * scale
        x = self.start_geometry.x() - (w - self.start_geometry.width()) / 2
        y = self.start_geometry.y() - (h - self.start_geometry.height()) / 2
        self.animation_container.setGeometry(int(x), int(y), int(w), int(h))

        # --- OPRAVENÁ LOGIKA PRO PÍSMO ---
        for widget, original_font in self.original_fonts.items():
            if not widget: continue  # Pojistka, kdyby widget mezitím zmizel

            scaled_font = QFont(original_font)

            # Zjistíme, jestli font používá body nebo pixely
            if original_font.pointSizeF() > 0:
                new_size = original_font.pointSizeF() * scale
                # Pojistka proti záporným hodnotám
                if new_size > 0.1:
                    scaled_font.setPointSizeF(new_size)
            elif original_font.pixelSize() > 0:
                new_size = original_font.pixelSize() * scale
                if new_size > 1:
                    scaled_font.setPixelSize(int(new_size))

            widget.setFont(scaled_font)

    def _animate_card_out(self):
        """Spustí animaci pro návrat na původní místo."""
        if not self.animation_container:
            return

        # Odpojíme signály, aby se nic nespustilo dvakrát
        try:
            self.animation_container.mouse_left.disconnect()
        except TypeError:
            pass
        try:
            self.scale_animation.finished.disconnect()
        except TypeError:
            pass

        # Po dokončení animace "ven" se VŽDY spustí úklid
        self.scale_animation.finished.connect(self._cleanup_animation)

        self.scale_animation.setDirection(QPropertyAnimation.Direction.Backward)
        self.scale_animation.start()

    def _cleanup_animation(self):
        """Uklidí a případně spustí další animaci z fronty."""
        # Zastavíme běžící animaci
        if self.scale_animation and self.scale_animation.state() == QPropertyAnimation.State.Running:
            self.scale_animation.stop()

        # Uklidíme staré prvky
        if self.animation_container:
            self.animation_container.hide()
            self.animation_container.deleteLater()
            self.animation_container = None

        if self.original_card:
            self.original_card.front_widget.show()
            self.original_card.setOpacity(1.0)

        # Reset stavů
        self.animated_card = None
        self.original_card = None
        self.active_hover_card = None
        self.original_fonts = {}

        if self.scale_animation:
            try:
                self.scale_animation.finished.disconnect()
            except TypeError:
                pass

        # ZDE JE TA MAGIE: Zkontrolujeme frontu
        if self.queued_card:
            # Pokud karta čeká, spustíme pro ni otevírací animaci
            card_to_open = self.queued_card
            self.queued_card = None  # Vyčistíme frontu
            self.active_hover_card = card_to_open
            self.hover_enter_timer.start()

    def get_stylesheet(self):
        return """
            QWidget { background: rgba(34, 43, 66, 230); color: #eafff7; font-family: Segoe UI, Arial; font-size: 15px; }
            QScrollArea { border: none; background: transparent; }
            QLabel { background: transparent; }
            QCheckBox {
                background-color: transparent;
                border: none;
            }
            QCheckBox:focus {
                outline: none; 
            }
            QCheckBox::indicator {
                width: 22px;   /* Větší box */
                height: 22px;
                border-radius: 11px; /* Lehce zakulatíme rohy */
            }
            QCheckBox::indicator:unchecked {
                background-color: #FF0000; 
            }            
            QCheckBox::indicator:checked {
                background-color: #1cf512; /* Pozadí se vyplní tyrkysovou */
                image: url(assets/icons/checkmark.svg); /* Ikonka fajfky (pokud ji máš) */
            }            
            QCheckBox::indicator:hover {
                border: 2px solid #00fff7; /* Při najetí myší okraj ještě více zesvětlí */
            }
            #filterPanel {
                background-color: #232941; /* Lehce odlišené pozadí panelu */
            }
            
            /* Hlavní styl pro seskupovací boxy */
            #groupBox {
                background-color: rgba(0, 0, 0, 0.15);
                border: 1px solid #3a4a63;
                border-radius: 10px;
                padding: 8px;
            }
            
            /* Hlavní nadpisy pro jednotlivé sekce */
            #filterPanel > QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #00fff7; /* Zářivá tyrkysová */
                margin-top: 5px;
                margin-bottom: 2px; /* Přisune box blíže k nadpisu */
                padding-left: 5px;
            }
            
            /* Menší nadpisy uvnitř boxů */
            #groupBox > QLabel {
                font-weight: normal;
                color: #eafff7;
                font-size: 14px;
            }
            
            TagButton {
                background-color: #2d3950;
                border: 1px solid #3a4a63;
                border-radius: 13px; /* Kulaté rohy */
                padding: 5px 12px;
                font-size: 13px;
                color: #a9b8d4;
            }
            TagButton:hover {
                border-color: #16e0ec;
            }
            TagButton[active="true"] { /* Styl pro aktivní štítek */
                background-color: #16e0ec;
                border-color: #00fff7;
                color: #000;
                font-weight: bold;
            }
            QLineEdit { background: #232941; border-radius: 8px; border: 1.5px solid #181a1f; padding: 5px; }
            QPushButton { background: qradialgradient(cx:0.5, cy:0.5, radius:0.8, stop:0 #283950, stop:1 #2d3950);
                          border-radius: 14px; border: 1.2px solid #20ffe988; color: #eafff7; font-weight: bold; min-height: 30px; padding: 4px; }
            QPushButton:hover { background: qradialgradient(cx:0.5, cy:0.5, radius:0.7, stop:0 #41ffe7, stop:1 #162c2c);
                               border: 1.8px solid #22ffc6; color: #000000; }
            #filmCardContainer { background-color: transparent; border-radius: 38px; border: 3px solid #00fff7; margin: 10px; }
            #filmCardContent { background-color: #2d3950; border-radius: 35px; }
            #titleLabel { color: #fff; font-size: 18px; font-weight: 600; }
        """


class DeleteWorker(QObject):
    finished = pyqtSignal()
    def __init__(self, db_name, filepaths):
        super().__init__()
        self.db_name = db_name
        self.filepaths = filepaths

    def run(self):
        db = DatabaseManager(self.db_name)
        if self.filepaths:
            db.delete_films(self.filepaths)
        db.close()

        self.finished.emit()