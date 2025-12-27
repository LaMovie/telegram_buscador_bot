from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__, template_folder='templates')

# Archivos de datos
CHAT_FILE = "chat.txt"
VIDEO_FILE = "video_actual.txt"

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
    # Flask buscará index.html dentro de la carpeta /templates
    return render_template("index.html")

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'POST':
        user = request.json.get('user', 'Anónimo')
        msg = request.json.get('msg', '')
        if msg.startswith("/video:"):
            video_index = msg.split(":")[1]
            write_file(VIDEO_FILE, video_index)
        
        with open(CHAT_FILE, "a") as f:
            f.write(f"{user}: {msg}\n")
        return jsonify({"status": "ok"})
    
    msgs = ""
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "r") as f:
            msgs = f.read()
            
    current_video = read_file(VIDEO_FILE)
    return jsonify({"messages": msgs, "video_index": current_video})

if __name__ == '__main__':
    # Ajuste vital para Render
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
    