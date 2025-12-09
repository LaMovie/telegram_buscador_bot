import fetch from 'node-fetch';

// === CONFIGURACI\u00d3N DEL BOT ===
// TOKEN y CHAT_ID proporcionados por el usuario
const TOKEN = '8385584980:AAFMeNIFrJmUdjnpPBfskRENzoGBNTjlml0'; 
const MY_CHAT_ID = '6216957128'; 
// URL de b\u00fasqueda
const BASE_SEARCH_URL = 'https://latino.solo-latino.com/es/search?keyword=';
// ==================================

const API_URL = `https://api.telegram.org/bot${TOKEN}`;
let offset = 0; 

// --- 1. FUNCIONES DE TELEGRAM API ---

async function sendMessage(chat_id, text) {
    const response = await fetch(`${API_URL}/sendMessage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            chat_id: chat_id,
            text: text,
            parse_mode: 'Markdown'
        })
    });
    return response.json();
}

async function getUpdates() {
    const response = await fetch(`${API_URL}/getUpdates?offset=${offset}&timeout=30`);
    return response.json();
}

// --- 2. BUCLE PRINCIPAL DEL BOT ---

async function startBot() {
    console.log(`\n\u26a1 BOT DE B\u00daSQUEDA DIRECTA INICIADO \u26a1\nTOKEN: ${TOKEN.substring(0, 15)}...\n`);
    await sendMessage(MY_CHAT_ID, "✅ Bot de b\u00fasqueda directa iniciado. Enviar\u00e9 un enlace con tu b\u00fasqueda.");

    while (true) {
        try {
            const data = await getUpdates();

            if (data.ok && data.result.length > 0) {
                for (const update of data.result) {
                    offset = update.update_id + 1; 

                    if (update.message && update.message.text) {
                        const messageText = update.message.text.trim();
                        const chat_id = update.message.chat.id;
                        const user_name = update.message.from.first_name || 'Usuario';
                        
                        // Si el mensaje est\u00e1 vac\u00edo o es solo /start, lo manejamos sin hacer la b\u00fasqueda de URL
                        if (messageText === '' || messageText.startsWith('/start')) {
                            const welcomeMsg = `Hola ${user_name}. Env\u00edame cualquier texto para buscarlo directamente en el sitio.`;
                            if (messageText.startsWith('/start')) {
                                await sendMessage(chat_id, welcomeMsg);
                            }
                            continue;
                        }

                        console.log(`\n\u2705 Nuevo mensaje de ${user_name} (${chat_id}): "${messageText}"`);

                        // \u25ba \u25ba L\u00d3GICA DE B\u00daSQUEDA DIRECTA (SIEMPRE RESPONDE)
                        
                        // 1. Codificamos el texto para que funcione correctamente en una URL (maneja espacios y caracteres especiales)
                        const encodedQuery = encodeURIComponent(messageText);
                        
                        // 2. Construimos la URL completa
                        const searchUrl = `${BASE_SEARCH_URL}${encodedQuery}`;
                        
                        // 3. Generamos el mensaje de respuesta
                        const responseText = `\ud83d\udd0d T\u00edtulo buscado: *${messageText}*\n\n\ud83d\udd17 Enlace directo:\n${searchUrl}`;

                        // Enviar la respuesta al usuario
                        await sendMessage(chat_id, responseText);
                        console.log(`\u27a1 Respuesta enviada: Enlace de b\u00fasqueda generado.`);
                    }
                }
            }
        } catch (error) {
            console.error('\n\u274c Error en la comunicaci\u00f3n con Telegram:', error.message);
            await new Promise(resolve => setTimeout(resolve, 5000));
        }
    }
}

startBot();
