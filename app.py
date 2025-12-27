from flask import Flask, render_template, request, redirect
import os

app = Flask(__name__)

# Ruta del archivo donde se guardan los mensajes
CHAT_FILE = "chat.txt"

# Crear el archivo chat.txt si no existe para evitar errores
if not os.path.exists(CHAT_FILE):
    with open(CHAT_FILE, "w") as f:
        f.write("")

@app.route('/')
def index():
    # Leer mensajes del archivo
    with open(CHAT_FILE, "r") as f:
        mensajes = f.readlines()
    return render_template('index.html', mensajes=mensajes)

@app.route('/enviar', methods=['POST'])
def enviar():
    usuario = request.form.get('usuario', 'Anónimo')
    mensaje = request.form.get('mensaje', '')
    
    if mensaje:
        with open(CHAT_FILE, "a") as f:
            f.write(f"{usuario}: {mensaje}\n")
            
    return redirect('/')

if __name__ == '__main__':
    # AJUSTE PARA RENDER: Usa el puerto que el servidor asigne
    port = int(os.environ.get("PORT", 8080))
    # host='0.0.0.0' es obligatorio para que sea accesible desde internet
    app.run(host='0.0.0.0', port=port)
    