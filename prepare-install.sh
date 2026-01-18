#!/bin/bash

REPO_URL="https://github.com/IdentSpace/iot-hub-core"


# Prüfen, ob git installiert ist
if ! command -v git &> /dev/null
then
    echo "== Git ist nicht installiert. Installation wird gestartet..."
	echo ""

    # Prüfen, ob der Benutzer root ist
    if [ "$EUID" -ne 0 ]; then
        echo "Bitte als root oder mit sudo ausführen."
        exit 1
    fi

    # Git installieren (Debian/Ubuntu)
    apt update
    apt install -y git

    # Prüfen, ob die Installation erfolgreich war
    if command -v git &> /dev/null
    then
        echo "== Git wurde erfolgreich installiert."
    else
        echo "== Fehler bei der Installation von Git."
        exit 1
    fi
else
    echo "== Git ist bereits installiert."
fi

# Zielordner aus Git-URL ableiten
REPO_NAME=$(basename "$REPO_URL" .git)
TARGET_DIR="/opt/$REPO_NAME"

# Repository in /opt/ klonen
if [ ! -d "$TARGET_DIR" ]; then
    echo "== Klonen des Repository in $TARGET_DIR..."
    git clone "$REPO_URL" "$TARGET_DIR"
    if [ $? -eq 0 ]; then
        echo "== Repository erfolgreich geklont."
    else
        echo "== Fehler beim Klonen des Repository."
        exit 1
    fi
else
    echo "== Zielordner $TARGET_DIR existiert bereits. Repository wird nicht erneut geklont."
fi
