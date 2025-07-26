# settings_window.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QComboBox, QPushButton, QMessageBox, QHBoxLayout
from PyQt6.QtGui import QIcon

from .library.constants import LANG_METADATA
from .settings_manager import get_setting, set_setting

class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settingsDialog")
        self.setWindowTitle(self.tr("Nastavení"))
        self.setMinimumWidth(400)

        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # --- Výběr jazyka ---
        self.lang_combo = QComboBox()
        for code, data in LANG_METADATA.items():
            self.lang_combo.addItem(QIcon(data['icon']), data['native_name'], code)

        # Načteme a nastavíme aktuálně zvolený jazyk
        current_lang = get_setting("language", "cs") # Výchozí je 'cs'
        index = self.lang_combo.findData(current_lang)
        if index != -1:
            self.lang_combo.setCurrentIndex(index)

        form_layout.addRow(self.tr("Jazyk aplikace:"), self.lang_combo)
        main_layout.addLayout(form_layout)
        main_layout.addStretch()

        # --- Tlačítka Uložit / Zrušit ---
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