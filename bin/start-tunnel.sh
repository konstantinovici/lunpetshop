#!/bin/bash

# Tunnel script for LùnPetShop - supports both cloudflared and localtunnel
# Usage: ./bin/start-tunnel.sh [cloudflared|localtunnel] [port] [subdomain]

set -e

TUNNEL_TYPE=${1:-cloudflared}
PORT=${2:-8000}
SUBDOMAIN=${3:-lunpetshop-chatbot}

cd "$(dirname "$0")/.." || exit 1

echo "🌐 Starting tunnel for port $PORT..."

case $TUNNEL_TYPE in
  cloudflared|cf)
    echo "🚀 Using Cloudflare Tunnel (more reliable)"
    echo ""
    echo "Starting tunnel for http://localhost:${PORT}..."
    echo "Your tunnel URL will be shown below (random subdomain)"
    echo "Press Ctrl+C to stop"
    echo ""
    cloudflared tunnel --url "http://localhost:${PORT}"
    ;;
    
  localtunnel|lt)
    echo "🚇 Using LocalTunnel (may have connection issues)"
    echo ""
    LT_BIN="/Users/konstantinovichi/.bun/bin/lt"
    
    if [ ! -f "$LT_BIN" ]; then
      echo "❌ LocalTunnel not found at $LT_BIN"
      echo "   Install with: bun install -g localtunnel"
      exit 1
    fi
    
    # Auto-reconnect wrapper for localtunnel
    while true; do
      echo "🔄 Starting LocalTunnel..."
      "$LT_BIN" --port "$PORT" --subdomain "$SUBDOMAIN" || {
        echo "⚠️  Tunnel disconnected, reconnecting in 3 seconds..."
        sleep 3
      }
    done
    ;;
    
  *)
    echo "❌ Unknown tunnel type: $TUNNEL_TYPE"
    echo "   Usage: $0 [cloudflared|localtunnel] [port] [subdomain]"
    exit 1
    ;;
esac

