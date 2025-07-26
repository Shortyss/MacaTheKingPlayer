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
        border: 4px solid #00fff7;   
        border-radius: 38px;         
        margin: 10px;                 
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
    #donateOverlay {
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