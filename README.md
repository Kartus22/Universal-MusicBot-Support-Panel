# Universal MusicBot Remote Panel

A lightweight desktop application designed to manage, upload, and synchronize audio files with your remote MusicBot server via **SFTP** or **FTP**. It provides a clean, modern web-based interface running locally on your computer.

## ✨ Key Features
* **Universal Compatibility**: Works with any server (Linux, Windows, NAS) that supports standard SFTP or FTP protocols.
* **Bulk Upload with Progress**: Upload multiple files at once with a real-time progress bar.
* **Smart Playlist Sync**: Updates an existing `.txt` playlist file on your server by overwriting it with the current list of audio files found in your media directory.
* **Filename Optimization**: Designed to handle and clean up filenames to avoid issues with special characters or spaces on remote systems.
* **No Web Server Needed**: Runs as a standalone desktop app using Python and Eel.

## 🚀 Getting Started

### Prerequisites
* A MusicBot running on a remote server.
* FTP or SFTP access to your server's media and playlist folders.

### Installation
1. Download the latest `MusicBot_Panel.exe` from the **Releases** section on the right.
2. Run the application on your Windows PC.
   * *Note: Since the app is not digitally signed, you might need to click "More info" -> "Run anyway" when Windows SmartScreen appears.*

## ⚙️ Configuration
On the first start, you will be prompted to enter your server details:
* **Host & Port**: Your server's IP or domain and the port (usually 22 for SFTP or 21 for FTP).
* **Credentials**: Your username and password for the server.
* **Media Path**: The remote folder where your music files are stored.
* **Playlist Folder**: The remote folder where your `.txt` playlists are located.

## 🔄 How Playlist Sync Works
1. The app fetches a list of all existing `.txt` files from your configured playlist folder.
2. You select the specific playlist file you wish to update.
3. The app scans your remote media folder and overwrites the selected `.txt` file with the new file paths (using the `file://` prefix).

## 🛠️ Built With
* [Python](https://www.python.org/) - Backend logic
* [Eel](https://github.com/python-eel/Eel) - Desktop GUI framework
* [Paramiko](https://www.paramiko.org/) - SFTP implementation

---
*Developed to simplify remote music management.*

<img width="936" height="743" alt="image" src="https://github.com/user-attachments/assets/a0640e5a-3a02-4417-97de-7f83550461b2" />
<img width="936" height="1166" alt="image" src="https://github.com/user-attachments/assets/61cd01e5-85be-4138-b6fe-073d61ed9fc8" />

