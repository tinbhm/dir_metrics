#!/bin/bash

TMP_CONFIG="/tmp/config_host.yml"
CONFIG_ORIG="/app/config.yml"

echo "[INFO] Ersetze lokale Pfade in der config.yml..."

# Robuster sed-Befehl: ersetzt "path: /xyz" durch "path: /host/xyz"
sed -E 's|^([[:space:]]*path:[[:space:]]+)/|\1/host/|' "$CONFIG_ORIG" > "$TMP_CONFIG"

echo "[INFO] Angepasste config.yml:"
cat "$TMP_CONFIG"

echo "[INFO] Starte Exporter..."
exec python3 /app/exporter.py --config "$TMP_CONFIG"