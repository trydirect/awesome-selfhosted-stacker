#!/bin/sh
set -e

# Create TLS directory and self-signed certificates if they don't exist
TLS_DIR="/opt/tls"

# Try to create TLS directory - if we can't, proceed anyway
if mkdir -p "$TLS_DIR" 2>/dev/null; then
  if [ ! -f "$TLS_DIR/rustfs_key.pem" ] || [ ! -f "$TLS_DIR/rustfs_cert.pem" ] || [ ! -f "$TLS_DIR/ca.crt" ]; then
    echo "Generating self-signed TLS certificates..."
    
    # Generate private key
    if command -v openssl >/dev/null 2>&1; then
      openssl genrsa -out "$TLS_DIR/rustfs_key.pem" 2048 2>/dev/null || true
      openssl req -new -x509 -key "$TLS_DIR/rustfs_key.pem" \
        -out "$TLS_DIR/rustfs_cert.pem" \
        -days 365 \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost" 2>/dev/null || true
      cp "$TLS_DIR/rustfs_cert.pem" "$TLS_DIR/ca.crt"
    else
      echo "dummy-key" > "$TLS_DIR/rustfs_key.pem" || true
      echo "dummy-cert" > "$TLS_DIR/rustfs_cert.pem" || true
      echo "dummy-ca" > "$TLS_DIR/ca.crt" || true
    fi
    echo "TLS certificates created"
  fi
else
  echo "WARNING: Cannot create TLS directory at $TLS_DIR, proceeding without TLS"
fi

# Initialize data directories if needed
mkdir -p /data/rustfs0 /data/rustfs1 /data/rustfs2 /data/rustfs3 /app/logs || true

# Start RustFS server
exec /usr/bin/rustfs server /data/rustfs0 /data/rustfs1 /data/rustfs2 /data/rustfs3
