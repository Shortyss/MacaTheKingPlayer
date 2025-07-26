from PyQt6.QtWidgets import (QHBoxLayout, QVBoxLayout, QListWidget, QStackedWidget,
                             QWidget, QLabel, QPushButton, QApplication, QLineEdit, QFrame)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices

from player.library.styles import get_main_stylesheet


class DonateOverlay(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("donateOverlay")
        self.setStyleSheet(get_main_stylesheet())

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel(f"<h2>{self.tr('Podpořit vývoj')}</h2>"))
        header_layout.addStretch()
        close_button = QPushButton(self.tr("Zavřít"))
        close_button.clicked.connect(self.hide)
        header_layout.addWidget(close_button)
        main_layout.addLayout(header_layout)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        main_layout.addLayout(content_layout)

        self.nav_list = QListWidget()
        self.nav_list.setFixedWidth(180)
        self.nav_list.addItems([self.tr("Podpora v CZK"), "Wise (EUR / USD)", "Buy Me a Coffee"])
        content_layout.addWidget(self.nav_list)

        self.stack = QStackedWidget()
        content_layout.addWidget(self.stack, 1)

        self.stack.addWidget(self._create_czk_page())
        self.stack.addWidget(self._create_wise_page())
        self.stack.addWidget(self._create_bmac_page())

        self.nav_list.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.nav_list.setCurrentRow(0)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
        else:
            super().keyPressEvent(event)

    def _create_czk_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addWidget(QLabel(f"<h2>{self.tr('Podpora v CZK')}</h2>"))
        layout.addWidget(QLabel(self.tr("Nejjednodušší způsob pro podporu v českých korunách.")))

        qr_label = QLabel()
        qr_pixmap = QPixmap("assets/donations/czk_qr.png")
        qr_label.setPixmap(qr_pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio))
        qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(qr_label, 1)

        acc_layout = QHBoxLayout()
        self.czk_account_input = QLineEdit("188724691/0800")
        self.czk_account_input.setReadOnly(True)
        copy_btn = QPushButton(QIcon("assets/icons/copy.svg"), "")
        copy_btn.setToolTip(self.tr("Kopírovat číslo účtu"))
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(self.czk_account_input.text()))
        acc_layout.addWidget(self.czk_account_input)
        acc_layout.addWidget(copy_btn)
        layout.addLayout(acc_layout)

        layout.addStretch()
        return page

    def _create_wise_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addWidget(QLabel(f"<h2>{self.tr('Podpora přes Wise (EUR / USD)')}</h2>"))
        layout.addWidget(QLabel(self.tr("Ideální pro mezinárodní platby.")))

        eur_label = QLabel("<b>EUR IBAN:</b><br> BE95 9055 3919 9058<br>")
        usd_text = """
                <b>USD Account No.:</b><br>
                215037517213<br><br>
                <b>ACH Routing:</b><br>
                101019628<br><br>
                <b>SWIFT/BIC:</b><br>
                TRWIUS35XXX
            """

        usd_label = QLabel(usd_text)
        layout.addWidget(eur_label)
        layout.addWidget(usd_label)
        layout.addStretch()
        return page

    def _create_bmac_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        bmac_link = "https://coff.ee/shortyss"

        label = QLabel(
            self.tr("Pokud preferuješ jednoduchou platbu kartou nebo přes PayPal, můžeš mě podpořit přes službu Buy Me a Coffee."))
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        button = QPushButton(self.tr("Přejít na Buy Me a Coffee"))
        button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(bmac_link)))
        layout.addWidget(button)
        return page