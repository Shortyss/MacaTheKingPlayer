# The King's Player
# by Shortyss

A minimalist yet powerful local movie player for the Linux environment. The player's main feature is its library, where you can find all the information about your movies, including trailers and posters. No more guessing what a movie is about!

## Key Features
* **Video Playback:** Support for all common formats thanks to the FFmpeg backend (MKV, MP4, AVI, and more).
* **Library Management:** Simply add your movie folders, and the player will automatically scan and organize them.
* **Automatic Metadata:** The program connects to The Movie Database (TMDB) to automatically download posters, descriptions, release years, and other details for your movies.
* **Playlists:** Create your own playlists, change their order, and switch between them easily.
* **Intuitive Controls:**
    * Full playback control (play/pause, seek forward/backward, volume).
    * Drag & Drop support for quick file playback and adding to playlists.
    * Keyboard shortcuts for volume control and seeking.
    * Automatic hiding of the cursor and controls.
* **Screensaver Deactivation:** Automatically prevents the screen from sleeping while watching a movie.
* **Multilingual Interface:** Support for multiple languages with easy switching in the settings section.

## Installation and Usage (for regular users)
The easiest way is to download the pre-built AppImage file, which works on most modern Linux distributions.

1.  Download the latest version `KingPlayer-x86_64.AppImage` from the [**Releases**](https://github.com/Shortyss/MacaTheKingPlayer/releases/latest) section.
2.  Make the file executable:
    ```bash
    chmod +x KingPlayer-x86_64.AppImage
    ```
3.  Run the application:
    ```bash
    ./KingPlayer-x86_64.AppImage
    ```

## Development and Building from Source (for enthusiasts)

If you want to build the program yourself, you will need a Conda environment.

1.  **Create and activate the environment:**
    ```bash
    # Create the environment with all key dependencies
    conda create --name kingplayer python=3.11 pyqt=6.4 pyqt-webengine=6.4 dbus -c conda-forge
    
    # Activate
    conda activate kingplayer
    ```
2.  **Install the remaining packages:**
    ```bash
    # Install dependencies for the API, compilation, and SVG
    pip install requests tmdbv3api yt-dlp pyinstaller pyqt-svg
    ```
3.  **Run from source:**
    ```bash
    python main.py
    ```
4.  **Create the AppImage:**
    For the final compilation, follow the steps we debugged (creating a `.desktop` file, running `pyinstaller`, and then `appimagetool`).

## License
This project is licensed under the **CC BY-NC-ND 4.0** - see the `LICENSE` file for details.