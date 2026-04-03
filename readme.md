# 🎵 MusicBot Support Panel

> **A local desktop tool with a web-based interface for managing Discord MusicBots.** > This application runs directly on your own computer and connects to your remote bot server via SFTP/FTP. It provides a clean, modern web UI in your browser, allowing you to manage your remote music library and sync playlists without ever needing to touch an SSH terminal.

## ✨ Core Features

* **Local Execution, Remote Management:** Runs entirely on your local PC (`127.0.0.1`). Nothing needs to be installed on your bot's server.
* **Hybrid Protocol Engine:** Seamlessly connects to your remote server using **SFTP (Secure Shell)** or standard **FTP**.
* **Intelligent Playlist Sync:** Select any existing `.txt` playlist on your server via the dropdown menu. The panel scans your remote media directory and updates the selected file with `file://` URIs.
* **Asynchronous Web UI:** Built with modern JS/Fetch API for real-time progress tracking. The page doesn't reload during batch operations.
* **Batch Operations:** High-speed bulk deletion and multi-file uploads from your PC directly to the server.
* **Smart Library Management:** * Instant search and filtering of large audio collections (`.mp3`, `.opus`, `.m4a`, `.wav`).
  * Dedicated dashboard section highlighting the 5 most recently added tracks.

---

## 🚀 Installation & Quick Start

### Option A: The Standalone Executable (Windows Only)
The easiest way to use the tool. No Python installation required.

1. Download the `MusicBot_Support_Panel.exe` from the **Releases** tab.
2. Launch the executable. *(A command console will remain open to display connection logs and allow you to safely close the app).*
3. Open your web browser and navigate to `http://127.0.0.1:5000`.

### Option B: Run from Source (Cross-Platform)
For developers or users on Linux/macOS.

1. **Clone the repository** (or download the `appexe.py` file):
   ```bash
   git clone [https://github.com/Kartus22/MusicBot-Support-Panel.git](https://github.com/Kartus22/MusicBot-Support-Panel.git)
   cd MusicBot-Support-Panel
Install dependencies:

Bash
pip install -r requirements.txt
Launch the local server:

Bash
python appexe.py
Access the panel at http://127.0.0.1:5000.

⚙️ Initial Setup
Upon the first launch, the local web interface will automatically redirect you to the Setup Page. You will be prompted to configure your connection to the remote bot:

Connection: Your remote server's Host IP, Port, Username, and Password.

Media Path: The directory on your remote server where audio files are stored (e.g., media/).

Playlist Folder: The directory on your remote server where your bot expects its .txt files (e.g., config/playlists/).

All configurations are saved securely on your local hard drive in a config.json file. You only need to set this up once.

🏗️ Build It Yourself (For Developers)
Want to compile the Windows .exe yourself? It is highly recommended to use PyInstaller without the --noconsole flag to retain the diagnostic terminal:

Bash
pip install pyinstaller
python -m PyInstaller --onefile --name "MusicBot_Support_Panel" appexe.py
The compiled binary will be located in the dist/ folder.

🔒 Security & Privacy Policy
Zero Server Installation: This tool leaves no footprint on your server other than the uploaded audio and modified .txt files.

Local Storage Only: Your remote server credentials are saved only on your personal machine (config.json).

No Telemetry: This application does not track usage or communicate with any third-party APIs.

🛡️ Antivirus / Windows SmartScreen Notice
Since this application is compiled using PyInstaller and is not signed with an expensive enterprise certificate, Windows SmartScreen or some Antivirus programs might flag it as "unknown" or "suspicious".

When scanning the .exe on VirusTotal, 2 out of 71 vendors (usually AI-based heuristic scanners like Bkav or SecureAge) might flag it as a generic malware.

This is a known false positive for standalone Python applications. The big vendors (Microsoft, Kaspersky, Malwarebytes) rate it as 100% clean.

You can view the live [VirusTotal Scan Report here.](https://www.virustotal.com/gui/file/b455542bfbb45e56282f226e2d751f151fd68af0b2cf50513ad1818be0e0c35c/detection)

💡 Still suspicious? We completely understand! You are highly encouraged to ignore the .exe, review the open-source code yourself, and run the appexe.py directly via Python!

<img width="464" height="573" alt="image" src="https://github.com/user-attachments/assets/61b2306d-9d05-468b-be77-a1f15ab76344" /> 
<img width="681" height="1007" alt="image" src="https://github.com/user-attachments/assets/e8d3ad0f-1d32-45a9-92a4-03a0e49b7c7b" />

