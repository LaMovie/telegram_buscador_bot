#!/bin/bash

# Reemplaza 'TU_TOKEN_AQUI' con tu token real
TOKEN="8385584980:AAFMeNIFrJmUdjnpPBfskRENzoGBNTjlml0" 

# Reemplaza 'ID_DE_CHAT' con tu Chat ID real
CHAT_ID="6216957128" 

# El mensaje de respuesta que solo contiene un enlace
MENSAJE="Aquí está el enlace solicitado: https://www.ejemplo.com/recurso"

API_URL="https://api.telegram.org/bot$TOKEN/sendMessage"

# Enviar el mensaje
curl -s -X POST $API_URL \
    -d chat_id="$CHAT_ID" \
    -d text="$MENSAJE" 

