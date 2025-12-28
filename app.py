from flask import Flask, request, jsonify, render_template
import os
from git import Repo

app = Flask(__name__, template_folder='templates')

# --- CONFIGURACIÓN DE GITHUB ---
GITHUB_REPO_URL = "https://github.com/LaMovie/cine_chat.git"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO_DIR = os.getcwd()

def sync_to_github():
    try:
        remote_url = GITHUB_REPO_URL.replace("https://", f"https://{GITHUB_TOKEN}@")
        try:
            repo = Repo(REPO_DIR)
        except:
            repo = Repo.init(REPO_DIR)
        
        with repo.config_writer() as cw:
            cw.set_value("user", "name", "RenderServer")
            cw.set_value("user", "email", "render@example.com")
        
        if 'origin' in repo.remotes:
            origin = repo.remote(name='origin')
            origin.set_url(remote_url)
        else:
            origin = repo.create_remote('origin', remote_url)

        repo.index.add([CHAT_FILE, VIDEO_FILE, CONTROLES_FILE])
        repo.index.commit("Update chat data")
        origin.push(refspec='HEAD:main', force=True) 
        print(">>> ¡ÉXITO! Sincronizado con GitHub")
    except Exception as e:
        print(f">>> ERROR al sincronizar: {e}")

# Archivos de datos
CHAT_FILE = "chat.txt"
VIDEO_FILE = "video_actual.txt"
CONTROLES_FILE = "controles_estado.txt"

def write_file(filename, content):
    with open(filename, "w") as f:
        f.write(content)

def read_file(filename, default="0"):
    if not os.path.exists(filename):
        return default
    with open(filename, "r") as f:
        return f.read()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'POST':
        user = request.json.get('user', 'Anónimo')
        msg = request.json.get('msg', '')
        
        # --- COMANDOS DE ADMINISTRACIÓN ---
        if msg == "CLR":
            # Borra el contenido del chat y deja una notificación del sistema
            write_file(CHAT_FILE, "SISTEMA: Chat reiniciado\n")
            sync_to_github()
            return jsonify({"status": "ok", "hide": True})

        if msg == "CMD":
            write_file(CONTROLES_FILE, "flex")
            sync_to_github()
            return jsonify({"status": "ok", "hide": True})
        
        if msg == "CMX":
            write_file(CONTROLES_FILE, "none")
            sync_to_github()
            return jsonify({"status": "ok", "hide": True})

        if msg.startswith("/video:"):
            video_index = msg.split(":")[1]
            write_file(VIDEO_FILE, video_index)
            sync_to_github()
            return jsonify({"status": "ok"})
        
        # --- MENSAJES NORMALES ---
        with open(CHAT_FILE, "a") as f:
            f.write(f"{user}: {msg}\n")
        
        sync_to_github()
        return jsonify({"status": "ok"})
    
    # Respuesta GET
    msgs = ""
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "r") as f:
            msgs = f.read()
            
    current_video = read_file(VIDEO_FILE)
    controles_visibilidad = read_file(CONTROLES_FILE, "none")
    
    return jsonify({
        "messages": msgs, 
        "video_index": current_video,
        "controles": controles_visibilidad
    })
        
    @app.route('/keep-alive')
def keep_alive():
    return "Servidor Activo", 200
    
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
    