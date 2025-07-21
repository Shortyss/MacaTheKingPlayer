

def get_main_stylesheet():
    return """
        QWidget { background: rgba(34, 43, 66, 230); color: #eafff7; font-family: Segoe UI, Arial; font-size: 15px; }
        QScrollArea { border: none; background: transparent; }
        QLabel { background: transparent; }
        QCheckBox {
            background-color: transparent;
            border: none;
        }
        QCheckBox:focus {
            outline: none; 
        }
        QCheckBox::indicator {
            width: 22px;   /* Větší box */
            height: 22px;
            border-radius: 11px; /* Lehce zakulatíme rohy */
        }
        QCheckBox::indicator:unchecked {
            background-color: #FF0000; 
        }            
        QCheckBox::indicator:checked {
            background-color: #1cf512; /* Pozadí se vyplní tyrkysovou */
            image: url(assets/icons/checkmark.svg); /* Ikonka fajfky (pokud ji máš) */
        }            
        QCheckBox::indicator:hover {
            border: 2px solid #00fff7; /* Při najetí myší okraj ještě více zesvětlí */
        }
        #filterPanel {
            background-color: #232941; /* Lehce odlišené pozadí panelu */
        }

        /* Hlavní styl pro seskupovací boxy */
        #groupBox {
            background-color: rgba(0, 0, 0, 0.15);
            border: 1px solid #3a4a63;
            border-radius: 10px;
            padding: 8px;
        }

        /* Hlavní nadpisy pro jednotlivé sekce */
        #filterPanel > QLabel {
            font-size: 16px;
            font-weight: bold;
            color: #00fff7; /* Zářivá tyrkysová */
            margin-top: 5px;
            margin-bottom: 2px; /* Přisune box blíže k nadpisu */
            padding-left: 5px;
        }

        /* Menší nadpisy uvnitř boxů */
        #groupBox > QLabel {
            font-weight: normal;
            color: #eafff7;
            font-size: 14px;
        }

        TagButton {
            background-color: #2d3950;
            border: 1px solid #3a4a63;
            border-radius: 13px; /* Kulaté rohy */
            padding: 5px 12px;
            font-size: 13px;
            color: #a9b8d4;
        }
        TagButton:hover {
            border-color: #16e0ec;
        }
        TagButton[active="true"] { /* Styl pro aktivní štítek */
            background-color: #16e0ec;
            border-color: #00fff7;
            color: #000;
            font-weight: bold;
        }
        QLineEdit { background: #232941; border-radius: 8px; border: 1.5px solid #181a1f; padding: 5px; }
        QPushButton { background: qradialgradient(cx:0.5, cy:0.5, radius:0.8, stop:0 #283950, stop:1 #2d3950);
                      border-radius: 14px; border: 1.2px solid #20ffe988; color: #eafff7; font-weight: bold; min-height: 30px; padding: 4px; }
        QPushButton:hover { background: qradialgradient(cx:0.5, cy:0.5, radius:0.7, stop:0 #41ffe7, stop:1 #162c2c);
                           border: 1.8px solid #22ffc6; color: #000000; }
        #filmCardContainer { background-color: transparent; border-radius: 38px; border: 3px solid #00fff7; margin: 10px; }
        #filmCardContent { background-color: #2d3950; border-radius: 35px; }
        #titleLabel { color: #fff; font-size: 18px; font-weight: 600; }
    """