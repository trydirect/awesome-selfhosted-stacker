#!/bin/sh
set -e

CONFIG_FILE="/data/config.ini"
WRITEFREELY="/go/cmd/writefreely/writefreely"

if [ ! -f "$CONFIG_FILE" ]; then
  echo "Generating WriteFreely config..."
  cd /data
  $WRITEFREELY config generate

  # Server config
  sed -i "s|^bind                 = localhost|bind                 = 0.0.0.0|" "$CONFIG_FILE"

  # Database config
  sed -i "s|^type     =.*|type     = ${WF_DB_TYPE:-mysql}|" "$CONFIG_FILE"
  sed -i "s|^username =.*|username = ${WF_DB_USER}|" "$CONFIG_FILE"
  sed -i "s|^password =.*|password = ${WF_DB_PASSWORD}|" "$CONFIG_FILE"
  sed -i "s|^database =.*|database = ${WF_DB_NAME}|" "$CONFIG_FILE"
  sed -i "s|^host     = localhost|host     = ${WF_DB_HOST:-mysql}|" "$CONFIG_FILE"

  # App config
  sed -i "s|^host                  = http://localhost:8080|host                  = http://${WF_HOST:-localhost}:8080|" "$CONFIG_FILE"

  echo "Initializing database..."
  $WRITEFREELY -c "$CONFIG_FILE" db init
fi

exec $WRITEFREELY -c "$CONFIG_FILE"
