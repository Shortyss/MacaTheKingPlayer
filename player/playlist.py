import os.path
import sqlite3

from PyQt6 import QtGui
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton,
    QInputDialog, QMessageBox, QLabel, QFileDialog, QListWidgetItem
)
from PyQt6.QtCore import Qt, QPoint


DB_PATH = "playlist.db"

def get_connection():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS playlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS playlist_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            playlist_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            position INTEGER NOT NULL,
            FOREIGN KEY(playlist_id) REFERENCES playlists(id)
        )
    """)
    con.commit()
    return con

def init_settings_table():
    with get_connection() as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        con.commit()


class FilmListWidget(QListWidget):
    def __init__(self, parent=None, add_files_callback=None):
        super().__init__(parent)
        self.add_files_callback = add_files_callback
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() or event.source() == self:
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            files = [url.toLocalFile() for url in event.mimeData().urls()]
            if self.add_files_callback:
                self.add_files_callback(files)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)
            if self.parent() and hasattr(self.parent(), "reorder_films"):
                self.parent().reorder_films()


def set_setting(key, value):
    with get_connection() as con:
        cur = con.cursor()
        cur.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        con.commit()

def get_setting(key, default=None):
    with get_connection() as con:
        cur = con.cursor()
        cur.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = cur.fetchone()
        return row[0] if row else default


class PlaylistWindow(QWidget):
    def __init__(self, player_callback, on_close_callback, main_window_ref=None):
        super().__init__()
        self.setAcceptDrops(True)
        self.setEnabled(True)
        self.setWindowTitle("Playlisty")
        self.setWindowIcon(QIcon("assets/icons/KingPlayer6.png"))
        self.resize(420, 480)
        self.dock_offset = QPoint(0, 0)
        self.player_callback = player_callback
        self.on_close_callback = on_close_callback
        self.main_window_ref = main_window_ref

        self.current_playlist_id = None

        layout = QHBoxLayout(self)
        playlist_layout = QVBoxLayout()
        self.playlist_list = QListWidget()
        self.btn_add_playlist = QPushButton("Nový playlist")
        self.btn_delete_playlist = QPushButton("Smazat playlist")
        self.btn_rename_playlist = QPushButton("Přejmenovat")
        playlist_layout.addWidget(QLabel("Playlisty:"))
        playlist_layout.addWidget(self.playlist_list)
        playlist_layout.addWidget(self.btn_add_playlist)
        playlist_layout.addWidget(self.btn_delete_playlist)
        playlist_layout.addWidget(self.btn_rename_playlist)

        # Filmy vpravo
        film_layout = QVBoxLayout()
        self.film_list = FilmListWidget(add_files_callback=self.add_files_to_current_playlist)
        self.film_list.viewport().setAcceptDrops(True)
        self.film_list.viewport().dragEnterEvent = self.film_list.dragEnterEvent
        self.film_list.viewport().dropEvent = self.film_list.dropEvent
        self.film_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)

        self.setWindowOpacity(0.66)

        self.setStyleSheet("""
            QWidget {
                background: rgba(34, 43, 66, 100); 
                border-radius: 20px;
                color: #eafff7;
                font-family: Segoe UI, Arial, sans-serif;
                font-size: 15px;
            }
            QListWidget {
                background: #232941;
                border-radius: 14px;
                border: 1.5px solid #32ffd299;
                color: #f8fff8;
                font-size: 15px;
                padding: 5px;
                selection-background-color: #41ffe7; 
                selection-color: #000000;    
                outline: none;
            }
            QListWidget::item:selected {
                background: #22ffc6;  
                color: #000000;      
                border-radius: 8px;
            }
            QPushButton {
                background: qradialgradient(
                    cx:0.5, cy:0.55, radius:0.82, fx:0.5, fy:0.5,
                    stop:0 #283950, stop:0.5 #26466e, stop:0.9 #365b82, stop:1 transparent
                );
                border-radius: 14px;
                border: 1.2px solid #20ffe988;
                color: #000000;  
                font-weight: bold;
                min-width: 90px; min-height: 30px;
                margin-top: 4px;
                margin-bottom: 4px;
            }
            QPushButton:hover {
                background: qradialgradient(
                    cx:0.5, cy:0.52, radius:0.7, fx:0.5, fy:0.5,
                    stop:0 #41ffe7, stop:0.7 #162c2c, stop:1 transparent
                );
                border: 1.8px solid #22ffc6;
                color: #000000;  
            }
            QLabel {
                color: #aaf0fc;
                font-size: 14px;
                background: transparent;
                font-weight: 600;
                letter-spacing: 0.5px;
            }
        """)

        self.current_playing_file = None

        self.btn_add_film = QPushButton("Přidat film")
        self.btn_remove_film = QPushButton("Smazat film")
        film_layout.addWidget(QLabel("Filmy v playlistu:"))
        film_layout.addWidget(self.film_list)
        film_layout.addWidget(self.btn_add_film)
        film_layout.addWidget(self.btn_remove_film)

        layout.addLayout(playlist_layout, 1)
        layout.addLayout(film_layout, 2)

        # Connect signals
        self.btn_add_playlist.clicked.connect(self.add_playlist)
        self.btn_delete_playlist.clicked.connect(self.delete_playlist)
        self.btn_rename_playlist.clicked.connect(self.rename_playlist)
        self.playlist_list.itemClicked.connect(self.load_films)
        self.btn_add_film.clicked.connect(self.add_film)
        self.btn_remove_film.clicked.connect(self.remove_film)
        self.film_list.itemDoubleClicked.connect(self.play_selected_film)
        self.film_list.keyPressEvent = self.film_list_keyPressEvent

        self.load_playlists()

    def load_playlists(self):
        self.playlist_list.clear()
        with get_connection() as con:
            con.execute("INSERT OR IGNORE INTO playlists (name) VALUES ('_DEFAULT_')")
            con.commit()

            rows = list(con.execute("SELECT id, name FROM playlists ORDER BY name"))

        for row_id, name in rows:
            item_text = "Default" if name == "_DEFAULT_" else name
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, row_id)
            self.playlist_list.addItem(item)

        # poslední vybraný playlist
        last_id = get_setting("last_playlist_id", None)
        found = False
        if last_id is not None:
            for i in range(self.playlist_list.count()):
                item = self.playlist_list.item(i)
                if str(item.data(Qt.ItemDataRole.UserRole)) == str(last_id):
                    self.playlist_list.setCurrentRow(i)
                    found = True
                    break

        if not found and self.playlist_list.count() > 0:
            self.playlist_list.setCurrentRow(0)

        self.load_films()

    def add_playlist(self):
        name, ok = QInputDialog.getText(self, "Nový playlist", "Zadej název:")

        if ok and name:
            if name.lower() == 'default':
                QMessageBox.warning(self, "Chyba", "Název 'Default' je rezervovaný a nelze ho použít.")
                return

            try:
                with get_connection() as con:
                    cur = con.cursor()
                    cur.execute("INSERT INTO playlists (name) VALUES (?)", (name,))
                    new_id = cur.lastrowid
                    con.commit()

                item = QListWidgetItem(name)
                item.setData(Qt.ItemDataRole.UserRole, new_id)
                self.playlist_list.addItem(item)
                self.playlist_list.setCurrentItem(item)

            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Chyba", f"Playlist s názvem '{name}' již existuje.")

    def delete_playlist(self):
        item = self.playlist_list.currentItem()
        if item and item.text() != "Default":
            playlist_id = item.data(Qt.ItemDataRole.UserRole)
            row = self.playlist_list.row(item)

            with get_connection() as con:
                con.execute("DELETE FROM playlist_items WHERE playlist_id=?", (playlist_id,))
                con.execute("DELETE FROM playlists WHERE id=?", (playlist_id,))

            self.playlist_list.takeItem(row)

    def rename_playlist(self):
        item = self.playlist_list.currentItem()
        if not item or item.text() == "Default":
            return

        id_ = item.data(Qt.ItemDataRole.UserRole)
        old_name = item.text()
        new_name, ok = QInputDialog.getText(self, "Přejmenovat", "Nový název:", text=old_name)

        if ok and new_name and new_name != old_name:
            if new_name.lower() == 'default':
                QMessageBox.warning(self, "Chyba", "Název 'Default' je rezervovaný a nelze ho použít.")
                return

            try:
                with get_connection() as con:
                    con.execute("UPDATE playlists SET name=? WHERE id=?", (new_name, id_))
                item.setText(new_name)


            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Chyba", f"Playlist s názvem '{new_name}' již existuje.")


    def load_films(self):
        self.film_list.clear()
        item = self.playlist_list.currentItem()
        if not item:
            return
        id_ = item.data(Qt.ItemDataRole.UserRole)
        self.current_playlist_id = id_
        with get_connection() as con:
            for row in con.execute("SELECT filename FROM playlist_items WHERE playlist_id=? ORDER BY position", (id_,)):
                fpath = row[0]
                fname = os.path.basename(fpath)
                fitem = QListWidgetItem(fname)
                fitem.setData(Qt.ItemDataRole.UserRole, fpath)
                self.film_list.addItem(fitem)
        if self.current_playing_file:
            self.highlight_current_film(self.current_playing_file)
        set_setting("last_playlist_id", str(self.current_playlist_id))

    def ensure_playlist_exists(self):
        with get_connection() as con:
            cur = con.cursor()
            cur.execute("SELECT id FROM playlists ORDER BY id")
            row = cur.fetchone()
            if row:
                return row[0]
            cur.execute("INSERT INTO playlists (name) VALUES ('_DEFAULT_')")
            con.commit()
            return cur.lastrowid

    def add_film(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Přidat filmy", "", "Videa (*.mp4 *.avi *.mkv)")
        playlist_id = self.current_playlist_id or self.ensure_playlist_exists()
        self.current_playlist_id = playlist_id
        if files:
            with get_connection() as con:
                cur = con.cursor()
                cur.execute("SELECT COALESCE(MAX(position),0) FROM playlist_items WHERE playlist_id=?", (playlist_id,))
                pos = cur.fetchone()[0] + 1
                for i, f in enumerate(files):
                    cur.execute("INSERT INTO playlist_items (playlist_id, filename, position) VALUES (?, ?, ?)",
                                (playlist_id, f, pos + i))
                con.commit()
            self.load_films()

    def remove_film(self):
        item = self.film_list.currentItem()
        if item and self.current_playlist_id:
            filepath = item.data(Qt.ItemDataRole.UserRole)
            with get_connection() as con:
                con.execute("DELETE FROM playlist_items WHERE playlist_id=? AND filename=?",
                            (self.current_playlist_id, filepath))
            self.load_films()

    def play_selected_film(self, item):
        all_files = [self.film_list.item(i).data(Qt.ItemDataRole.UserRole) for i in range(self.film_list.count())]
        current_index = self.film_list.row(item)
        filepath = item.data(Qt.ItemDataRole.UserRole)

        self.player_callback(filepath, all_files, current_index)

    def film_list_keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            self.remove_film()
        else:
            QListWidget.keyPressEvent(self.film_list, event)


    def add_files_to_playlist(self, files):
        if files and self.current_playlist_id:
            with get_connection() as con:
                cur = con.cursor()
                cur.execute("SELECT COALESCE(MAX(position),0) FROM playlist_items WHERE playlist_id=?",
                            (self.current_playlist_id,))
                pos = cur.fetchone()[0] + 1
                for i, f in enumerate(files):
                    cur.execute("INSERT INTO playlist_items (playlist_id, filename, position) VALUES (?, ?, ?)",
                                (self.current_playlist_id, f, pos + i))
                con.commit()
            self.load_films()

    def closeEvent(self, event):
        if self.on_close_callback:
            self.on_close_callback()
        event.accept()

    def add_files_to_current_playlist(self, files: list):
        if not self.current_playlist_id:
            QMessageBox.warning(self, "Chyba", "Není vybrán žádný playlist.")
            return

        with get_connection() as con:
            cur = con.cursor()
            cur.execute("SELECT COALESCE(MAX(position), 0) FROM playlist_items WHERE playlist_id=?",
                        (self.current_playlist_id,))
            pos = cur.fetchone()[0] + 1
            for i, f in enumerate(files):
                cur.execute("INSERT INTO playlist_items (playlist_id, filename, position) VALUES (?, ?, ?)",
                            (self.current_playlist_id, f, pos + i))
            con.commit()
        self.load_films()

    def reorder_films(self):
        new_order = []
        for i in range(self.film_list.count()):
            fpath = self.film_list.item(i).data(Qt.ItemDataRole.UserRole)
            new_order.append(fpath)
        if not self.current_playlist_id:
            return
        with get_connection() as con:
            cur = con.cursor()
            for pos, filename in enumerate(new_order, 1):
                cur.execute(
                    "UPDATE playlist_items SET position=? WHERE playlist_id=? AND filename=?",
                    (pos, self.current_playlist_id, filename)
                )
            con.commit()

    def highlight_current_film(self, filepath):
        for i in range(self.film_list.count()):
            item = self.film_list.item(i)
            path = item.data(Qt.ItemDataRole.UserRole)
            font = item.font()
            if path == filepath:
                font.setBold(True)
                item.setFont(font)
                item.setBackground(QtGui.QColor("#22ffc6"))
                item.setForeground(QtGui.QColor("#181a1f"))
            else:
                font.setBold(False)
                item.setFont(font)
                item.setBackground(Qt.GlobalColor.transparent)
                item.setForeground(QtGui.QColor("#f8fff8"))


def cleanup_default_playlist():
    try:
        with get_connection() as con:
            cur = con.cursor()
            cur.execute("SELECT id FROM playlists WHERE name = '_DEFAULT_'")
            res = cur.fetchone()
            if res:
                default_id = res[0]
                # Smažeme položky tohoto playlistu
                con.execute("DELETE FROM playlist_items WHERE playlist_id = ?", (default_id,))
            con.commit()
    except sqlite3.Error as e:
        print(f"Chyba při čištění dočasného playlistu: {e}")


