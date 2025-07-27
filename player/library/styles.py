def get_main_stylesheet():
    return """
    /* -------- ZÁKLADNÍ VZHLED PRO CELOU APPKU -------- */
    QWidget { 
        background: rgba(34, 43, 66, 230); 
        color: #eafff7; 
        font-family: Segoe UI, Arial; 
        font-size: 15px; 
    }
    QScrollArea { border: none; background: transparent; }
    QLabel { background: transparent; }

    /* --- Checkboxy, včetně zelených fajfek --- */
    QCheckBox {
        background-color: transparent;
        border: none;
    }
    QCheckBox:focus { outline: none; }
    QCheckBox::indicator {
        width: 22px; height: 22px; border-radius: 11px;
    }
    QCheckBox::indicator:unchecked { background-color: #FF0000; }
    QCheckBox::indicator:checked { background-color: #1cf512; image: url(assets/icons/checkmark.svg); }
    QCheckBox::indicator:hover { border: 2px solid #00fff7; }

    /* --------- PANEL FILTRŮ + GROUPBOX --------- */
    #filterPanel {
        background-color: #232941; 
    }
    #groupBox {
        background-color: rgba(0, 0, 0, 0.15);
        border: 1px solid #3a4a63;
        border-radius: 10px;
        padding: 8px;
    }
    #filterPanel > QLabel {
        font-size: 16px;
        font-weight: bold;
        color: #00fff7; 
        margin-top: 5px; margin-bottom: 2px; padding-left: 5px;
    }
    #groupBox > QLabel {
        font-weight: normal;
        color: #eafff7;
        font-size: 14px;
    }

    /* --------- TAG BUTTONY (Žánry, filtry, atd.) --------- */
    TagButton, .TagButton, QPushButton#TagButton {
        background-color: #2d3950;
        border: 1px solid #3a4a63;
        border-radius: 13px;
        padding: 5px 12px;
        font-size: 13px;
        color: #a9b8d4;
    }
    TagButton:hover, .TagButton:hover, QPushButton#TagButton:hover {
        border-color: #16e0ec;
    }
    TagButton[active="true"], .TagButton[active="true"], QPushButton#TagButton[active="true"] {
        background-color: #16e0ec;
        border-color: #00fff7;
        color: #000;
        font-weight: bold;
    }

    /* --------- TEXTOVÁ POLE --------- */
    QLineEdit { 
        background: #232941; 
        border-radius: 8px; 
        border: 1.5px solid #181a1f; 
        padding: 5px; 
    }

    /* --------- TLAČÍTKA --------- */
    QPushButton { 
        background: qradialgradient(cx:0.5, cy:0.5, radius:0.8, stop:0 #283950, stop:1 #2d3950);
        border-radius: 14px; 
        border: 1.2px solid #20ffe988; 
        color: #eafff7; 
        font-weight: bold; 
        min-height: 30px; 
        padding: 4px; 
    }
    QPushButton:hover { 
        background: qradialgradient(cx:0.5, cy:0.5, radius:0.7, stop:0 #41ffe7, stop:1 #162c2c);
        border: 1.8px solid #22ffc6; 
        color: #000000; 
    }
    /* Playlist a speciální tlačítka mají vlastní gradient – viz níže */

    /* --------- FILMOVÁ KARTA (FILMCARD) --------- */
    QFrame#FilmCard {
        background-color: #2d3950;    
        border: 3px solid #00fff7;   
        border-radius: 22px;         
        margin: 4px;                 
    }
    #backSideTitle {
        font-size: 22px;
        font-weight: bold;
        color: #00fff7;
    }
    #backSideLabel {
        font-size: 14px;
        color: #a9b8d4;
    }
    #overviewText {
        background-color: rgba(0, 0, 0, 0.2);
        border: 1px solid #3a4a63;
        border-radius: 8px;
    }
    #muteButton {
        min-width: 30px;
        max-width: 30px;
        border-radius: 15px; 
    }
    #titleLabel { color: #fff; font-size: 16px; font-weight: 600; }
    #yearLabel { color: #a9b8d4; font-size: 14px; }
    """

def get_playlist_stylesheet():
    return """
    /* ---- SPECIÁLNÍ STYLY PRO PLAYLIST WINDOW ---- */
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
    #donateOverlay, #settingsDialog {
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(60, 110, 160, 240),
            stop:1 rgba(28, 36, 62, 220)
        );
        border-radius: 20px;
        border: 1.5px solid #5eefff;
    }
    """

def get_overlay_stylesheet():
    return """
    #OverlayPanel  {
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
            }
        
            QLabel {
                color: #f8fff8;
                font-weight: bold;
                font-size: 11px;
                background: transparent;
            }

            QPushButton[class="media"], QPushButton[class="home"], QPushButton[class="donate"] {
                background: qradialgradient(
                    cx:0.5, cy:0.55, radius:0.82, fx:0.5, fy:0.5,
                    stop:0 #283950, stop:0.5 #26466e, stop:0.9 #365b82, stop:1 transparent);
                border-radius: 16px;
                border: 1.1px solid #1affb388;
                min-width: 34px; min-height: 36px; max-height: 40px;
                color: #eafff7;
            }
            QPushButton[class="media"]:hover, QPushButton[class="home"]:hover, QPushButton[class="donate"]:hover, QPushButton[class="circle"]:hover{
                background: qradialgradient(cx:0.5, cy:0.52, radius:0.7, fx:0.5, fy:0.5,
                    stop:0 #41ffe7, stop:0.7 #162c2c, stop:1 transparent);
                border: 1.5px solid #22ffc6;
            }

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
            }

            QPushButton[class="home"], QPushButton[class="donate"] {
                min-width: 44px; min-height: 44px;
                max-width: 44px; max-height: 44px;
                border-radius: 22px;
            }
            
            QPushButton > * {
                color: #eafff7;
            }

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
            }
         
            QSlider::sub-page:horizontal {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #81f7ff, stop:1 #aaff00
                );
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #f8fff8;
                width: 8px; height: 8px;
                border-radius: 3px;
                border: 2px solid #c0ff95;
            }
    
    """

def get_info_overlay_sytlesheet():
    return """
    QLabel {
            background: rgba(0,0,0,170);
            color: #aaffbb;
            border-radius: 13px;
            font-size: 19px;
            padding: 14px 22px;
            border: 2px solid #41ffae;
            min-width: 80px;
            qproperty-alignment: AlignCenter;
            text-shadow: 0 0 4px #4f8, 0 0 12px #0ff;
        }
    """

def get_main_stylesheet_fhd():
    return """
    QWidget { 
        background: rgba(34, 43, 66, 230); 
        color: #eafff7; 
        font-family: Segoe UI, Arial; 
        font-size: 13px;
    }
    QScrollArea { border: none; background: transparent; }
    QLabel { background: transparent; }

    QCheckBox::indicator {
        width: 18px; height: 18px; border-radius: 9px;
    }
    QCheckBox::indicator:unchecked { background-color: #FF0000; }
    QCheckBox::indicator:checked { background-color: #1cf512; }

    #filterPanel { background-color: #232941; }
    #groupBox {
        background-color: rgba(0, 0, 0, 0.15);
        border: 1px solid #3a4a63;
        border-radius: 10px;
        padding: 8px;
    }
    #filterPanel > QLabel {
        font-size: 15px;
        font-weight: bold;
        color: #00fff7; 
        margin-top: 3px; margin-bottom: 2px; padding-left: 4px;
    }
    #groupBox > QLabel {
        font-weight: normal;
        color: #eafff7;
        font-size: 13px;
    }

    TagButton {
        background-color: #2d3950;
        border: 1px solid #3a4a63;
        border-radius: 13px;
        padding: 4px 11px;
        font-size: 12px;
        color: #a9b8d4;
    }
    TagButton:hover {
        border-color: #16e0ec;
    }
    TagButton[active="true"] {
        background-color: #16e0ec;
        border-color: #00fff7;
        color: #000;
        font-weight: bold;
    }

    QLineEdit {
        background: #232941; 
        border-radius: 8px; 
        border: 1.5px solid #181a1f; 
        padding: 4px; 
        font-size: 12px;
    }

    QPushButton {
        background: qradialgradient(cx:0.5, cy:0.5, radius:0.8, stop:0 #283950, stop:1 #2d3950);
        border-radius: 10px;
        border: 1.2px solid #20ffe988;
        color: #eafff7;
        font-weight: bold;
        min-height: 20px;
        padding: 2px 7px;
        font-size: 11px;
        margin: 2px 2px;
    }
    QPushButton:hover {
        background: qradialgradient(cx:0.5, cy:0.5, radius:0.7, stop:0 #41ffe7, stop:1 #162c2c);
        border: 1.8px solid #22ffc6;
        color: #000;
    }

    /* --- SeekBar & VolumeBar --- */
    QSlider::groove:horizontal {
        height: 8px;
        background: #232941;
        border-radius: 5px;
    }
    QSlider::handle:horizontal {
        background: #00fff7;
        border: 2px solid #20ffe9;
        width: 18px;
        height: 18px;
        margin: -5px 0;
        border-radius: 9px;
    }
    QSlider::sub-page:horizontal {
        background: #00fff7;
        border-radius: 5px;
    }
    QSlider::add-page:horizontal {
        background: #1a2033;
        border-radius: 5px;
    }

    /* --- FilmCard --- */
    QFrame#FilmCard {
        background-color: #2d3950;
        border: 3px solid #00fff7;
        border-radius: 18px;
        margin: 4px;
    }
    #backSideTitle {
        font-size: 19px;
        font-weight: bold;
        color: #00fff7;
    }
    #backSideLabel {
        font-size: 12px;
        color: #a9b8d4;
    }
    #overviewText {
        background-color: rgba(0, 0, 0, 0.2);
        border: 1px solid #3a4a63;
        border-radius: 8px;
    }
    #muteButton {
        width: 20px;
        border-radius: 10px; 
    }
    #titleLabel { color: #fff; font-size: 14px; font-weight: 600; }
    #yearLabel { color: #a9b8d4; font-size: 12px; }

    /* --- Playlist window, info overlay, atd. můžeš přenést obdobně pokud potřebuješ --- */
    """


def get_settings_stylesheet():
    return """
    #settingsDialog {
        background: #232941;
        padding: 30px 32px 25px 32px;
    }

    /* Roletka s jazyky */
    QComboBox {
        background: #2d3950;
        color: #eafff7;
        border: 1.5px solid #3a4a63;
        border-radius: 8px;
        font-size: 15px;
        padding: 7px 16px;
        min-width: 180px;
    }

    QComboBox:hover {
        border-color: #5a7aa5;
    }

    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 30px;
        border-left-width: 1px;
        border-left-color: #3a4a63;
        border-left-style: solid;
        border-top-right-radius: 8px;
        border-bottom-right-radius: 8px;
    }

    QComboBox::down-arrow {
        image: url(assets/icons/down_arrow.svg); 
        width: 20px;
        height: 20px;
    }

    /* Vzhled rozbaleného seznamu */
    QComboBox QAbstractItemView {
        background: #2d3950;
        color: #eafff7;
        border-radius: 8px;
        border: 1px solid #5a7aa5;
        padding: 4px;
        outline: 0px;
    }

    /* Zvýraznění vybrané (kliknuté) položky */
    QComboBox QAbstractItemView::item:selected {
        background-color: #16e0ec;
        color: #000;
        border-radius: 4px;
    }

    /* Zbytek kódu beze změny */
    QPushButton {
        background: qradialgradient(cx:0.5, cy:0.5, radius:0.8, stop:0 #283950, stop:1 #2d3950);
        border-radius: 13px;
        border: 1.2px solid #20ffe988;
        color: #eafff7;
        font-weight: bold;
        font-size: 15px;
        min-width: 120px;
        min-height: 32px;
        padding: 5px 18px;
        margin: 6px 0;
    }
    QPushButton:hover {
        background: qradialgradient(cx:0.5, cy:0.5, radius:0.7, stop:0 #41ffe7, stop:1 #162c2c);
        border: 1.8px solid #22ffc6;
        color: #000;
    }
    QLabel {
        background: transparent; 
        color: #00fff7;
        font-size: 17px;
        font-weight: bold;
        margin-bottom: 8px;
    }
    QFormLayout > QLabel {
        color: #eafff7;
        font-size: 12px;
        font-weight: normal;
        margin-bottom: 0px;
    }
    QMessageBox {
        background-color: #232941;
    }
    QMessageBox QLabel {
        color: #eafff7;
        font-size: 14px;
        background-color: transparent;
    }
    QMessageBox QPushButton {
        background: qradialgradient(cx:0.5, cy:0.5, radius:0.8, stop:0 #283950, stop:1 #2d3950);
        border-radius: 10px;
        border: 1.2px solid #20ffe988;
        color: #eafff7;
        font-weight: bold;
        padding: 5px 20px;
        min-width: 80px;
        margin-top: 10px;
    }
    QMessageBox QPushButton:hover {
        background: qradialgradient(cx:0.5, cy:0.5, radius:0.7, stop:0 #41ffe7, stop:1 #162c2c);
        border: 1.8px solid #22ffc6;
        color: #000;
    }
    """
