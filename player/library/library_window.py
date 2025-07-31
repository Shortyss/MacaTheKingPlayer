import datetime
import os
from glob import glob


from PyQt6.QtCore import Qt, QThread, QTimer, QPropertyAnimation, QRect, \
    QEasingCurve, QPoint, QVariantAnimation, QSettings, QCoreApplication

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QGridLayout, QScrollArea, QFileDialog, QListWidget, QApplication, QFrame,
     QMessageBox
)

from player.library.api_key_dialog import ApiKeyDialog
from player.library.edit_film_window import EditFilmWindow
from player.library.flow_layout import FlowLayout

from .constants import ALL_GENRES, get_placeholder_poster, SUPPORTED_EXTS
from .custom_widgets import (
    AnimatedContainer, TagButton, ClickableStarFilter
)
from .database_manager import DatabaseManager
from .film_card import FilmCard
from .workers import DataFetchingWorker, DeleteWorker
from .styles import get_main_stylesheet, get_main_stylesheet_fhd

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QFont

def scale_widget_fonts_and_sizes(widget: QWidget, scale_factor: float):
    font = widget.font()
    if font.pointSizeF() > 0:
        font.setPointSizeF(font.pointSizeF() * scale_factor)
        widget.setFont(font)

    min_w = widget.minimumWidth()
    if min_w > 0:
        widget.setMinimumWidth(int(min_w * scale_factor))
    min_h = widget.minimumHeight()
    if min_h > 0:
        widget.setMinimumHeight(int(min_h * scale_factor))

    max_w = widget.maximumWidth()
    if max_w > 0 and max_w != 16777215:
        widget.setMaximumWidth(int(max_w * scale_factor))
    max_h = widget.maximumHeight()
    if max_h > 0 and max_h != 16777215:
        widget.setMaximumHeight(int(max_h * scale_factor))

    # Fixed size
    if widget.minimumWidth() == widget.maximumWidth() and widget.minimumWidth() > 0:
        widget.setFixedWidth(int(widget.minimumWidth() * scale_factor))
    if widget.minimumHeight() == widget.maximumHeight() and widget.minimumHeight() > 0:
        widget.setFixedHeight(int(widget.minimumHeight() * scale_factor))

    # Rekurzivně projdi děti
    for child in widget.findChildren(QWidget):
        scale_widget_fonts_and_sizes(child, scale_factor)


class LibraryWindow(QWidget):
    def __init__(self, player_window=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("The King's Player - library")
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        screen = QApplication.primaryScreen()
        self.width = screen.size().width()

        if self.width <= 1920:
            self.setStyleSheet(get_main_stylesheet_fhd())
        else:
            self.setStyleSheet(get_main_stylesheet())

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
        self.hover_enter_timer.setInterval(250)
        self.hover_enter_timer.timeout.connect(self._animate_card_in)

        self.filter_debounce_timer = QTimer(self)
        self.filter_debounce_timer.setSingleShot(True)
        self.filter_debounce_timer.setInterval(250)
        self.hover_enter_timer.timeout.connect(self._animate_card_in)

        self.db = DatabaseManager()
        self.setup_ui()
        if self.width <= 1920:
            self.library_paths_list.setMaximumHeight(70)
            self.grid_layout.setSpacing(8)
        else:
            self.grid_layout.setSpacing(12)
        self.setup_connections()
        self.load_films_from_db()
        self.load_library_paths_from_db()

        self.move_to_center_of_parent()

        QApplication.restoreOverrideCursor()
        self.setMouseTracking(True)

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        if self.width <= 1920:
            main_layout.setContentsMargins(8, 8, 8, 8)
            main_layout.setSpacing(5)
        else:
            main_layout.setContentsMargins(12, 12, 12, 12)
            main_layout.setSpacing(8)

        # Hlavní panel s filtry
        self.filter_panel = QWidget()
        self.filter_panel.setObjectName("filterPanel")
        filter_layout = QVBoxLayout(self.filter_panel)
        if self.width <= 1920:
            filter_layout.setContentsMargins(6, 9, 6, 9)
            filter_layout.setSpacing(10)
        else:
            filter_layout.setContentsMargins(10, 15, 10, 15)
            filter_layout.setSpacing(20)

        # Blok 1: Rychlé filtry
        filter_layout.addWidget(QLabel(self.tr("Základní filtry")))
        fast_filters_group = QFrame(self)
        fast_filters_group.setObjectName("groupBox")
        fast_filters_layout = QVBoxLayout(fast_filters_group)

        self.title_filter = QLineEdit()
        self.title_filter.setPlaceholderText(self.tr("Hledat podle názvu..."))
        fast_filters_layout.addWidget(self.title_filter)

        fast_filters_layout.addWidget(QLabel(self.tr("Minimální hodnocení:")))
        self.rating_filter = ClickableStarFilter()
        fast_filters_layout.addWidget(self.rating_filter, alignment=Qt.AlignmentFlag.AlignCenter)

        filter_layout.addWidget(fast_filters_group)

        # Blok 2: Pokročilé filtry
        filter_layout.addWidget(QLabel(self.tr("Pokročilé filtry")))
        adv_filters_group = QFrame(self)
        adv_filters_group.setObjectName("groupBox")
        adv_filters_layout = QVBoxLayout(adv_filters_group)

        # Rok vydání (vedle sebe)
        year_layout = QHBoxLayout()
        self.year_filter_from = QLineEdit()
        self.year_filter_from.setPlaceholderText(self.tr("Rok od"))
        self.year_filter_to = QLineEdit()
        self.year_filter_to.setPlaceholderText(f"{self.tr('Rok do')} ({datetime.date.today().year})")
        year_layout.addWidget(self.year_filter_from)
        year_layout.addWidget(QLabel("–"))
        year_layout.addWidget(self.year_filter_to)
        adv_filters_layout.addLayout(year_layout)

        # Ostatní filtry
        adv_filters_layout.addWidget(QLabel(self.tr("Délka:")))
        self.length_layout = FlowLayout(spacing=8)
        self.length_buttons = []
        self.length_options = [
            {"label": self.tr("Do 90 min"), "range": (0, 90), "id": "under_90"},
            {"label": self.tr("90-120 min"), "range": (90, 120), "id": "90_120"},
            {"label": self.tr("Nad 120 min"), "range": (120, 9999), "id": "over_120"}
        ]
        for option in self.length_options:
            button = TagButton(option['label'])
            button.setProperty("filter_id", option['id'])
            self.length_layout.addWidget(button)
            self.length_buttons.append(button)
        adv_filters_layout.addLayout(self.length_layout)

        adv_filters_layout.addWidget(QLabel(self.tr("Země původu:")))
        self.country_layout = FlowLayout(spacing=8)
        self.country_buttons = []
        adv_filters_layout.addLayout(self.country_layout)

        adv_filters_layout.addWidget(QLabel(self.tr("Žánry:")))
        self.genre_layout = FlowLayout(spacing=8)
        self.genre_buttons = {}

        for genre in ALL_GENRES:
            button = TagButton(QCoreApplication.translate("Genres", genre))
            button.stateChanged.connect(self.apply_filters)
            self.genre_layout.addWidget(button)
            self.genre_buttons[genre] = button

        adv_filters_layout.addLayout(self.genre_layout)
        filter_layout.addWidget(adv_filters_group)

        # Blok 3: Správa Knihovny
        filter_layout.addWidget(QLabel(self.tr("Správa knihovny")))
        library_group = QFrame(self)
        library_group.setObjectName("groupBox")
        library_layout = QVBoxLayout(library_group)

        self.library_paths_list = QListWidget()
        library_layout.addWidget(self.library_paths_list)

        path_buttons_layout = QHBoxLayout()
        self.btn_add_path = QPushButton(self.tr("Přidat složku"))
        self.btn_remove_path = QPushButton(self.tr("Odebrat"))
        path_buttons_layout.addWidget(self.btn_add_path)
        path_buttons_layout.addWidget(self.btn_remove_path)
        library_layout.addLayout(path_buttons_layout)

        self.btn_scan_paths = QPushButton(self.tr("Prohledat knihovnu"))
        library_layout.addWidget(self.btn_scan_paths)

        filter_layout.addWidget(library_group)

        # Blok 4: Akce a Nastavení
        filter_layout.addWidget(QLabel(self.tr("Akce s filmy")))
        actions_group = QFrame(self)
        actions_group.setObjectName("groupBox")
        actions_layout = QGridLayout(actions_group)

        self.btn_select_mode = QPushButton(self.tr("Označit filmy"))
        self.btn_add_files = QPushButton(self.tr("Přidat soubory"))
        self.btn_import = QPushButton(self.tr("Nahrát data"))
        self.btn_remove = QPushButton(self.tr("Odebrat vybrané"))

        actions_layout.addWidget(self.btn_select_mode, 0, 0)
        actions_layout.addWidget(self.btn_add_files, 0, 1)
        actions_layout.addWidget(self.btn_import, 1, 0)
        actions_layout.addWidget(self.btn_remove, 1, 1)

        filter_layout.addWidget(actions_group)

        # Ukončení
        filter_layout.addStretch(1)

        self.status_label = QLabel(self.tr("Připraven"))
        self.status_label.setObjectName("statusLabel")
        filter_layout.addWidget(self.status_label)

        bottom_buttons_layout = QHBoxLayout()
        self.btn_toggle_fullscreen = QPushButton(self.tr("Fullscreen"))
        self.btn_back = QPushButton(self.tr("Zpět na přehrávač"))
        bottom_buttons_layout.addWidget(self.btn_toggle_fullscreen)
        bottom_buttons_layout.addWidget(self.btn_back)

        filter_layout.addLayout(bottom_buttons_layout)

        # Mřížka s filmy
        grid_panel = QWidget()
        self.grid_layout = QGridLayout(grid_panel)
        self.grid_layout.setSpacing(12)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(grid_panel)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Finální sestavení okna
        main_layout.addWidget(scroll, stretch=5)
        main_layout.addWidget(self.filter_panel, stretch=2)

        filter_scroll = QScrollArea()
        filter_scroll.setWidgetResizable(True)
        filter_scroll.setFrameShape(QFrame.Shape.NoFrame)
        filter_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        filter_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        filter_scroll.setWidget(self.filter_panel)
        main_layout.addWidget(filter_scroll, stretch=2)

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
        for button in self.length_buttons:
            button.stateChanged.connect(self.apply_filters)
        self.filter_debounce_timer.timeout.connect(self._execute_filters)

    def on_import_button_clicked(self):
        settings = QSettings("KingPlayer", "Library")
        api_key = settings.value("tmdb_api_key", "")
        if not api_key:
            dialog = ApiKeyDialog(self)
            if dialog.exec():
                api_key = dialog.get_api_key()
                if api_key:
                    settings.setValue("tmdb_api_key", api_key)
                else:
                    return
            else:
                return

        films_to_update = self.films[:]
        if not films_to_update:
            self.status_label.setText(self.tr("Všechny filmy jsou aktuální."))
            return

        # Vytvoření a spuštění vlákna
        self.thread = QThread()
        self.worker = DataFetchingWorker(api_key, films_to_update)
        self.worker.moveToThread(self.thread)

        # Propojení signálů a slotů
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_fetching_finished)
        self.worker.progress.connect(self.update_fetch_progress)
        self.worker.film_updated.connect(self.on_single_film_updated)

        # Příprava UI
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.btn_import.setEnabled(False)
        self.status_label.setText(self.tr("Spouštím stahování dat..."))

        self.thread.start()

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
        self._update_country_filter_buttons()
        self.apply_filters()

    def load_library_paths_from_db(self):
        self.library_paths_list.clear()
        paths = self.db.get_library_paths()
        self.library_paths_list.addItems(paths)

    def _execute_filters(self):
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

        selected_ids = {btn.property("filter_id") for btn in self.length_buttons if btn.isChecked()}
        selected_lengths = [
            opt['range'] for opt in self.length_options if opt['id'] in selected_ids
        ]

        selected_countries = {btn.text() for btn in self.country_buttons if btn.isChecked()}

        selected_genres = {genre for genre, button in self.genre_buttons.items() if button.isActive()}

        # Filtrování filmů
        filtered_films = []
        for film_data in self.all_films:
            title_ok = not title_text or title_text in film_data.get('title', '').lower()
            rating_ok = float(film_data.get('rating', 0)) >= min_rating

            # Podmínka pro rok
            film_year_str = film_data.get('year') or ''
            film_year = int(film_year_str) if film_year_str.isdigit() else 0
            year_ok = year_from <= film_year <= year_to

            # Podmínka pro délku
            length_ok = True
            if selected_lengths:
                film_runtime = film_data.get('runtime') or 0
                length_ok = any(min_len < film_runtime <= max_len for min_len, max_len in selected_lengths)

            # Podmínka pro zemi
            country_ok = True
            if selected_countries:
                film_countries_str = film_data.get('country') or ''
                film_countries = {c.strip() for c in film_countries_str.split(',')}
                if film_countries.isdisjoint(selected_countries):
                    country_ok = False

            # ŽÁNRY
            genre_ok = True
            if selected_genres:
                film_genres_str = film_data.get('genres') or ''
                film_genres = set(g.strip() for g in film_genres_str.split(','))
                if film_genres.isdisjoint(selected_genres):
                    genre_ok = False

            if title_ok and rating_ok and year_ok and genre_ok and length_ok and country_ok:
                filtered_films.append(film_data)

        # Aktualizace UI
        filtered_films.sort(key=lambda film: film.get('title', '').lower())
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
                card = FilmCard(film_data, parent=self, player_window=self.player_window)
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
                             "poster": get_placeholder_poster(), "filepath": f}
                self.db.add_or_update_film(film_data)
                new_films_added = True
        if new_films_added:
            self.load_films_from_db()

    def add_selected_files(self):
        filepaths, _ = QFileDialog.getOpenFileNames(self, self.tr("Vyber filmy"), os.path.expanduser("~"),
                                                    f"{self.tr('Video soubory')} ({' '.join(['*' + ext for ext in SUPPORTED_EXTS])})",
                                                    options=QFileDialog.Option.DontUseNativeDialog)
        if filepaths:
            self.add_films_to_library(filepaths)

    def scan_library_paths(self):
        self.status_label.setText(self.tr(self.tr("Skenuji knihovnu, prosím čekejte...")))
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        QApplication.processEvents()

        try:
            all_files = []
            paths = [self.library_paths_list.item(i).text() for i in range(self.library_paths_list.count())]

            for dirpath in paths:
                self.status_label.setText(f"{self.tr('Prohledávám:')} {dirpath}...")
                QApplication.processEvents()

                for ext in SUPPORTED_EXTS:
                    all_files.extend(glob(os.path.join(dirpath, f"**/*{ext}"), recursive=True))

            if all_files:
                self.add_films_to_library(all_files)

        finally:
            QApplication.restoreOverrideCursor()
            self.status_label.setText(self.tr("Skenování dokončeno."))

    def remove_selected_films(self):
        if not self.select_mode: return

        films_to_delete = [card.film_data for card in self.card_widgets if card.checkbox.isChecked()]
        if not films_to_delete: return

        filepaths_to_delete = [film['filepath'] for film in films_to_delete]

        self.btn_remove.setEnabled(False)
        self.btn_remove.setText(self.tr("Mažu..."))
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
        self.btn_remove.setText(self.tr("Odebrat vybrané"))

        # Aktualizuje data v paměti a překresli UI
        filepaths_set = set(deleted_filepaths)
        self.all_films = [film for film in self.all_films if film['filepath'] not in filepaths_set]

        self.toggle_select_mode()
        self.apply_filters()

    def add_library_path(self):
        dirpath = QFileDialog.getExistingDirectory(self, self.tr("Vyber složku pro knihovnu"), os.path.expanduser("~"))
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
            if card.isVisible():
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

    def _handle_play_film_request(self, film_data):
        if self.animation_container:
            self._cleanup_animation()
        if self.player_window:
            playlist, idx = self.player_window.add_file_to_default_playlist(film_data["filepath"])
            self.player_window.play_from_playlist(film_data["filepath"], playlist, idx)
            self.player_window.show()
            self.player_window.showFullScreen()
        self.back_to_player()


    def on_card_hover_event(self, entered, card):
        if entered:
            if self.animation_container and self.original_card and self.original_card != card:
                self.queued_card = card
                self._animate_card_out()
            elif not self.animation_container:
                self.active_hover_card = card
                self.hover_enter_timer.start()
        else:
            self.hover_enter_timer.stop()

    def _animate_card_in(self):
        if self.animation_container or not self.active_hover_card:
            return

        self.original_card = self.active_hover_card
        self.original_card.setOpacity(0.0)

        self.animation_container = AnimatedContainer(self)
        self.animation_container.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip)

        self.animation_container.mouse_left.connect(self._animate_card_out)
        if self.width <= 1920:
            radius = 18
        else:
            radius = 22

        self.animation_container.setStyleSheet(f"""
                    AnimatedContainer {{
                        background-color: #2d3950;
                        border: 3px solid #00fff7;
                        border-radius: {radius}px;
                    }}
                """)

        self.animated_card, interactive_widgets = self.original_card._create_back_widget()

        self.original_card.play_film_requested.connect(self._handle_play_film_request)
        rating_widget = interactive_widgets.get("rating_widget")
        if rating_widget:
            rating_widget.ratingChanged.connect(
                lambda rating: self._handle_rating_changed(self.original_card.film_data, rating)
            )

        # signály tlačítek
        interactive_widgets["delete_button"].clicked.connect(
            lambda: self._handle_delete_film(self.original_card.film_data))
        interactive_widgets["edit_button"].clicked.connect(lambda: self._handle_edit_film(self.original_card.film_data))

        interactive_widgets["rating_widget"].ratingChanged.connect(
            lambda rating: self._handle_rating_changed(self.original_card.film_data, rating)
        )

        container_layout = QVBoxLayout(self.animation_container)
        container_layout.setContentsMargins(6, 6, 6, 6)
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
        if not self.animation_container: return

        # Výpočet geometrie
        w = self.start_geometry.width() * scale
        h = self.start_geometry.height() * scale
        x = self.start_geometry.x() - (w - self.start_geometry.width()) / 2
        y = self.start_geometry.y() - (h - self.start_geometry.height()) / 2
        self.animation_container.setGeometry(int(x), int(y), int(w), int(h))

        for widget, original_font in self.original_fonts.items():
            if not widget: continue
            scaled_font = QFont(original_font)

            if original_font.pointSizeF() > 0:
                new_size = original_font.pointSizeF() * scale
                if new_size > 0.1:
                    scaled_font.setPointSizeF(new_size)
            elif original_font.pixelSize() > 0:
                new_size = original_font.pixelSize() * scale
                if new_size > 1:
                    scaled_font.setPixelSize(int(new_size))

            widget.setFont(scaled_font)

    def _animate_card_out(self):
        if not self.animation_container or not self.scale_animation:
            return

        try:
            self.animation_container.mouse_left.disconnect()
        except TypeError:
            pass
        try:
            self.scale_animation.finished.disconnect()
        except TypeError:
            pass

        self.scale_animation.finished.connect(self._cleanup_animation)

        self.scale_animation.setDirection(QPropertyAnimation.Direction.Backward)
        self.scale_animation.start()

    def _cleanup_animation(self):
        if self.scale_animation and self.scale_animation.state() == QPropertyAnimation.State.Running:
            self.scale_animation.stop()

        if self.animation_container:
            self.animation_container.hide()
            self.animation_container.deleteLater()
            self.animation_container = None

        if self.original_card:
            try:
                self.original_card.play_film_requested.disconnect(self._handle_play_film_request)
            except TypeError:
                pass

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

        if self.queued_card:
            card_to_open = self.queued_card
            self.queued_card = None
            self.active_hover_card = card_to_open
            self.hover_enter_timer.start()

    def _handle_delete_film(self, film_data):
        filepath = film_data.get('filepath')
        title = film_data.get('title', self.tr('Tento soubor'))
        if not filepath:
            return

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(self.tr("Potvrdit smazání"))
        msg_box.setText(f"{self.tr('Opravdu si přejete trvale smazat film')}\n{title}?")
        msg_box.setInformativeText(self.tr("Tato akce je nevratná."))
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)

        reply = msg_box.exec()

        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_film(filepath)
            self.all_films = [film for film in self.all_films if film['filepath'] != filepath]

            self._animate_card_out()
            self.apply_filters()
        else:
            pass

    def on_film_data_updated(self, old_data, new_data):
        self.db.delete_film(old_data['filepath'])
        self.db.add_or_update_film(new_data)

        for i, film in enumerate(self.all_films):
            if film['filepath'] == old_data['filepath']:
                self.all_films[i] = new_data
                break

        self.apply_filters()

    def _handle_edit_film(self, film_data):
        self.edit_window = EditFilmWindow(film_data, self.db)
        self.edit_window.film_updated.connect(self.on_film_data_updated)
        self.edit_window.show()

        self._animate_card_out()

    def _handle_rating_changed(self, film_data, new_rating):
        film_data['rating'] = new_rating

        self.db.add_or_update_film(film_data)

        if self.original_card and self.original_card.film_data['filepath'] == film_data['filepath']:
            self.original_card.rating_widget.setRating(new_rating)

    def on_single_film_updated(self, updated_film_data):
        self.db.add_or_update_film(updated_film_data)
        for i, film in enumerate(self.all_films):
            if film['filepath'] == updated_film_data['filepath']:
                self.all_films[i] = updated_film_data
                break
        for card in self.card_widgets:
            if card.isVisible() and card.film_data['filepath'] == updated_film_data['filepath']:
                card.update_data(updated_film_data, self.select_mode)
                break

    def update_fetch_progress(self, current, total, title):
        self.status_label.setText(f"{self.tr('Stahuji')} ({current}/{total}): {title}...")

    def on_fetching_finished(self):
        QApplication.restoreOverrideCursor()
        self.btn_import.setEnabled(True)
        self.status_label.setText(self.tr("Stahování dokončeno."))
        self.apply_filters()
        self.thread.quit()
        self.thread.wait()
        self.thread = None
        self.worker = None

    def _update_animation_frame(self, scale):
        if not self.animation_container: return

        w = self.start_geometry.width() * scale
        h = self.start_geometry.height() * scale
        x = self.start_geometry.x() - (w - self.start_geometry.width()) / 2
        y = self.start_geometry.y() - (h - self.start_geometry.height()) / 2
        self.animation_container.setGeometry(int(x), int(y), int(w), int(h))

        for widget, original_font in self.original_fonts.items():
            try:
                if not widget: continue

                scaled_font = QFont(original_font)
                if original_font.pointSizeF() > 0:
                    new_size = original_font.pointSizeF() * scale
                    if new_size > 0.1: scaled_font.setPointSizeF(new_size)
                elif original_font.pixelSize() > 0:
                    new_size = original_font.pixelSize() * scale
                    if new_size > 1: scaled_font.setPixelSize(int(new_size))

                widget.setFont(scaled_font)

            except RuntimeError:
                continue

    def _update_country_filter_buttons(self):
        for button in self.country_buttons:
            self.country_layout.removeWidget(button)
            button.deleteLater()
        self.country_buttons.clear()

        all_countries = set()
        for film in self.all_films:
            countries_str = film.get('country') or ''
            for country in countries_str.split(','):
                cleaned_country = country.strip()
                if cleaned_country:
                    all_countries.add(cleaned_country)

        for country in sorted(list(all_countries)):
            button = TagButton(country)
            button.stateChanged.connect(self.apply_filters)
            self.country_layout.addWidget(button)
            self.country_buttons.append(button)