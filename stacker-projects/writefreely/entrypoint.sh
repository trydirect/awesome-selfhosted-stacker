#!/bin/sh
set -e

CONFIG_FILE="/data/config.ini"

if [ ! -f "$CONFIG_FILE" ]; then
  echo "Generating WriteFreely config..."
  writefreely config init
  sed -i "s|bind = localhost:8080|bind = 0.0.0.0:8080|" "$CONFIG_FILE"
  sed -i "s|driver = sqlite3|driver = mysql|" "$CONFIG_FILE"
  sed -i "s|database = writefreely.db|database = ${WF_DB_USER}:${WF_DB_PASSWORD}@tcp(${WF_DB_HOST}:3306)/${WF_DB_NAME}?parseTime=true|" "$CONFIG_FILE"
  sed -i "s|host = localhost|host = ${WF_HOST:-localhost}|" "$CONFIG_FILE"
  echo "Initializing database..."
  writefreely db init
fi

exec writefreely
