import eel
import os
import json
import paramiko
from ftplib import FTP
import tkinter as tk
from tkinter import filedialog

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return None

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

def get_client(conf):
    if conf.get('proto') == 'FTP':
        ftp = FTP()
        ftp.connect(conf['host'], int(conf['port']), timeout=10)
        ftp.login(conf['user'], conf['password'])
        ftp.set_pasv(True)
        return ftp, 'FTP'
    else:
        transport = paramiko.Transport((conf['host'], int(conf['port'])))
        transport.connect(username=conf['user'], password=conf['password'])
        return paramiko.SFTPClient.from_transport(transport), 'SFTP'

# --- EEL EXPOSED FUNCTIONS ---

@eel.expose
def check_config():
    return load_config()

@eel.expose
def save_setup(conf_data):
    try:
        client, proto = get_client(conf_data)
        if proto == 'FTP': client.quit()
        else: client.close()
        save_config(conf_data)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

@eel.expose
def get_data(search_query=""):
    conf = load_config()
    if not conf: return None
    try:
        client, proto = get_client(conf)
        playlists = []
        songs_data = []
        if proto == 'SFTP':
            try: playlists = [f for f in client.listdir(conf['playlist_folder']) if f.lower().endswith('.txt')]
            except: pass
            for attr in client.listdir_attr(conf['media_path']):
                if attr.filename.lower().endswith(('.mp3', '.opus', '.m4a', '.wav')):
                    songs_data.append({'name': attr.filename, 'mtime': attr.st_mtime})
            client.close()
        else:
            try:
                client.cwd(conf['playlist_folder'])
                playlists = [f for f in client.nlst() if f.lower().endswith('.txt')]
                client.cwd('/')
            except: pass
            client.cwd(conf['media_path'])
            for name in client.nlst():
                if name.lower().endswith(('.mp3', '.opus', '.m4a', '.wav')):
                    songs_data.append({'name': name, 'mtime': 0})
            client.quit()
        
        songs_recent = sorted(songs_data, key=lambda x: x['mtime'], reverse=True)[:5]
        songs_all = sorted(songs_data, key=lambda x: x['name'].lower())
        
        if search_query:
            search_query = search_query.lower()
            songs_all = [s for s in songs_all if search_query in s['name'].lower()]

        return {
            "playlists": playlists,
            "songs_recent": songs_recent,
            "songs_all": songs_all,
            "conf": conf
        }
    except Exception as e:
        return {"error": str(e)}

@eel.expose
def upload_files():
    # Öffnet einen nativen Dateiauswahldialog
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    files = filedialog.askopenfilenames(title="Select Audio Files", filetypes=[("Audio", "*.mp3 *.opus *.m4a *.wav")])
    
    if not files: return {"status": "cancelled"}

    conf = load_config()
    total_files = len(files)
    
    try:
        client, proto = get_client(conf)
        for index, filepath in enumerate(files):
            filename = os.path.basename(filepath)
            
            # Sende aktuelles Update an das Frontend (VOR dem Upload der Datei)
            eel.update_progress(index + 1, total_files, filename)()
            
            rem = conf['media_path'] + "/" + filename
            if proto == 'FTP':
                with open(filepath, 'rb') as rb: client.storbinary(f"STOR {rem}", rb)
            else: 
                client.put(filepath, rem)
                
        if proto == 'FTP': client.quit()
        else: client.close()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@eel.expose
def sync_playlist(target):
    conf = load_config()
    try:
        client, proto = get_client(conf)
        if proto == 'FTP':
            client.cwd(conf['media_path'])
            songs = sorted([f for f in client.nlst() if f.lower().endswith(('.mp3', '.opus', '.m4a', '.wav'))])
        else:
            sorted_attr = sorted([a for a in client.listdir_attr(conf['media_path']) if a.filename.lower().endswith(('.mp3', '.opus', '.m4a', '.wav'))], key=lambda x: x.st_mtime)
            songs = [a.filename for a in sorted_attr]
        
        # Temp File lokal erzeugen
        local_p = "temp_playlist.txt"
        with open(local_p, "w", encoding="utf-8", newline='\n') as f:
            for s in songs: f.write(f"file://{s}\n")
            
        rem_p = conf['playlist_folder'] + "/" + target
        if proto == 'FTP':
            client.cwd('/') 
            with open(local_p, 'rb') as rb: client.storbinary(f"STOR {rem_p}", rb)
            client.quit()
        else: 
            client.put(local_p, rem_p)
            client.close()
            
        if os.path.exists(local_p): os.remove(local_p)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@eel.expose
def delete_bulk(files):
    conf = load_config()
    try:
        client, proto = get_client(conf)
        for name in files:
            rem = conf['media_path'] + "/" + name
            try:
                if proto == 'FTP': client.delete(rem)
                else: client.remove(rem)
            except: pass
        if proto == 'FTP': client.quit()
        else: client.close()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == '__main__':
    eel.init('web')
    eel.start('index.html', size=(950, 750), mode='chrome')