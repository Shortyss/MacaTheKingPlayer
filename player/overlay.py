from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStyle, QLabel, QSlider, QFrame
from PyQt6.QtGui import QMouseEvent, QIcon
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from PyQt6.QtMultimedia import QMediaPlayer

class ClickableSlider(QSlider):
    """Slider that reacts to click-to-seek."""
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            val = self.style().sliderValueFromPosition(
                self.minimum(), self.maximum(), event.pos().x(), self.width()
            )
            self.setValue(val)
            self.sliderMoved.emit(val)
        super().mousePressEvent(event)

class ControlOverlay(QWidget):
    play_pause_toggled = pyqtSignal()
    stop_pressed = pyqtSignal()
    position_seeked = pyqtSignal(int)
    fullscreen_toggled = pyqtSignal()
    prev_pressed = pyqtSignal()
    next_pressed = pyqtSignal()
    back10_pressed = pyqtSignal()
    forward10_pressed = pyqtSignal()
    volume_changed = pyqtSignal(int)
    donate_pressed = pyqtSignal()
    playlist_pressed = pyqtSignal()
    library_pressed = pyqtSignal()
    settings_pressed = pyqtSignal()
    effects_volume_pressed = pyqtSignal()
    mute_toggled = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ControlOverlay")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.bg_panel = QFrame(self)
        self.bg_panel.setObjectName("OverlayPanel")

        # ---- Ovládací prvky ----
        self.play_icon = QIcon("assets/icons/play.svg")
        self.pause_icon = QIcon("assets/icons/pause.svg")
        self.stop_icon = QIcon("assets/icons/stop.svg")
        self.prev_icon = QIcon("assets/icons/prev.svg")
        self.next_icon = QIcon("assets/icons/next.svg")
        self.back10_icon = QIcon("assets/icons/back10.svg")
        self.forward10_icon = QIcon("assets/icons/forward10.svg")
        self.fullscreen_icon = QIcon("assets/icons/fullscreen.svg")
        self.playlist_icon = QIcon("assets/icons/playlist1.svg")
        self.library_icon = QIcon("assets/icons/home2.svg")
        self.settings_icon = QIcon("assets/icons/settings.svg")
        self.effects_icon = QIcon("assets/icons/effects.png")
        self.donate_icon = QIcon("assets/icons/donate1.png")
        self.mute_icon = QIcon("assets/icons/mute.svg")
        self.unmute_icon = QIcon("assets/icons/unmute.svg")

        # --- Ovládací tlačítka ---
        self.prev_button = QPushButton(self.bg_panel)
        self.prev_button.setIcon(self.prev_icon)
        self.prev_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev_button.setToolTip("Předchozí stopa")
        self.prev_button.setProperty("class", "media")

        self.back10_button = QPushButton(self.bg_panel)
        self.back10_button.setIcon(self.back10_icon)
        self.back10_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back10_button.setToolTip("Zpět o 10s")
        self.back10_button.setProperty("class", "media")

        self.play_pause_button = QPushButton(self.bg_panel)
        self.play_pause_button.setIcon(self.play_icon)
        self.play_pause_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.play_pause_button.setToolTip("Play / Pause")
        self.play_pause_button.setProperty("class", "media")

        self.stop_button = QPushButton(self.bg_panel)
        self.stop_button.setIcon(self.stop_icon)
        self.stop_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stop_button.setToolTip("Stop")
        self.stop_button.setProperty("class", "media")

        self.forward10_button = QPushButton(self.bg_panel)
        self.forward10_button.setIcon(self.forward10_icon)
        self.forward10_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.forward10_button.setToolTip("Vpřed o 10s")
        self.forward10_button.setProperty("class", "media")

        self.next_button = QPushButton(self.bg_panel)
        self.next_button.setIcon(self.next_icon)
        self.next_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_button.setToolTip("Další stopa")
        self.next_button.setProperty("class", "media")

        self.mute_button = QPushButton(self.bg_panel)
        self.mute_button.setIcon(self.unmute_icon)
        self.mute_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.mute_button.setToolTip("Ztlumit / Zapnout zvuk")
        self.mute_button.setProperty("class", "circle")

        self.fullscreen_button = QPushButton(self.bg_panel)
        self.fullscreen_button.setIcon(self.fullscreen_icon)
        self.fullscreen_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.fullscreen_button.setToolTip("Fullscreen")
        self.fullscreen_button.setProperty("class", "circle")

        self.donate_button = QPushButton(self.bg_panel)
        self.donate_button.setIcon(self.donate_icon)
        self.donate_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.donate_button.setToolTip("Podpořit vývoj")
        self.donate_button.setProperty("class", "donate")

        self.playlist_button = QPushButton(self.bg_panel)
        self.playlist_button.setIcon(self.playlist_icon)
        self.playlist_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.playlist_button.setToolTip("Playlisty")
        self.playlist_button.setProperty("class", "circle")

        self.library_button = QPushButton(self.bg_panel)
        self.library_button.setIcon(self.library_icon)
        self.library_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.library_button.setToolTip("Zpět do knihovny")
        self.library_button.setProperty("class", "home")

        self.settings_button = QPushButton(self.bg_panel)
        self.settings_button.setIcon(self.settings_icon)
        self.settings_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_button.setToolTip("Nastavení")
        self.settings_button.setProperty("class", "circle")

        self.effects_button = QPushButton(self.bg_panel)
        self.effects_button.setIcon(self.effects_icon)
        self.effects_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.effects_button.setToolTip("Hlasitost efektů")
        self.effects_button.hide()  # Skrytý dokud nemáš separátní stopy

        # Volume slider:
        self.volume_slider = QSlider(Qt.Orientation.Horizontal, self.bg_panel)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setFixedWidth(90)

        # --- Layout ---
        seek_layout = QHBoxLayout()
        seek_layout.setSpacing(12)
        self.time_label = QLabel("00:00", self.bg_panel)
        self.duration_label = QLabel("00:00", self.bg_panel)
        self.seek_slider = ClickableSlider(Qt.Orientation.Horizontal, self.bg_panel)
        self.seek_slider.sliderMoved.connect(self.position_seeked.emit)
        seek_layout.addWidget(self.time_label)
        seek_layout.addWidget(self.seek_slider, 1)
        seek_layout.addWidget(self.duration_label)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)
        button_layout.addWidget(self.library_button)
        button_layout.addWidget(self.donate_button)
        button_layout.addSpacing(25)
        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.back10_button)
        button_layout.addWidget(self.play_pause_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.forward10_button)
        button_layout.addWidget(self.next_button)
        button_layout.addSpacing(25)
        button_layout.addWidget(self.playlist_button)
        button_layout.addWidget(self.fullscreen_button)
        button_layout.addSpacing(25)
        button_layout.addWidget(self.settings_button)
        button_layout.addSpacing(25)
        button_layout.addWidget(self.mute_button)
        button_layout.addWidget(self.volume_slider)
        button_layout.addWidget(self.effects_button)

        panel_layout = QVBoxLayout(self.bg_panel)
        panel_layout.setContentsMargins(20, 12, 20, 12)
        panel_layout.setSpacing(8)
        panel_layout.addLayout(seek_layout)
        panel_layout.addLayout(button_layout)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.bg_panel)

        # --- Signály (konektory) ---
        self.prev_button.clicked.connect(lambda: self.prev_pressed.emit())
        self.next_button.clicked.connect(lambda: self.next_pressed.emit())
        self.back10_button.clicked.connect(lambda: self.back10_pressed.emit())
        self.forward10_button.clicked.connect(lambda: self.forward10_pressed.emit())
        self.fullscreen_button.clicked.connect(self.fullscreen_toggled)
        self.volume_slider.valueChanged.connect(self.volume_changed.emit)
        self.play_pause_button.clicked.connect(self.play_pause_toggled.emit)
        self.stop_button.clicked.connect(lambda: self.stop_pressed.emit())
        self.donate_button.clicked.connect(lambda: self.donate_pressed.emit())
        self.playlist_button.clicked.connect(lambda: self.playlist_pressed.emit())
        self.library_button.clicked.connect(lambda: self.library_pressed.emit())
        self.settings_button.clicked.connect(lambda: self.settings_pressed.emit())
        self.mute_button.clicked.connect(self.mute_toggled)
        self.effects_button.clicked.connect(lambda: self.effects_volume_pressed.emit())

        # Stylujeme JEN panel (OverlayPanel)
        self.bg_panel.setStyleSheet("""
            #OverlayPanel {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(60, 110, 160, 190),
                    stop:1 rgba(28, 36, 62, 170)
                );
                border-radius: 20px;
                border: 1.5px solid qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #5eefff, 
                    stop:0.25 #32ffd2,
                    stop:0.55 #aaff80,
                    stop:0.8 #0fd9ff,
                    stop:1 #1fa2ff
                );
                box-shadow: 0 0 18px 2px #00ffc828;
            }
        
            QLabel {
                color: #f8fff8;
                font-weight: bold;
                font-size: 11px;
                text-shadow: 0 0 2px #1f1, 0 0 12px #2ff;
                background: transparent;
            }
        
            /* Multimediální tlačítka – oválné, menší šířka */
            QPushButton[class="media"], QPushButton[class="home"], QPushButton[class="donate"] {
                background: qradialgradient(
                    cx:0.5, cy:0.55, radius:0.82, fx:0.5, fy:0.5,
                    stop:0 #283950, stop:0.5 #26466e, stop:0.9 #365b82, stop:1 transparent);
                border-radius: 16px;
                border: 1.1px solid #1affb388;
                min-width: 34px; min-height: 36px; max-height: 40px;
                color: #eafff7;
                box-shadow: 0 1px 9px 0 #65f1ff22;
            }
            QPushButton[class="media"]:hover, QPushButton[class="home"]:hover, QPushButton[class="donate"]:hover, QPushButton[class="circle"]:hover{
                background: qradialgradient(cx:0.5, cy:0.52, radius:0.7, fx:0.5, fy:0.5,
                    stop:0 #41ffe7, stop:0.7 #162c2c, stop:1 transparent);
                border: 1.5px solid #22ffc6;
                box-shadow: 0 0 11px 2px #1affb399;
            }
            
            /* Kulatá tlačítka */
            QPushButton[class="circle"] {
                background: qradialgradient(
                    cx:0.5, cy:0.55, radius:0.82, fx:0.5, fy:0.5,
                    stop:0 #283950, stop:0.5 #26466e, stop:0.9 #365b82, stop:1 transparent
                );
                width: 32px; height: 32px;
                min-width: 32px; min-height: 32px;
                max-width: 32px; max-height: 32px;
                border-radius: 16px;
                border: 1.2px solid #20ffe988;
                color: #f2fff8;
                box-shadow: 0 1px 9px 0 #7fefff33;
                transition: background 0.18s, box-shadow 0.18s;
            }

            /* Home & Donate – stejné pozadí, max 10% světlejší, kulaté! */
            QPushButton[class="home"], QPushButton[class="donate"] {
                min-width: 44px; min-height: 44px;
                max-width: 44px; max-height: 44px;
                border-radius: 22px;
                /* Můžeš lehce zvýšit světlost, třeba: stop:0 #3b4f6d (o 10% světlejší) */
            }
            
            /* Ikony: světlejší barva */
            QPushButton > * {
                color: #eafff7;
            }
            
            /* Tenčí border */
            QPushButton {
                border-width: 1.1px;
            }
            
            QToolTip {
                color: #181e2a;                 
                background: #eafff7;             
                border: 1px solid #37ffe6;       
                font-size: 10px;
                border-radius: 4px;
                padding: 4px 4px;
                box-shadow: 0 1px 12px #36ffd8a2;
            }
         
            QSlider::sub-page:horizontal {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #81f7ff, stop:1 #aaff00
                );
                border-radius: 4px;
                box-shadow: 0 0 24px 8px #aaff00cc;
            }
            QSlider::handle:horizontal {
                background: #f8fff8;
                width: 8px; height: 8px;
                border-radius: 3px;
                border: 2px solid #c0ff95;
                box-shadow: 0 0 14px 3px #d8ffd4;
            }
        """)

        if self.window():
            self.window().setFocus()

        # will be injected
        self.player = None
        self.hide()

    def _on_play_clicked(self):
        if self.player:
            if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                self.player.pause()
            else:
                self.player.play()
            self.update_play_pause_icon(self.player.playbackState())
        self.play_pause_toggled.emit()

    def sizeHint(self):
        parent_w = self.parent().width() if self.parent() else 800
        h = self.layout().sizeHint().height()
        return QSize(int(parent_w * 0.9), h)

    def set_duration(self, dur_ms: int):
        self.seek_slider.setRange(0, dur_ms)
        self.duration_label.setText(self._format_time(dur_ms))

    def update_position(self, pos_ms: int):
        if not self.seek_slider.isSliderDown():
            self.seek_slider.setValue(pos_ms)
        self.time_label.setText(self._format_time(pos_ms))

    def update_play_pause_icon(self, state):
        icon = self.pause_icon if state == QMediaPlayer.PlaybackState.PlayingState else self.play_icon
        self.play_pause_button.setIcon(icon)

    def showEvent(self, event):
        super().showEvent(event)
        if self.player:
            self.update_play_pause_icon(self.player.playbackState())

    def _format_time(self, ms: int) -> str:
        s = ms // 1000
        m, s = divmod(s, 60)
        return f"{m:02d}:{s:02d}"

    def set_muted(self, muted: bool):
        if muted:
            self.mute_button.setIcon(self.mute_icon)
        else:
            self.mute_button.setIcon(self.unmute_icon)

