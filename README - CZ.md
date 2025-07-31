# The King's Player
# by Shortyss

Minimalistický, ale výkonný lokální přehrávač filmů v prostředí Linuxu. Hlavní předností přehrávače je jeho knihovna, kde najdete veškeré informace o svých filmech, 
včetně ukázek a plakátů. Takže už nebudete muset hádat co je to asi za film.

## Klíčové vlastnosti
* **Přehrávání videa:** Podpora všech běžných formátů díky FFmpeg backendu (MKV, MP4, AVI a další).
* **Správa knihovny:** Jednoduše přidejte složky s vašimi filmy a přehrávač si je automaticky načte a zorganizuje.
* **Automatická metadata:** Program se napojí na The Movie Database (TMDB) a automaticky stáhne plakáty, popisy, rok vydání a další detaily k vašim filmům.
* **Playlisty:** Vytvářejte si vlastní playlisty, měňte jejich pořadí a snadno mezi nimi přepínejte.
* **Intuitivní ovládání:**
    * Plná kontrola nad přehráváním (play/pause, posun vpřed/vzad, hlasitost).
    * Drag & Drop podpora pro rychlé přehrání souborů a vkládání do playlistů.
    * Klávesové zkratky pro ovládání hlasitosti a posun ve videu.
    * Automatické skrytí kurzoru a ovládacích prvků.
* **Deaktivace spořiče:** Automaticky zabrání uspání obrazovky během sledování filmu.
* **Vícejazyčné rozhraní:** Podpora pro více jazyků s možností snadného přepínání v sekci nastavení.

## Instalace a spuštění (pro běžné uživatele)
Nejjednodušší cesta je stáhnout si hotový soubor AppImage, který funguje na většině moderních Linuxových distribucí.

1.  Stáhněte si nejnovější verzi `KingPlayer-x86_64.AppImage` ze sekce [**Releases**](https://github.com/Shortyss/MacaTheKingPlayer/releases/latest).
2.  Udělejte soubor spustitelným:
    ```bash
    chmod +x KingPlayer-x86_64.AppImage
    ```
3.  Spusťte aplikaci:
    ```bash
    ./KingPlayer-x86_64.AppImage
    ```

## Vývoj a kompilace z kódu (pro fajnšmekry)

Pokud si chcete program zkompilovat sami, budete potřebovat Conda prostředí.

1.  **Vytvořte a aktivujte prostředí:**
    ```bash
    # Vytvoření prostředí se všemi klíčovými závislostmi
    conda create --name kingplayer python=3.11 pyqt=6.4 pyqt-webengine=6.4 dbus -c conda-forge
    
    # Aktivace
    conda activate kingplayer
    ```
2.  **Instalace zbylých balíčků:**
    ```bash
    # Instalace závislostí pro API, kompilaci a SVG
    pip install requests tmdbv3api yt-dlp pyinstaller pyqt-svg
    ```
3.  **Spuštění z kódu:**
    ```bash
    python main.py
    ```
4.  **Vytvoření AppImage:**
    Pro finální kompilaci postupujte podle kroků, které jsme ladili (vytvoření `.desktop` souboru, `pyinstaller` a následně `appimagetool`).

## Licence
Tento projekt je licencován pod **CC BY-NC-ND 4.0** - viz soubor `LICENSE` pro detaily.