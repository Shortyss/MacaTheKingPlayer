# test_card.py
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QFrame
from PyQt6.QtCore import Qt


# --- Zkopírovaná, ale ultra-zjednodušená třída FilmCard ---
class FilmCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("filmCardContainer")
        self.setFixedSize(230, 380)

        container_layout = QVBoxLayout(self)
        container_layout.setContentsMargins(3, 3, 3, 3)

        self.content_widget = QWidget(self)
        self.content_widget.setObjectName("filmCardContent")
        self.content_widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        container_layout.addWidget(self.content_widget)


# --- OPRAVA: Spojíme styly do jednoho řetězce ---
STYLESHEET = """
    /* Hlavní okno bude mít tmavé pozadí */
    #mainWindow {
        background-color: #1a1a1a;
    }

    /* Styl pro vnější kontejner karty */
    #filmCardContainer {
        background-color: #00fff7;
        border-radius: 38px;
        margin: 10px;
    }

    /* Styl pro vnitřní obsah karty */
    #filmCardContent {
        background-color: #2d3950;
        border-radius: 35px;
    }
"""

# --- Kód pro spuštění testovacího okna ---
if __name__ == '__main__':
    app = QApplication(sys.argv)

    main_window = QWidget()
    main_window.setObjectName("mainWindow")  # Dáme oknu jméno pro stylování
    main_window.setWindowTitle("Test Zakulacených Rohů")

    test_card = FilmCard()

    layout = QVBoxLayout(main_window)
    layout.addWidget(test_card, alignment=Qt.AlignmentFlag.AlignCenter)

    # Aplikujeme JEDEN kompletní stylopis
    main_window.setStyleSheet(STYLESHEET)

    main_window.resize(400, 500)
    main_window.show()

    sys.exit(app.exec())