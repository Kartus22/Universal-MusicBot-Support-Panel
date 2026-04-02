from flask import Flask, render_template_string, request, redirect, url_for, jsonify
import paramiko
from ftplib import FTP
import os
import json

app = Flask(__name__)
app.secret_key = "musicbot-support-full-list-v10"

CONFIG_FILE = "config.json"
TEMP_DIR = os.path.join(os.getcwd(), "temp_upload")

if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

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

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    conf = load_config() or {}
    if request.method == 'POST':
        new_conf = {
            'proto': request.form['proto'],
            'host': request.form['host'].strip(),
            'port': request.form['port'].strip(),
            'user': request.form['user'].strip(),
            'password': request.form['password'].strip(),
            'media_path': request.form['media_path'].strip().strip('/'),
            'playlist_folder': request.form['playlist_folder'].strip().strip('/')
        }
        try:
            client, proto = get_client(new_conf)
            if proto == 'FTP': client.quit()
            else: client.close()
            save_config(new_conf)
            return redirect(url_for('index'))
        except Exception as e:
            return f"❌ Connection failed: {e} <br><a href='/setup'>Go back</a>"
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head><title>Setup</title><style>body{font-family:sans-serif;background:#121212;color:white;display:flex;justify-content:center;align-items:center;height:100vh;} .card{background:#1e1e1e;padding:30px;border-radius:15px;width:400px;border:1px solid #3498db;} input,select{width:100%;padding:12px;margin:8px 0;background:#252525;color:white;border:1px solid #444;border-radius:5px;} button{width:100%;padding:12px;background:#3498db;color:white;border:none;border-radius:5px;cursor:pointer;font-weight:bold;}</style></head>
    <body><div class="card"><h2>⚙️ Support Setup</h2><form method="post"><select name="proto"><option value="SFTP" {% if conf.proto=='SFTP' %}selected{% endif %}>SFTP</option><option value="FTP" {% if conf.proto=='FTP' %}selected{% endif %}>FTP</option></select><input name="host" placeholder="Host" value="{{conf.host or ''}}" required><input name="port" placeholder="Port" value="{{conf.port or '2022'}}" required><input name="user" placeholder="User" value="{{conf.user or ''}}" required><input type="password" name="password" placeholder="Password" required><input name="media_path" placeholder="Media Path" value="{{conf.media_path or 'media'}}" required><input name="playlist_folder" placeholder="Playlist Folder" value="{{conf.playlist_folder or 'config/playlists'}}" required><button type="submit">Save & Connect</button></form></div></body></html>
    """, conf=conf)

@app.route('/')
def index():
    conf = load_config()
    if not conf: return redirect(url_for('setup'))
    search_query = request.args.get('search', '').lower()
    try:
        client, proto = get_client(conf)
        playlists = []
        songs_data = []
        if proto == 'SFTP':
            try: playlists = [f for f in client.listdir(conf['playlist_folder']) if f.lower().endswith('.txt')]
            except: pass
            all_attr = client.listdir_attr(conf['media_path'])
            for attr in all_attr:
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
        
        # 'songs_recent' bekommt die Top 5 für die gelbe Box
        songs_recent = sorted(songs_data, key=lambda x: x['mtime'], reverse=True)[:5]
        # 'songs_all' enthält UNABHÄNGIG davon alle Songs für die Hauptliste
        songs_all = sorted(songs_data, key=lambda x: x['name'].lower())
        
        if search_query:
            songs_all = [s for s in songs_all if search_query in s['name'].lower()]

        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>MusicBot Support Panel</title>
            <style>
                body { font-family: 'Segoe UI', sans-serif; background: #121212; color: #e0e0e0; padding: 20px; }
                .container { max-width: 900px; margin: auto; padding-bottom: 80px; }
                .card { background: #1e1e1e; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #3498db; }
                .btn { padding: 10px 15px; border-radius: 5px; border: none; cursor: pointer; font-weight: bold; }
                .btn-sync { background: #9b59b6; color: white; flex-grow: 1; }
                .btn-upload { background: #2ecc71; color: white; width: 100%; margin-top: 15px; }
                .btn-delete-bulk { background: #e74c3c; color: white; margin-bottom: 15px; display: none; width: 100%; }
                .song-item { background: #2c2c2c; margin: 5px 0; padding: 12px; border-radius: 5px; display: flex; align-items: center; gap: 15px; }
                input[type="checkbox"] { transform: scale(1.3); cursor: pointer; }
                input, select { padding: 10px; background: #252525; color: white; border: 1px solid #444; border-radius: 5px; }
                .sync-bar { display: flex; gap: 10px; margin-bottom: 10px; align-items: center; }
                #status-toast { position: fixed; bottom: 20px; right: 20px; padding: 15px 25px; border-radius: 10px; background: #333; color: white; display: none; align-items: center; gap: 10px; z-index: 1000; border-bottom: 4px solid #3498db; }
                .spinner { border: 3px solid #f3f3f3; border-top: 3px solid #3498db; border-radius: 50%; width: 16px; height: 16px; animation: spin 1s linear infinite; }
                @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            </style>
        </head>
        <body>
            <div id="status-toast"><div id="status-icon"></div><span id="status-text">Processing...</span></div>
            <div class="container">
                <h1>🎵 MusicBot Support Panel</h1>
                <p>Connected: <b>{{conf.host}} ({{conf.proto}})</b> | <a href="/setup" style="color:#3498db; text-decoration:none;">Settings</a></p>
                
                <div class="card" style="border-left-color: #9b59b6;">
                    <h3>🔄 Synchronize Playlist</h3>
                    <div class="sync-bar">
                        <select id="playlist-select" style="flex-grow: 2;">
                            <option value="" disabled selected>Select target .txt file...</option>
                            {% for p in playlists %}<option value="{{p}}">{{p}}</option>{% endfor %}
                        </select>
                        <button onclick="syncPlaylist()" class="btn btn-sync">Update Selected File</button>
                    </div>
                </div>

                <div class="card">
                    <h3>🚀 Upload</h3>
                    <input type="file" id="upload-input" multiple>
                    <button onclick="startUpload()" class="btn btn-upload">Upload Files</button>
                </div>

                <button id="bulk-delete-btn" onclick="bulkDelete()" class="btn btn-delete-bulk">🗑️ Delete Selected Songs</button>

                {% if songs_recent %}
                <div class="card" style="border-left-color: #f1c40f;">
                    <h3>✨ Recently Added</h3>
                    {% for song in songs_recent %}
                    <div class="song-item" style="background:#252525;">
                        <input type="checkbox" class="song-checkbox" value="{{song.name}}" onchange="toggleBulkButton()">
                        <span><b>{{song.name}}</b></span>
                    </div>
                    {% endfor %}
                </div>
                {% endif %}

                <div class="card" style="border-left-color: #95a5a6;">
                    <form action="/" method="get" style="display:flex; gap:10px;">
                        <input type="text" name="search" placeholder="Search..." value="{{search}}" style="flex-grow:1;">
                        <button class="btn" style="background:#444; color:white;">🔍</button>
                    </form>
                </div>

                <div id="song-list">
                    {% for song in songs_all %}
                    <div class="song-item">
                        <input type="checkbox" class="song-checkbox" value="{{song.name}}" onchange="toggleBulkButton()">
                        <span style="flex-grow:1;">{{song.name}}</span>
                    </div>
                    {% endfor %}
                </div>
            </div>

            <script>
                const toast = document.getElementById('status-toast');
                function showStatus(text, type) {
                    toast.style.display = 'flex';
                    document.getElementById('status-text').innerText = text;
                    const icon = document.getElementById('status-icon');
                    if (type === 'loading') { icon.className = 'spinner'; icon.innerText = ''; }
                    else { icon.className = ''; icon.innerText = (type === 'success' ? '✅' : '❌'); setTimeout(() => { location.reload(); }, 1500); }
                }
                function toggleBulkButton() {
                    const count = document.querySelectorAll('.song-checkbox:checked').length;
                    document.getElementById('bulk-delete-btn').style.display = count > 0 ? 'block' : 'none';
                }
                async function startUpload() {
                    const input = document.getElementById('upload-input');
                    if(input.files.length === 0) return;
                    const fd = new FormData();
                    for(let f of input.files) fd.append('file', f);
                    showStatus("Uploading...", "loading");
                    const res = await fetch('/upload', {method:'POST', body:fd});
                    showStatus(res.ok ? "Success!" : "Failed!", res.ok ? "success" : "error");
                }
                async function syncPlaylist() {
                    const sel = document.getElementById('playlist-select').value;
                    if(!sel) return;
                    const fd = new FormData(); fd.append('target_file', sel);
                    showStatus("Syncing...", "loading");
                    const res = await fetch('/sync', {method:'POST', body:fd});
                    showStatus(res.ok ? "Success!" : "Failed!", res.ok ? "success" : "error");
                }
                async function bulkDelete() {
                    const files = Array.from(document.querySelectorAll('.song-checkbox:checked')).map(cb => cb.value);
                    if(!confirm("Delete " + files.length + " selected files?")) return;
                    showStatus("Deleting...", "loading");
                    const res = await fetch('/delete_bulk', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({files:files})});
                    showStatus(res.ok ? "Deleted!" : "Failed!", res.ok ? "success" : "error");
                }
            </script>
        </body>
        </html>
        """, conf=conf, songs_all=songs_all, songs_recent=songs_recent, playlists=playlists, search=search_query)
    except Exception as e: return f"Error: {e} <br><a href='/setup'>Fix Settings</a>"

@app.route('/upload', methods=['POST'])
def upload():
    conf = load_config(); files = request.files.getlist('file')
    client, proto = get_client(conf)
    for f in files:
        if f.filename == '': continue
        path = os.path.join(TEMP_DIR, f.filename); f.save(path)
        rem = conf['media_path'] + "/" + f.filename
        if proto == 'FTP':
            with open(path, 'rb') as rb: client.storbinary(f"STOR {rem}", rb)
        else: client.put(path, rem)
        os.remove(path)
    if proto == 'FTP': client.quit()
    else: client.close()
    return jsonify({"status": "success"})

@app.route('/sync', methods=['POST'])
def sync():
    conf = load_config(); target = request.form.get('target_file')
    client, proto = get_client(conf)
    if proto == 'FTP':
        client.cwd(conf['media_path'])
        songs = sorted([f for f in client.nlst() if f.lower().endswith(('.mp3', '.opus', '.m4a', '.wav'))])
    else:
        all_attr = client.listdir_attr(conf['media_path'])
        sorted_attr = sorted([a for a in all_attr if a.filename.lower().endswith(('.mp3', '.opus', '.m4a', '.wav'))], key=lambda x: x.st_mtime)
        songs = [a.filename for a in sorted_attr]
    local_p = os.path.join(TEMP_DIR, "temp.txt")
    with open(local_p, "w", encoding="utf-8", newline='\n') as f:
        for s in songs: f.write(f"file://{s}\n")
    rem_p = conf['playlist_folder'] + "/" + target
    if proto == 'FTP':
        client.cwd('/'); 
        with open(local_p, 'rb') as rb: client.storbinary(f"STOR {rem_p}", rb)
        client.quit()
    else: client.put(local_p, rem_p); client.close()
    if os.path.exists(local_p): os.remove(local_p)
    return jsonify({"status": "success"})

@app.route('/delete_bulk', methods=['POST'])
def delete_bulk():
    conf = load_config(); files = request.json.get('files', [])
    client, proto = get_client(conf)
    for name in files:
        rem = conf['media_path'] + "/" + name
        try:
            if proto == 'FTP': client.delete(rem)
            else: client.remove(rem)
        except: pass
    if proto == 'FTP': client.quit()
    else: client.close()
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=False, port=5000)