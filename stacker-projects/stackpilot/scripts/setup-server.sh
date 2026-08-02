#!/usr/bin/env bash
set -euo pipefail

SERVER="${1:?Usage: $0 <server_ip> [ssh_key]}"
SSH_KEY="${2:-${BASE_PATH}/stacker-project-test}"

SSH="ssh -i $SSH_KEY -o ConnectTimeout=10 root@$SERVER"

echo "==> Setting up server $SERVER"

# Check if already has swap
if $SSH "swapon --show | grep -q swapfile"; then
  echo "  Swap already configured"
else
  echo "  Creating 2GB swap..."
  $SSH "fallocate -l 2G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile && echo '/swapfile none swap sw 0 0' >> /etc/fstab"
  echo "  Swap created"
fi

# Ensure Docker is installed
if $SSH "command -v docker" > /dev/null 2>&1; then
  echo "  Docker already installed"
else
  echo "  Installing Docker..."
  $SSH "curl -fsSL https://get.docker.com | sh"
  echo "  Docker installed"
fi

# Ensure Docker Compose plugin is available
if $SSH "docker compose version" > /dev/null 2>&1; then
  echo "  Docker Compose already available"
else
  echo "  Installing Docker Compose plugin..."
  $SSH "apt-get update && apt-get install -y docker-compose-plugin"
  echo "  Docker Compose installed"
fi

# Show final status
echo ""
echo "==> Server status:"
$SSH "free -h | head -2"
$SSH "docker --version"
echo ""
echo "==> Ready to deploy!"
