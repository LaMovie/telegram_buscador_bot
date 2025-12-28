from flask import Flask, request, jsonify, render_template
import os
from git import Repo

app = Flask(__name__, template_folder='templates')

# --- CONFIGURACIÓN DE GITHUB ---
# RECUERDA: Cambia esto por tu URL real
GITHUB_REPO_URL = "https://github.com/LaMovie/cine_chat.git"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO_DIR = os.getcwd()

# --- CONFIGURACIÓN DE SEGURIDAD (Filtro) ---
PALABRAS_PROHIBIDAS = ["tonto", "idiota", "spam", "basura"] 

def filtrar_mensaje(texto):
    for palabra in PALABRAS_PROHIBIDAS:
        # Reemplaza la palabra por asteriscos según su longitud
        texto = texto.replace(palabra, "*" * len(palabra))
    return texto

# Función para guardar en GitHub permanentemente
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
        repo.index.commit("Update data from server")
        # Cambia 'main' por 'master' si es necesario
        origin.push(refspec='HEAD:main', force=True)
        print(">>> Sincronizado con GitHub")
    except Exception as e:
        print(f">>> Error sincronizando: {e}")

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
        msg = request.json.get('msg', '').strip()
        
        # --- COMANDOS DE ADMINISTRADOR ---
        if msg == "CLR":
            write_file(CHAT_FILE, "SISTEMA: El chat ha sido reiniciado por el administrador.\n")
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

        # --- LÓGICA DE VIDEO ---
        if msg.startswith("/video:"):
            video_index = msg.split(":")[1]
            write_file(VIDEO_FILE, video_index)
            sync_to_github()
            return jsonify({"status": "ok"})
        
        # --- MENSAJES NORMALES ---
        msg_filtrado = filtrar_mensaje(msg)
        with open(CHAT_FILE, "a") as f:
            f.write(f"{user}: {msg_filtrado}\n")
        
        sync_to_github()
        return jsonify({"status": "ok"})
    
    # Respuesta para el método GET (actualización automática)
    msgs = read_file(CHAT_FILE, "")
    current_video = read_file(VIDEO_FILE, "0")
    controles = read_file(CONTROLES_FILE, "none")
    
    return jsonify({
        "messages": msgs, 
        "video_index": current_video,
        "controles": controles
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
    