# library_window.py

import getpass
import os
from glob import glob
import sqlite3

from PyQt6.QtCore import Qt, pyqtSignal, QPointF, QRectF
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QGridLayout, QScrollArea, QFileDialog, QCheckBox, QGraphicsDropShadowEffect, QListWidget, QApplication, QFrame
)
from PyQt6.QtGui import QPixmap, QCursor, QColor, QFont, QScreen, QPainter, QPen, QPolygonF, QBrush

PLACEHOLDER_POSTER = "assets/icons/KingPlayer6.png"
SUPPORTED_EXTS = ('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mpg', '.mpeg')


class DatabaseManager:
    # ... (beze změny)
    def __init__(self, db_name="king_player_library.db"):
        self.conn = sqlite3.connect(db_name);
        self.conn.row_factory = sqlite3.Row;
        self.cursor = self.conn.cursor();
        self.create_tables()

    def create_tables(self):
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS films (filepath TEXT PRIMARY KEY, title TEXT, year TEXT, rating REAL, poster TEXT, overview TEXT, genres TEXT, runtime INTEGER)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS library_paths (path TEXT PRIMARY KEY)");
        self.conn.commit()

    def add_or_update_film(self, film_data):
        self.cursor.execute(
            "INSERT OR REPLACE INTO films (filepath, title, year, rating, poster) VALUES (?, ?, ?, ?, ?)",
            (film_data.get('filepath'), film_data.get('title'), film_data.get('year'),
             float(film_data.get('rating', 0)), film_data.get('poster')));
        self.conn.commit()

    def delete_film(self, filepath):
        self.cursor.execute("DELETE FROM films WHERE filepath = ?", (filepath,));
        self.conn.commit()

    def get_all_films(self):
        self.cursor.execute("SELECT * FROM films");
        return [dict(row) for row in self.cursor.fetchall()]

    def add_library_path(self, path):
        self.cursor.execute("INSERT OR IGNORE INTO library_paths (path) VALUES (?)", (path,));
        self.conn.commit()

    def remove_library_path(self, path):
        self.cursor.execute("DELETE FROM library_paths WHERE path = ?", (path,));
        self.conn.commit()

    def get_library_paths(self):
        self.cursor.execute("SELECT path FROM library_paths");
        return [row['path'] for row in self.cursor.fetchall()]

    def close(self): self.conn.close()


### NOVÝ, SPOLEHLIVÝ SYSTÉM HVĚZD S VLASTNÍM KRESLENÍM ###
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
            star.setEnabled(False)  # Jen pro zobrazení, nereaguje na klik
            layout.addWidget(star)
            self.star_widgets.append(star)

    def setRating(self, rating):
        val = round(float(rating) * 2) / 2
        for i, star_widget in enumerate(self.star_widgets):
            value = max(0.0, min(1.0, val - i))
            star_widget.setValue(value)


# --- OSTATNÍ TŘÍDY JSOU BEZE ZMĚNY ---
class FilmCard(QFrame):
    def __init__(self, film_data, select_mode=False, checked=False, parent=None):
        super().__init__(parent)
        self.film_data = film_data
        self.setFixedSize(225, 360)
        self.setObjectName("filmCardContainer")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        card_layout = QVBoxLayout(self)
        card_layout.setContentsMargins(3, 3, 3, 3)
        content_widget = QWidget(self)
        content_widget.setObjectName("filmCardContent")
        card_layout.addWidget(content_widget)
        main_vbox = QVBoxLayout(content_widget)
        main_vbox.setContentsMargins(12, 12, 12, 12)
        main_vbox.setSpacing(10)
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(checked)
        self.checkbox.setVisible(select_mode)
        main_vbox.addWidget(self.checkbox, alignment=Qt.AlignmentFlag.AlignLeft)
        main_vbox.addStretch(1)
        self.title_label = QLabel(film_data.get("title", "???"))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setWordWrap(True)
        self.title_label.setFixedHeight(48)
        main_vbox.addWidget(self.title_label)
        self.poster_label = QLabel()
        self.poster_label.setFixedSize(175, 225)
        self.poster_label.setScaledContents(True)
        pix = QPixmap(film_data.get("poster", PLACEHOLDER_POSTER)).scaled(175, 225, Qt.AspectRatioMode.KeepAspectRatio,
                                                                          Qt.TransformationMode.SmoothTransformation)
        self.poster_label.setPixmap(pix)
        main_vbox.addWidget(self.poster_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.rating_widget = StarRatingDisplay()
        self.rating_widget.setRating(film_data.get("rating", 0))
        main_vbox.addWidget(self.rating_widget)
        main_vbox.addStretch(1)
        shadow = QGraphicsDropShadowEffect(content_widget)
        shadow.setBlurRadius(28)
        shadow.setColor(QColor("#16e0ec88"))
        shadow.setOffset(0, 0)
        content_widget.setGraphicsEffect(shadow)
        font = self.title_label.font()
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 0.4)
        self.title_label.setFont(font)


class LibraryWindow(QWidget):
    def __init__(self, player_window=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Královská knihovna filmů – The King's Player")
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        self.player_window = player_window
        self.select_mode = False
        self.card_widgets = []
        self.db = DatabaseManager()
        self.setup_ui()
        self.setup_connections()
        self.load_films_from_db()
        self.load_library_paths_from_db()
        self.move_to_center_of_parent()

        QApplication.restoreOverrideCursor()
        self.setMouseTracking(True)

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(8)
        self.setStyleSheet(self.get_stylesheet())
        self.filter_panel = QWidget()
        filter_layout = QVBoxLayout(self.filter_panel)
        filter_layout.setContentsMargins(10, 20, 10, 10)
        filter_layout.setSpacing(14)
        self.title_filter = QLineEdit()
        self.title_filter.setPlaceholderText("Název filmu...")
        self.year_filter_from = QLineEdit()
        self.year_filter_from.setPlaceholderText("Rok od")
        self.year_filter_to = QLineEdit()
        self.year_filter_to.setPlaceholderText("Rok do")
        self.rating_filter = ClickableStarFilter()  # Použije finální verzi hvězd
        self.length_filter = QLineEdit()
        self.length_filter.setPlaceholderText("Délka (min)...")
        self.country_filter = QLineEdit()
        self.country_filter.setPlaceholderText("Země původu...")
        self.genre_filter = QLineEdit()
        self.genre_filter.setPlaceholderText("Žánry (čárkou)...")
        self.library_paths_list = QListWidget()
        self.btn_add_path = QPushButton("Přidat složku")
        self.btn_remove_path = QPushButton("Odebrat složku")
        self.btn_scan_paths = QPushButton("Prohledat knihovnu")
        self.btn_select_mode = QPushButton("Označit filmy")
        self.btn_toggle_fullscreen = QPushButton("Režim okno/fullscreen")
        self.btn_import = QPushButton("Nahrát data k filmům")
        self.btn_add_files = QPushButton("Přidat vybrané soubory")
        self.btn_remove = QPushButton("Odebrat vybrané")
        self.btn_back = QPushButton("Zpět na přehrávač")
        for widget in [QLabel("Filtry:"), self.title_filter, self.year_filter_from, self.year_filter_to,
                       QLabel("Minimální hodnocení:"), self.rating_filter, self.length_filter, self.country_filter,
                       self.genre_filter, QLabel("Knihovní složky:"), self.library_paths_list, self.btn_add_path,
                       self.btn_remove_path, self.btn_scan_paths, self.btn_toggle_fullscreen, self.btn_import,
                       self.btn_add_files, self.btn_select_mode, self.btn_remove]:
            filter_layout.addWidget(widget)
        filter_layout.addStretch(1)
        filter_layout.addWidget(self.btn_back)
        grid_panel = QWidget()
        self.grid_layout = QGridLayout(grid_panel)
        self.grid_layout.setSpacing(12)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(grid_panel)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        main_layout.addWidget(scroll, stretch=6)
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
        self.films = self.all_films[:]
        self.refresh_grid()

    def load_library_paths_from_db(self):
        self.library_paths_list.clear()
        paths = self.db.get_library_paths()
        self.library_paths_list.addItems(paths)

    def apply_filters(self):
        min_rating = self.rating_filter._rating
        title_text = self.title_filter.text().lower()

        # Projdeme všechny karty, které jsme si vytvořili při startu
        for card in self.card_widgets:
            film_data = card.film_data

            # Zkontrolujeme, zda film splňuje podmínky
            rating_ok = float(film_data.get('rating', 0)) >= min_rating
            title_ok = (not title_text) or (title_text in film_data.get('title', '').lower())

            if rating_ok and title_ok:
                card.show()
            else:
                card.hide()

    def refresh_grid(self):
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().deleteLater()
        self.card_widgets = []
        for idx, film in enumerate(self.films):
            row, col = divmod(idx, 5)
            card = FilmCard(film, select_mode=self.select_mode)
            self.grid_layout.addWidget(card, row, col)
            self.card_widgets.append(card)

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
        if not self.select_mode:
            return
        checkboxes = [card.checkbox for card in self.card_widgets]
        indices_to_delete = [i for i, cb in enumerate(checkboxes) if cb.isChecked()]
        if not indices_to_delete:
            return
        for i in sorted(indices_to_delete, reverse=True):
            self.db.delete_film(self.films[i]['filepath'])
        self.toggle_select_mode()
        self.load_films_from_db()

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

    def get_stylesheet(self):
        return """
            QWidget { background: rgba(34, 43, 66, 230); color: #eafff7; font-family: Segoe UI, Arial; font-size: 15px; }
            QScrollArea { border: none; background: transparent; }
            QLabel { background: transparent; }
            QLineEdit { background: #232941; border-radius: 8px; border: 1.5px solid #181a1f; padding: 5px; }
            QPushButton { background: qradialgradient(cx:0.5, cy:0.5, radius:0.8, stop:0 #283950, stop:1 #2d3950);
                          border-radius: 14px; border: 1.2px solid #20ffe988; color: #eafff7; font-weight: bold; min-height: 30px; padding: 4px; }
            QPushButton:hover { background: qradialgradient(cx:0.5, cy:0.5, radius:0.7, stop:0 #41ffe7, stop:1 #162c2c);
                               border: 1.8px solid #22ffc6; color: #000000; }
            #filmCardContainer { background-color: transparent; border-radius: 38px; border: 3px solid #00fff7; margin: 10px; }
            #filmCardContent { background-color: #2d3950; border-radius: 35px; }
            #titleLabel { color: #fff; font-size: 18px; font-weight: 600; }
        """