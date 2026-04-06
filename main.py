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
        backups = []
        songs_data = []
        if proto == 'SFTP':
            try: 
                pl_files = client.listdir(conf['playlist_folder'])
                playlists = [f for f in pl_files if f.lower().endswith('.txt')]
                backups = [f for f in pl_files if f.lower().endswith('.bak')]
            except: pass
            for attr in client.listdir_attr(conf['media_path']):
                if attr.filename.lower().endswith(('.mp3', '.opus', '.m4a', '.wav')):
                    songs_data.append({'name': attr.filename, 'mtime': attr.st_mtime})
            client.close()
        else:
            try:
                client.cwd(conf['playlist_folder'])
                pl_files = client.nlst()
                playlists = [f for f in pl_files if f.lower().endswith('.txt')]
                backups = [f for f in pl_files if f.lower().endswith('.bak')]
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
            "playlists": sorted(playlists),
            "backups": sorted(backups),
            "songs_recent": songs_recent,
            "songs_all": songs_all,
            "conf": conf
        }
    except Exception as e:
        return {"error": str(e)}

@eel.expose
def upload_files():
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
        
        rem_p = conf['playlist_folder'] + "/" + target
        bak_p = rem_p + ".bak"
        local_bak = "temp_bak.txt"
        try:
            if proto == 'FTP':
                client.cwd('/')
                with open(local_bak, 'wb') as fb: client.retrbinary(f"RETR {rem_p}", fb.write)
                with open(local_bak, 'rb') as rb: client.storbinary(f"STOR {bak_p}", rb)
            else:
                client.get(rem_p, local_bak)
                client.put(local_bak, bak_p)
            if os.path.exists(local_bak): os.remove(local_bak)
        except Exception:
            pass 
            
        if proto == 'FTP':
            client.cwd(conf['media_path'])
            songs = sorted([f for f in client.nlst() if f.lower().endswith(('.mp3', '.opus', '.m4a', '.wav'))])
        else:
            sorted_attr = sorted([a for a in client.listdir_attr(conf['media_path']) if a.filename.lower().endswith(('.mp3', '.opus', '.m4a', '.wav'))], key=lambda x: x.st_mtime)
            songs = [a.filename for a in sorted_attr]
        
        local_p = "temp_playlist.txt"
        with open(local_p, "w", encoding="utf-8", newline='\n') as f:
            for s in songs: f.write(f"file://{s}\n")
            
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
def add_youtube_links(target, urls_list):
    conf = load_config()
    try:
        client, proto = get_client(conf)
        rem_p = conf['playlist_folder'] + "/" + target
        local_p = "temp_yt.txt"

        if proto == 'FTP':
            client.cwd('/')
            try:
                with open(local_p, 'wb') as fb: client.retrbinary(f"RETR {rem_p}", fb.write)
            except: pass
        else:
            try: client.get(rem_p, local_p)
            except: pass

        content = ""
        if os.path.exists(local_p):
            with open(local_p, "r", encoding="utf-8") as f: content = f.read()

        with open(local_p, "a", encoding="utf-8", newline='\n') as f:
            if content and not content.endswith('\n'): f.write('\n')
            for url in urls_list:
                if url.strip():
                    f.write(f"{url.strip()}\n")

        if proto == 'FTP':
            client.cwd('/')
            with open(local_p, 'rb') as rb: client.storbinary(f"STOR {rem_p}", rb)
            client.quit()
        else:
            client.put(local_p, rem_p)
            client.close()

        if os.path.exists(local_p): os.remove(local_p)
        return {"status": "success", "count": len(urls_list)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@eel.expose
def get_playlist_content(target):
    conf = load_config()
    try:
        client, proto = get_client(conf)
        rem_p = conf['playlist_folder'] + "/" + target
        local_p = "temp_view.txt"
        lines = []

        if proto == 'FTP':
            client.cwd('/')
            try:
                with open(local_p, 'wb') as fb: client.retrbinary(f"RETR {rem_p}", fb.write)
            except: pass
            client.quit()
        else:
            try: client.get(rem_p, local_p)
            except: pass
            client.close()

        if os.path.exists(local_p):
            with open(local_p, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
            os.remove(local_p)

        return {"status": "success", "lines": lines}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@eel.expose
def delete_playlist_line(target, line_index):
    return delete_playlist_lines(target, [line_index])

@eel.expose
def delete_playlist_lines(target, indices):
    conf = load_config()
    try:
        client, proto = get_client(conf)
        rem_p = conf['playlist_folder'] + "/" + target
        local_p = "temp_del_multi.txt"

        if proto == 'FTP':
            client.cwd('/')
            try:
                with open(local_p, 'wb') as fb: client.retrbinary(f"RETR {rem_p}", fb.write)
            except: pass
        else:
            try: client.get(rem_p, local_p)
            except: pass

        if os.path.exists(local_p):
            with open(local_p, "r", encoding="utf-8") as f:
                lines = [line for line in f.readlines() if line.strip()]
            
            # Konvertiere sicherheitshalber in Integers
            indices = [int(i) for i in indices]
            
            with open(local_p, "w", encoding="utf-8", newline='\n') as f:
                for i, line in enumerate(lines):
                    if i not in indices:
                        f.write(line)

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

@eel.expose
def create_playlist(filename):
    if not filename.lower().endswith('.txt'):
        filename += '.txt'
    conf = load_config()
    try:
        client, proto = get_client(conf)
        rem_p = conf['playlist_folder'] + "/" + filename
        local_p = "temp_new_pl.txt"
        
        with open(local_p, "w", encoding="utf-8") as f: pass 
            
        if proto == 'FTP':
            client.cwd('/')
            with open(local_p, 'rb') as rb: client.storbinary(f"STOR {rem_p}", rb)
            client.quit()
        else:
            client.put(local_p, rem_p)
            client.close()
            
        if os.path.exists(local_p): os.remove(local_p)
        return {"status": "success", "file": filename}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@eel.expose
def delete_playlist(filename):
    conf = load_config()
    try:
        client, proto = get_client(conf)
        rem_p = conf['playlist_folder'] + "/" + filename
        if proto == 'FTP':
            client.delete(rem_p)
            client.quit()
        else:
            client.remove(rem_p)
            client.close()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@eel.expose
def delete_backup(filename):
    conf = load_config()
    try:
        client, proto = get_client(conf)
        rem_p = conf['playlist_folder'] + "/" + filename
        if proto == 'FTP':
            client.delete(rem_p)
            client.quit()
        else:
            client.remove(rem_p)
            client.close()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == '__main__':
    eel.init('web')
    eel.start('index.html', size=(1100, 800), mode='chrome')