import os

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGraphicsView, QGraphicsScene
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QGraphicsVideoItem
from PyQt6.QtCore import (
    QUrl, QTimer, Qt, QSizeF, QPointF,
    QPropertyAnimation, QEasingCurve, QEvent, QSize
)

from .info_overlay import InfoOverlay
from .overlay import ControlOverlay
from .playlist import PlaylistWindow, cleanup_default_playlist, get_connection


class PlayerWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()

        self.setWindowTitle("The King's Player by Shortyss")
        self.setWindowIcon(QIcon("assets/icons/KingPlayer6.png"))
        self.resize(1280, 720)
        self.setStyleSheet("background-color:black;")
        # media
        self.player = QMediaPlayer(self)
        self.audio = QAudioOutput(self)
        self.player.setAudioOutput(self.audio)
        # scene/video
        self.video_item = QGraphicsVideoItem()
        self.player.setVideoOutput(self.video_item)
        self.video_item.setSize(QSizeF(self.width(), self.height()))
        scene = QGraphicsScene(self)
        scene.addItem(self.video_item)
        # overlays
        self.bottom = ControlOverlay()
        self.bottom.player = self.player
        # proxies
        self.proxy_b = scene.addWidget(self.bottom)
        self.proxy_b.setZValue(1)
        self.anim_b = QPropertyAnimation(self.proxy_b, b'pos')
        self.anim_b.setDuration(200)
        self.anim_b.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.anim_b.finished.connect(self._on_anim_finished)
        # view/layout
        self.view = DraggableGraphicsView(scene, self, on_drop_callback=self.handle_player_drop)

        self.view.setFrameStyle(0)
        self.view.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)

        # timer
        self.hide_timer = QTimer(self)
        self.hide_timer.setInterval(2000)
        self.hide_timer.timeout.connect(self.slide_out)

        # mouse
        self.view.viewport().installEventFilter(self)
        self._single_click_timer = QTimer(self)
        self._single_click_timer.setSingleShot(True)
        self._single_click_timer.timeout.connect(self.toggle_play_pause)
        # start
        self.playlist_window = None
        self.current_playlist = []
        self.current_index = -1
        # -- signály --

        self.player.durationChanged.connect(self.bottom.set_duration)
        self.player.positionChanged.connect(self.bottom.update_position)
        self.bottom.position_seeked.connect(self.player.setPosition)

        self.bottom.play_pause_toggled.connect(self.toggle_play)
        self.player.playbackStateChanged.connect(self.bottom.update_play_pause_icon)
        self.bottom.fullscreen_toggled.connect(self.on_fullscreen_button)

        self.bottom.stop_pressed.connect(self.stop_movie)

        self.bottom.prev_pressed.connect(self.prev_movie)
        self.bottom.next_pressed.connect(self.next_movie)
        self.bottom.back10_pressed.connect(self.seek_back10)
        self.bottom.forward10_pressed.connect(self.seek_forward10)
        self.bottom.mute_toggled.connect(self.toggle_mute)
        self.bottom.volume_changed.connect(self.set_volume)
        self.audio.setVolume(self.bottom.volume_slider.value() / 100)

        self.bottom.donate_pressed.connect(self.on_donate)
        self.bottom.playlist_pressed.connect(self.show_playlist)
        self.bottom.library_pressed.connect(self.on_library)
        self.bottom.settings_pressed.connect(self.on_settings)
        self.bottom.effects_volume_pressed.connect(self.on_effects_volume)

        self.player.mediaStatusChanged.connect(self._on_media_status_changed)

        # --- přidáme info overlay ---
        self.info_overlay = InfoOverlay(self)
        self.info_overlay.hide()

        self.bottom.hide()


    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.video_item.setSize(QSizeF(self.width(), self.height()))
        self.view.setSceneRect(0, 0, self.width(), self.height())
        self._compute_positions()
        QTimer.singleShot(0, self.fix_overlay_position)

    def _compute_positions(self):
        W, H = self.width(), self.height()
        # bottom
        bw, bh = W * 0.9, self.bottom.sizeHint().height()
        bx, by = (W - bw) / 2, H - bh
        self.start_b = QPointF(bx, H)
        self.end_b = QPointF(bx, by)
        self.bottom.resize(int(bw), int(bh))
        if not self.proxy_b.isVisible():
            self.proxy_b.setPos(self.start_b)


    def eventFilter(self, obj, event):
        if obj is self.view.viewport():
            if event.type() == QEvent.Type.MouseMove:
                event_type = event.type()
                if event_type == QEvent.Type.MouseMove:
                    self.slide_in()

            elif event.type() == QEvent.Type.MouseButtonPress:
                if event.button() == Qt.MouseButton.LeftButton:
                    pos = event.position().toPoint() if hasattr(event, 'position') else event.pos()
                    scene_pos = self.view.mapToScene(pos)
                    items = self.view.scene().items(scene_pos)
                    if any(isinstance(item.widget(), ControlOverlay) for item in items if hasattr(item, 'widget')):
                        self.setFocus()
                        return super().eventFilter(obj, event)
                    self._single_click_timer.start(180)
                    self.setFocus()

            elif event.type() == QEvent.Type.MouseButtonDblClick:
                if event.button() == Qt.MouseButton.LeftButton:
                    pos = event.position().toPoint() if hasattr(event, 'position') else event.pos()
                    scene_pos = self.view.mapToScene(pos)
                    items = self.view.scene().items(scene_pos)
                    if any(isinstance(item.widget(), ControlOverlay) for item in items if hasattr(item, 'widget')):
                        self.setFocus()
                        return super().eventFilter(obj, event)
                    self._single_click_timer.stop()
                    self.toggle_fullscreen()
                    self.setFocus()

        return super().eventFilter(obj, event)


    def slide_in(self):
        self.hide_timer.stop()
        for proxy, anim, start, end in (
            (self.proxy_b, self.anim_b, self.proxy_b.pos(), self.end_b),
        ):
            anim.stop()
            anim.setStartValue(start)
            anim.setEndValue(end)
            proxy.show()
            anim.start()
        self.hide_timer.start()

    def slide_out(self):
        self.hide_timer.stop()
        for anim, start, proxy in (
            (self.anim_b, self.start_b, self.proxy_b),
        ):
            anim.stop()
            anim.setStartValue(proxy.pos())
            anim.setEndValue(start)
            anim.start()

    def _on_anim_finished(self):
        if self.proxy_b.pos() == self.start_b:
            self.proxy_b.hide()

    def toggle_play_pause(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def resize_overlay(self):
        self._compute_positions()

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
        self.bottom.hide()
        self.fix_overlay_position()
        QTimer.singleShot(50, self.bottom.show)

    def on_fullscreen_button(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
        self.bottom.hide()
        QTimer.singleShot(50, self.bottom.show)

    def fix_overlay_position(self):
        self.view.setSceneRect(0, 0, self.width(), self.height())
        self._compute_positions()
        self.view.viewport().update()
        self.bottom.update()
        self.proxy_b.update()

    def toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        else:
            self.player.play()
        self.bottom.update_play_pause_icon(self.player.playbackState())

    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            self.handle_key(event, repeat=True)
        else:
            self.handle_key(event, repeat=False)
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        super().keyReleaseEvent(event)

    def handle_key(self, event, repeat=False):
        key = event.key()
        if key == Qt.Key.Key_Right:
            if repeat:
                self.player.setPosition(self.player.position() + 10000)
                self.info_overlay.show_message(">> +10s")
            else:
                self.player.setPosition(self.player.position() + 5000)
                self.info_overlay.show_message("> +5s")
        elif key == Qt.Key.Key_Left:
            if repeat:
                self.player.setPosition(self.player.position() - 10000)
                self.info_overlay.show_message("<< -10s")
            else:
                self.player.setPosition(self.player.position() - 5000)
                self.info_overlay.show_message("< -5s")
        elif key == Qt.Key.Key_Up:
            v = self.audio.volume()
            newval = min(1.0, v + 0.02)
            self.audio.setVolume(newval)
            self.bottom.volume_slider.setValue(int(newval * 100))
            self.info_overlay.show_volume(int(newval * 100))
        elif key == Qt.Key.Key_Down:
            v = self.audio.volume()
            newval = max(0.0, v - 0.02)
            self.audio.setVolume(newval)
            self.bottom.volume_slider.setValue(int(newval * 100))
            self.info_overlay.show_volume(int(newval * 100))
        elif key == Qt.Key.Key_Space:
            self.toggle_play_pause()
            state = "⏸ Pause" if self.player.playbackState() == QMediaPlayer.PlaybackState.PausedState else "▶ Play"
            self.info_overlay.show_message(state)

    def toggle_mute(self):
        muted = self.audio.isMuted()
        self.audio.setMuted(not muted)
        self.bottom.set_muted(not muted)
        self.bottom.set_muted(self.audio.isMuted())

    def stop_movie(self):
        self.player.stop()

    def seek_back10(self):
        self.player.setPosition(self.player.position() - 10000)

    def seek_forward10(self):
        self.player.setPosition(self.player.position() + 10000)

    def set_volume(self, val):
        self.audio.setVolume(val / 100)
        self.info_overlay.show_volume(val)

    def on_donate(self):
        # TODO: donate
        print("Díky, právě jsi mě skoro rozbrečel radostí!")

    def on_playlist_closed(self):
        print("Playlist okno bylo zavřeno, resetuji referenci.")
        self.playlist_window = None

    def show_playlist(self):
        if self.playlist_window and self.playlist_window.isVisible():
            self.playlist_window.raise_()
            self.playlist_window.activateWindow()
            return

        self.playlist_window = PlaylistWindow(
            player_callback=self.play_from_playlist,
            on_close_callback=self.on_playlist_closed,
        )
        self.playlist_window.show()

    def play_from_playlist(self, filepath, playlist_files, index):
        self.player.setSource(QUrl.fromLocalFile(filepath))
        self.player.play()
        self.current_playlist = playlist_files
        self.current_index = index
        print(
            f"Přehrávám '{os.path.basename(filepath)}' (index {index}) z playlistu o {len(playlist_files)} položkách.")
        if self.playlist_window and self.playlist_window.isVisible():
            self.playlist_window.highlight_current_film(filepath)
        if self.playlist_window and self.playlist_window.isVisible():
            self.playlist_window.current_playing_file = filepath
            self.playlist_window.highlight_current_film(filepath)

    def load_from_playlist(self, film_path, playlist, idx):
        self.player.setSource(QUrl.fromLocalFile(film_path))
        self.player.play()
        self.current_playlist = playlist
        self.current_index = idx

    def add_file_to_default_playlist(self, file_path: str):
        with get_connection() as con:
            cur = con.cursor()
            cur.execute("SELECT id FROM playlists WHERE name = '_DEFAULT_'")
            playlist_id = cur.fetchone()[0]

            cur.execute("SELECT COALESCE(MAX(position), 0) FROM playlist_items WHERE playlist_id=?", (playlist_id,))
            pos = cur.fetchone()[0] + 1
            cur.execute("INSERT INTO playlist_items (playlist_id, filename, position) VALUES (?, ?, ?)",
                        (playlist_id, file_path, pos))
            con.commit()

            cur.execute("SELECT filename FROM playlist_items WHERE playlist_id=? ORDER BY position", (playlist_id,))
            updated_playlist = [row[0] for row in cur.fetchall()]
            new_index = updated_playlist.index(file_path)

            return updated_playlist, new_index

    def next_movie(self):
        if self.current_playlist and 0 <= self.current_index + 1 < len(self.current_playlist):
            self.current_index += 1
            self.load_from_playlist(self.current_playlist[self.current_index], self.current_playlist,
                                    self.current_index)
            # Tady už je self.current_index na správném místě
            if self.playlist_window and self.playlist_window.isVisible():
                filepath = self.current_playlist[self.current_index]
                self.playlist_window.highlight_current_film(filepath)
            if self.playlist_window and self.playlist_window.isVisible():
                self.playlist_window.current_playing_file = filepath
                self.playlist_window.highlight_current_film(filepath)

    def prev_movie(self):
        if self.current_playlist and self.current_index > 0:
            self.current_index -= 1
            self.load_from_playlist(self.current_playlist[self.current_index], self.current_playlist,
                                    self.current_index)
            if self.playlist_window and self.playlist_window.isVisible():
                filepath = self.current_playlist[self.current_index]
                self.playlist_window.highlight_current_film(filepath)
            if self.playlist_window and self.playlist_window.isVisible():
                self.playlist_window.current_playing_file = filepath
                self.playlist_window.highlight_current_film(filepath)

    def handle_player_drop(self, files):
        if files:
            print(f"handle_player_drop: Přetažen soubor na přehrávač: {files}")
            playlist_files, idx = self.add_file_to_default_playlist(files[0])
            self.play_from_playlist(files[0], playlist_files, idx)
            if self.playlist_window and self.playlist_window.isVisible():
                self.playlist_window.load_films()
                self.playlist_window.current_playing_file = files[0]
                self.playlist_window.highlight_current_film(files[0])

    def on_library(self):
        print("Zpět do knihovny - ve vývoji.")

    def on_settings(self):
        print("Otevřít nastavení - ve vývoji.")

    def on_effects_volume(self):
        print("Ovládání efektů - zatím sci-fi.")

    def closeEvent(self, event):
        cleanup_default_playlist()
        if hasattr(self, "playlist_window") and self.playlist_window:
            self.playlist_window.close()
        super().closeEvent(event)

    def _on_media_status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.next_movie()


class DraggableGraphicsView(QGraphicsView):
    def __init__(self, *args, on_drop_callback=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)
        self.on_drop_callback = on_drop_callback

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            print("DRAG ENTER na VIEW!")  # debug
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            print("DRAG MOVE na VIEW!")  # debug
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            files = [url.toLocalFile() for url in event.mimeData().urls() if url.isLocalFile()]
            print("DROP na VIEW!", files)
            if self.on_drop_callback:
                self.on_drop_callback(files)
            event.acceptProposedAction()
        else:
            event.ignore()

