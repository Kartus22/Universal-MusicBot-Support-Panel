🎵 MusicBot Support Panel
A local desktop tool with a web-based interface for managing Discord MusicBots. > This application runs directly on your own computer and connects to your remote bot server via SFTP/FTP. It provides a clean, modern web UI in your browser, allowing you to manage your remote music library and sync playlists without ever needing to touch an SSH terminal.

✨ Core Features
Local Execution, Remote Management: Runs entirely on your local PC (127.0.0.1). Nothing needs to be installed on your bot's server.

Hybrid Protocol Engine: Seamlessly connects to your remote server using SFTP (Secure Shell) or standard FTP.

Intelligent Playlist Sync: Select any existing .txt playlist on your server via the dropdown menu. The panel scans your remote media directory and updates the selected file with file:// URIs.

Asynchronous Web UI: Built with modern JS/Fetch API for real-time progress tracking. The page doesn't reload during batch operations.

Batch Operations: High-speed bulk deletion and multi-file uploads from your PC directly to the server.

Smart Library Management: * Instant search and filtering of large audio collections (.mp3, .opus, .m4a, .wav).

Dedicated dashboard section highlighting the 5 most recently added tracks.

🚀 Installation & Quick Start
Option A: The Standalone Executable (Windows Only)
The easiest way to use the tool. No Python installation required.

Download the MusicBot_Support_Panel.exe from the Releases tab.

Launch the executable. (A command console will remain open to display connection logs and allow you to safely close the app).

Open your web browser and navigate to http://127.0.0.1:5000.

Option B: Run from Source (Cross-Platform)
For developers or users on Linux/macOS.

Clone the repository (or download the appexe.py file):

Bash
git clone https://github.com/Kartus22/MusicBot-Support-Panel.git
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
