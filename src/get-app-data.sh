#!/bin/bash

# Verifica che sia stato fornito almeno un parametro
if [ $# -eq 0 ]; then
    echo "Usage: $0 <additional_param>"
    exit 1
fi

# URL del servizio REST
BASE_URL="http://master:8088/ws/v1/cluster/apps"

# Parametro aggiuntivo passato allo script
APP_NAME="$1"

# Concatena il parametro aggiuntivo all'IP nell'URL
URL="$BASE_URL/$APP_NAME"

# Esegui la richiesta GET e salva la risposta JSON in un file temporaneo
OUTPUT_FILE="logs-car-prediction/output_$APP_NAME.xml"
touch "$OUTPUT_FILE"

curl --compressed -H "Accept: application/xml" -X GET "$URL" > "$OUTPUT_FILE"
