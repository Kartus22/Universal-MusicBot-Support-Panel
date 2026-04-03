# MusicBot Support Panel 🎵

A lightweight web-based management tool for MusicBots. This panel allows you to manage your music files via SFTP or FTP, synchronize playlists, and perform bulk deletions directly from your browser.

## 🚀 Features
- **Dual Protocol Support:** Works with both SFTP (SSH) and classic FTP.
- **Easy Upload:** Multi-file upload support with real-time status notifications.
- **Playlist Sync:** Automatically update your autoplaylist.txt or .txt you like to.
- **Bulk Delete:** Select multiple songs and delete them at once.
- **Search:** Quickly find songs in your library.
- **Recently Added:** Shows your 5 latest uploads at a glance.

## 🛠️ Installation

### 1. Run from Source (Python)
If you want to run the script directly:
1. Clone this repository or download the `appexe.py`.
2. Install dependencies:
   ```bash
   pip install flask paramiko
Start the application:

Bash
python appexe.py
Open http://127.0.0.1:5000 in your browser.

2. Build your own EXE
To create a standalone executable for Windows:

Install PyInstaller:

Bash
pip install pyinstaller
Build the EXE:

Bash
python -m PyInstaller --onefile --name "MusicBot_Support_Panel" appexe.py
Find your file in the dist/ folder.
