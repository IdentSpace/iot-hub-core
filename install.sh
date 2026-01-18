#!/bin/bash

# Absoluter Pfad zum aktuellen Ordner (wo install.sh liegt)
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"

# Prüfen, ob der Benutzer root ist (für Systemd-Zugriff notwendig)
if [ "$EUID" -ne 0 ]; then
    echo "Bitte als root oder mit sudo ausführen."
    exit 1
fi

# Python3 und venv prüfen
if ! command -v python3 &> /dev/null; then
    echo "Python3 ist nicht installiert. Bitte installieren."
    exit 1
fi

if ! python3 -m venv --help &> /dev/null; then
    echo "Python venv-Modul fehlt. Bitte sicherstellen, dass python3-venv installiert ist."
    exit 1
fi

# Virtuelles Environment einrichten
echo "Richte Python venv in $BASE_DIR/venv ein..."
python3 -m venv "$BASE_DIR/venv"

# Aktivieren und Abhängigkeiten installieren, falls requirements.txt existiert
if [ -f "$BASE_DIR/requirements.txt" ]; then
    echo "Installiere Python-Abhängigkeiten aus requirements.txt..."
    source "$BASE_DIR/venv/bin/activate"
    pip install --upgrade pip
    pip install -r "$BASE_DIR/requirements.txt"
    deactivate
else
    echo "Keine requirements.txt gefunden, überspringe Installation von Abhängigkeiten."
fi

# Systemd-Service kopieren
SERVICE_FILE="$BASE_DIR/iot-hub-core.service"
if [ -f "$SERVICE_FILE" ]; then
    echo "Kopiere $SERVICE_FILE nach /etc/systemd/system/..."
    cp "$SERVICE_FILE" /etc/systemd/system/
    systemctl daemon-reload
    systemctl enable iot-hub-core.service
    echo "Service iot-hub-core.service wurde aktiviert. Start mit: systemctl start iot-hub-core.service"
else
    echo "Service-Datei $SERVICE_FILE nicht gefunden."
fi
