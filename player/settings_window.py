import os
import sys

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QComboBox, QPushButton, QMessageBox, QHBoxLayout, QLabel
from PyQt6.QtGui import QIcon

from .library.constants import LANG_METADATA
from .library.styles import get_settings_stylesheet
from .settings_manager import get_setting, set_setting
from .utils import resource_path


def restart_app():
    python = sys.executable
    os.execl(python, python, *sys.argv)

class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settingsDialog")
        self.setWindowTitle(self.tr("Nastavení"))
        self.setMinimumWidth(420)

        self.setStyleSheet(get_settings_stylesheet())

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        form_layout = QFormLayout()

        # Výběr jazyka
        lbl = QLabel(self.tr("Výběr jazyka:"))
        lbl.setObjectName("formLabel")
        main_layout.addWidget(lbl)

        self.lang_combo = QComboBox()
        self.lang_combo.setObjectName("langComboBox")
        for code, data in LANG_METADATA.items():
            icon_path = resource_path(data['icon'])
            self.lang_combo.addItem(QIcon(icon_path), data['native_name'], code)

        # Načteme a nastavíme aktuálně zvolený jazyk
        current_lang = get_setting("language", "cs")
        index = self.lang_combo.findData(current_lang)
        if index != -1:
            self.lang_combo.setCurrentIndex(index)

        form_layout.addRow(self.tr("Jazyk aplikace:"), self.lang_combo)
        main_layout.addLayout(form_layout)
        main_layout.addStretch()

        # Tlačítka Uložit / Zrušit
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.btn_save = QPushButton(self.tr("Uložit a restartovat"))
        self.btn_cancel = QPushButton(self.tr("Zrušit"))
        button_layout.addWidget(self.btn_save)
        button_layout.addWidget(self.btn_cancel)
        main_layout.addLayout(button_layout)

        self.btn_save.clicked.connect(self.save_and_close)
        self.btn_cancel.clicked.connect(self.reject)

    def save_and_close(self):
        selected_lang_code = self.lang_combo.currentData()
        set_setting("language", selected_lang_code)
        QMessageBox.information(self, self.tr("Restart vyžadován"),
                                self.tr("Změna jazyka se projeví po restartu aplikace."))
        self.accept()
        restart_app()
