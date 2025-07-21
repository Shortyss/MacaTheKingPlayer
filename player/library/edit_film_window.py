import os
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QFormLayout, QMessageBox, QTextEdit, QFileDialog
)

from .constants import ALL_GENRES
from .custom_widgets import TagButton
from .flow_layout import FlowLayout
from .styles import get_main_stylesheet


class EditFilmWindow(QWidget):
    film_updated = pyqtSignal(dict, dict)

    def __init__(self, film_data, db_manager, parent=None):
        super().__init__(parent)
        self.setStyleSheet(get_main_stylesheet())
        self.film_data = film_data
        self.db = db_manager
        self.new_poster_path = self.film_data.get('poster')
        self.genre_buttons = []  # Seznam pro naše tlačítka žánrů

        self.setWindowTitle(f"Úprava filmu: {self.film_data.get('title', '...')}")
        self.setMinimumSize(600, 600)

        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)

        # --- Pole pro základní info ---
        self.title_edit = QLineEdit(self.film_data.get('title'))
        form_layout.addRow("Nový název:", self.title_edit)

        self.year_edit = QLineEdit(str(self.film_data.get('year', '')))
        form_layout.addRow("Rok vydání:", self.year_edit)

        self.country_edit = QLineEdit(self.film_data.get('country', ''))
        self.country_edit.setPlaceholderText("Země oddělené čárkou, např. USA, Německo")
        form_layout.addRow("Země původu:", self.country_edit)

        self.trailer_edit = QLineEdit(self.film_data.get('trailer_url', ''))
        self.trailer_edit.setPlaceholderText("Vložte odkaz na trailer (např. z YouTube)")
        form_layout.addRow("Odkaz na trailer:", self.trailer_edit)

        # --- Výběr žánrů ---
        genres_string = self.film_data.get('genres') or ''
        current_genres = {genre.strip() for genre in genres_string.split(',') if genre}
        genre_layout = FlowLayout(spacing=8)
        for genre_name in ALL_GENRES:
            button = TagButton(genre_name)
            if genre_name in current_genres:
                button.setChecked(True)
            self.genre_buttons.append(button)
            genre_layout.addWidget(button)
        form_layout.addRow("Žánry:", genre_layout)

        # --- Plakát a popis ---
        # ... kód pro plakát a popis zůstává stejný ...
        poster_layout = QHBoxLayout()
        self.poster_label = QLabel()
        self.poster_label.setFixedSize(100, 150)
        self.update_poster_preview(self.new_poster_path)
        btn_change_poster = QPushButton("Změnit plakát")
        btn_change_poster.clicked.connect(self.change_poster)
        poster_layout.addWidget(self.poster_label)
        poster_layout.addWidget(btn_change_poster, alignment=Qt.AlignmentFlag.AlignTop)
        form_layout.addRow("Plakát:", poster_layout)

        self.overview_edit = QTextEdit(self.film_data.get('overview'))
        self.overview_edit.setPlaceholderText("Zde napište stručný popis filmu...")
        self.overview_edit.setMinimumHeight(100)
        form_layout.addRow("Popis filmu:", self.overview_edit)

        main_layout.addLayout(form_layout)
        main_layout.addStretch()

        # --- Tlačítka Uložit / Zrušit ---
        # ... kód tlačítek zůstává stejný ...
        button_layout = QHBoxLayout()
        self.btn_save = QPushButton("Uložit změny")
        self.btn_cancel = QPushButton("Zrušit")
        button_layout.addStretch()
        button_layout.addWidget(self.btn_save)
        button_layout.addWidget(self.btn_cancel)
        main_layout.addLayout(button_layout)
        self.btn_cancel.clicked.connect(self.close)
        self.btn_save.clicked.connect(self.save_changes)

    def change_poster(self):
        # ... tato metoda zůstává stejná ...
        filepath, _ = QFileDialog.getOpenFileName(self, "Vyberte nový plakát", "", "Obrázky (*.png *.jpg *.jpeg)")
        if filepath:
            self.new_poster_path = filepath
            self.update_poster_preview(filepath)

    def update_poster_preview(self, path):
        # ... tato metoda zůstává stejná ...
        pixmap = QPixmap(path)
        if pixmap.isNull(): pixmap = QPixmap("assets/icons/KingPlayer6.png")
        scaled_pixmap = pixmap.scaled(100, 150, Qt.AspectRatioMode.KeepAspectRatio,
                                      Qt.TransformationMode.SmoothTransformation)
        self.poster_label.setPixmap(scaled_pixmap)

    def save_changes(self):
        """Sbírá data ze všech polí, zpracuje je a vyšle signál."""
        # --- Přejmenování souboru (logika zůstává) ---
        old_filepath = self.film_data['filepath']
        new_title = self.title_edit.text().strip()
        new_filepath = old_filepath

        # Přejmenování provedeme jen pokud se název skutečně změnil
        if new_title and new_title != self.film_data.get('title'):
            directory = os.path.dirname(old_filepath)
            _, extension = os.path.splitext(old_filepath)
            new_filepath = os.path.join(directory, new_title + extension)
            try:
                if os.path.exists(new_filepath):
                    raise FileExistsError(f"Soubor s názvem '{new_title}{extension}' již existuje.")
                os.rename(old_filepath, new_filepath)
            except (OSError, FileExistsError) as e:
                QMessageBox.critical(self, "Chyba při přejmenování", f"Nepodařilo se přejmenovat soubor.\nChyba: {e}")
                return

        # --- Sběr dat z nových polí ---
        new_data = self.film_data.copy()
        new_data['title'] = new_title
        new_data['filepath'] = new_filepath
        new_data['year'] = self.year_edit.text()
        new_data['overview'] = self.overview_edit.toPlainText()
        new_data['poster'] = self.new_poster_path
        new_data['country'] = self.country_edit.text().strip()
        new_data['trailer_url'] = self.trailer_edit.text().strip()

        active_genres = [btn.text() for btn in self.genre_buttons if btn.isChecked()]
        new_data['genres'] = ", ".join(active_genres)

        self.film_updated.emit(self.film_data, new_data)
        self.close()