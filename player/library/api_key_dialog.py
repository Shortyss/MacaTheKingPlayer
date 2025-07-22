from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox
)
from PyQt6.QtCore import Qt

class ApiKeyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nastavení TMDB API klíče")

        layout = QVBoxLayout(self)

        instructions = QLabel()
        instructions.setText(
            "Pro stahování dat je potřeba Váš osobní TMDB API klíč.\n\n"
            "1. Zaregistrujte se na <a href='https://www.themoviedb.org/signup'>TheMovieDB.org</a>.\n"
            "2. Po přihlášení si vygenerujte klíč v Nastavení -> API.\n"
            "3. Vložte klíč do pole níže."
        )
        instructions.setOpenExternalLinks(True)
        layout.addWidget(instructions)

        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Vložte Váš API klíč...")
        layout.addWidget(self.api_key_input)

        # Tlačítka OK a Zrušit
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def get_api_key(self):
        return self.api_key_input.text().strip()