#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -f .env ]; then cp .env.example .env; echo "  Created .env from .env.example"; fi
need() { [ -z "$(grep "^$1=" .env 2>/dev/null | cut -d= -f2- || true)" ]; }
if need "DB_PASSWORD"; then
  val=$(openssl rand -hex 16)
  if grep -q "^DB_PASSWORD=" .env; then sed -i '' "s|^DB_PASSWORD=.*|DB_PASSWORD=${val}|" .env; else echo "DB_PASSWORD=${val}" >> .env; fi
  echo "  Generated DB_PASSWORD"
fi
if need "ADMIN_PASSWORD"; then
  val="Adm1n.$(openssl rand -hex 6)"
  if grep -q "^ADMIN_PASSWORD=" .env; then sed -i '' "s|^ADMIN_PASSWORD=.*|ADMIN_PASSWORD=${val}|" .env; else echo "ADMIN_PASSWORD=${val}" >> .env; fi
  echo "  Generated ADMIN_PASSWORD"
fi
if need "ENCRYPTION_KEY"; then
  val=$(openssl rand -hex 16)
  if grep -q "^ENCRYPTION_KEY=" .env; then sed -i '' "s|^ENCRYPTION_KEY=.*|ENCRYPTION_KEY=${val}|" .env; else echo "ENCRYPTION_KEY=${val}" >> .env; fi
  echo "  Generated ENCRYPTION_KEY"
fi

DB_PASSWORD=$(grep "^DB_PASSWORD=" .env | cut -d= -f2-)
ENCRYPTION_KEY=$(grep "^ENCRYPTION_KEY=" .env | cut -d= -f2-)
cat > config.toml <<EOF
[app]
log_level = "info"
env = "prod"
check_updates = true
encryption_key = "${ENCRYPTION_KEY}"

[app.server]
address = "0.0.0.0:9000"
socket = ""
disable_secure_cookies = true
session_lifetime = "9h"
read_timeout = "60s"
write_timeout = "60s"
max_body_size = 104857600
read_buffer_size = 65536
keepalive_timeout = "10s"

[auth]
local_login_enabled = true

[upload]
provider = "fs"

[upload.fs]
upload_path = 'uploads'
expiry = "1h"

[db]
host = "db"
port = 5432
user = "libredesk"
password = "${DB_PASSWORD}"
database = "libredesk"
ssl_mode = "disable"
max_open = 30
max_idle = 30
max_lifetime = "300s"

[redis]
address = "redis:6379"
user = ""
password = ""
db = 0

[message]
outgoing_queue_workers = 10
incoming_queue_workers = 10
message_outgoing_scan_interval = "50ms"
incoming_queue_size = 5000
outgoing_queue_size = 5000

[notification]
concurrency = 2
queue_size = 2000

[automation]
worker_count = 10
time_trigger_lookback_days = 90

[ai_agent]
worker_count = 10
queue_size = 1000
max_steps = 6
max_history_messages = 30

[autoassigner]
autoassign_interval = "5m"

[webhook]
workers = 5
queue_size = 10000
timeout = "15s"

[ssrf]
enabled = false
allowed_cidrs = []

[conversation]
unsnooze_interval = "5m"
draft_retention_duration = "360h"
continuity_scan_interval = "5m"

[sla]
evaluation_interval = "5m"

[rate_limit.widget]
enabled = true
requests_per_minute = 100

[rate_limit.auth]
enabled = true
requests_per_minute = 30

[rate_limit.public]
enabled = true
requests_per_minute = 100

[rate_limit.media]
enabled = true
requests_per_minute = 300
EOF
echo "  Wrote config.toml"
echo "Secrets ready."
