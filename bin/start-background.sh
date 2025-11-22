#!/bin/bash

# Start the backend server AND tunnel in the background
# Usage: ./bin/start-background.sh [tunnel-type] [port] [subdomain]
#   tunnel-type: cloudflared (default) or localtunnel
#   port: server port (default: 8000)
#   subdomain: for localtunnel only (default: lunpetshop-chatbot)

cd "$(dirname "$0")/.." || exit 1

# Configuration
TUNNEL_TYPE=${1:-cloudflared}
PORT=${2:-${PORT:-8000}}
SUBDOMAIN=${3:-lunpetshop-chatbot}
LOG_DIR="./logs"
PID_DIR="./.pids"
MAX_LOG_SIZE_MB=50

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Create directories
mkdir -p "$LOG_DIR" "$PID_DIR"

# Rotate logs if they're getting too large
rotate_log_if_needed() {
    local logfile=$1
    
    if [ -f "$logfile" ]; then
        # Get size in MB
        local size_mb=$(du -m "$logfile" 2>/dev/null | cut -f1 || echo "0")
        
        if [ "$size_mb" -gt "$MAX_LOG_SIZE_MB" ]; then
            local timestamp=$(date +%Y%m%d_%H%M%S)
            mv "$logfile" "${logfile}.${timestamp}"
            echo -e "${YELLOW}📦 Rotated log: ${logfile}.${timestamp} (was ${size_mb}MB)${NC}"
            
            # Keep only last 5 rotated logs
            ls -t "${logfile}".* 2>/dev/null | tail -n +6 | xargs rm -f 2>/dev/null || true
        fi
    fi
}

# Rotate logs before starting
rotate_log_if_needed "$LOG_DIR/backend.log"
rotate_log_if_needed "$LOG_DIR/tunnel.log"

# Check if virtual environment exists
if [ ! -d .venv ]; then
    echo -e "${RED}❌ Virtual environment not found. Run './run.sh' first.${NC}"
    exit 1
fi

# Check if already running
if [ -f "$PID_DIR/backend.pid" ]; then
    OLD_PID=$(cat "$PID_DIR/backend.pid")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  Backend is already running (PID: $OLD_PID)${NC}"
        echo "   Use './bin/stop-background.sh' to stop it first"
        exit 1
    else
        # PID file exists but process is dead, clean it up
        rm -f "$PID_DIR/backend.pid"
    fi
fi

if [ -f "$PID_DIR/tunnel.pid" ]; then
    OLD_PID=$(cat "$PID_DIR/tunnel.pid")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  Tunnel is already running (PID: $OLD_PID)${NC}"
        echo "   Use './bin/stop-background.sh' to stop it first"
        exit 1
    else
        rm -f "$PID_DIR/tunnel.pid"
    fi
fi

# Check if port is in use
if command -v lsof >/dev/null 2>&1; then
    if lsof -i :"$PORT" >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Port $PORT is already in use${NC}"
        echo "   Use a different port: PORT=8001 ./bin/start-background.sh"
        exit 1
    fi
fi

# Activate virtual environment
source .venv/bin/activate

# Start backend in background
echo -e "${BLUE}🚀 Starting backend server in background...${NC}"
echo "   Port: $PORT"
echo "   Logs: $LOG_DIR/backend.log"
echo "   PID file: $PID_DIR/backend.pid"

(
    export PORT=$PORT
    cd backend
    nohup python main.py >> "../$LOG_DIR/backend.log" 2>&1 &
    echo $! > "../$PID_DIR/backend.pid"
)

# Wait a moment to check if it started successfully
sleep 2

# Verify backend is running
if [ -f "$PID_DIR/backend.pid" ]; then
    PID=$(cat "$PID_DIR/backend.pid")
    if kill -0 "$PID" 2>/dev/null; then
        echo -e "${GREEN}✅ Backend started! (PID: $PID)${NC}"
    else
        echo -e "${RED}❌ Failed to start backend${NC}"
        echo "   Check logs: tail -f $LOG_DIR/backend.log"
        rm -f "$PID_DIR/backend.pid"
        exit 1
    fi
else
    echo -e "${RED}❌ Failed to start backend${NC}"
    exit 1
fi

# Wait for backend to be ready before starting tunnel
sleep 3

# Start tunnel in background
echo ""
echo -e "${BLUE}🌐 Starting tunnel ($TUNNEL_TYPE) in background...${NC}"
echo "   Logs: $LOG_DIR/tunnel.log"
echo "   PID file: $PID_DIR/tunnel.pid"

case $TUNNEL_TYPE in
    cloudflared|cf)
        (
            nohup cloudflared tunnel --url "http://localhost:$PORT" 2>&1 | \
            while IFS= read -r line; do
                echo "$(date '+%Y-%m-%d %H:%M:%S') $line" >> "$LOG_DIR/tunnel.log"
                # Extract and save tunnel URL
                if echo "$line" | grep -qE "https://.*\.trycloudflare\.com"; then
                    TUNNEL_URL=$(echo "$line" | grep -oE "https://[a-zA-Z0-9-]+\.trycloudflare\.com" | head -1)
                    if [ -n "$TUNNEL_URL" ]; then
                        echo "$TUNNEL_URL" > "$PID_DIR/tunnel.url"
                        echo "$(date '+%Y-%m-%d %H:%M:%S') Tunnel URL: $TUNNEL_URL" >> "$LOG_DIR/tunnel.log"
                    fi
                fi
            done
        ) &
        TUNNEL_PID=$!
        ;;
        
    localtunnel|lt)
        LT_BIN="/Users/konstantinovichi/.bun/bin/lt"
        if [ ! -f "$LT_BIN" ]; then
            echo -e "${RED}❌ LocalTunnel not found at $LT_BIN${NC}"
            echo "   Install with: bun install -g localtunnel"
            exit 1
        fi
        
        (
            nohup "$LT_BIN" --port "$PORT" --subdomain "$SUBDOMAIN" 2>&1 | \
            while IFS= read -r line; do
                echo "$(date '+%Y-%m-%d %H:%M:%S') $line" >> "$LOG_DIR/tunnel.log"
                # Extract and save tunnel URL
                if echo "$line" | grep -qE "https://.*\.loca\.lt"; then
                    TUNNEL_URL=$(echo "$line" | grep -oE "https://[a-zA-Z0-9-]+\.loca\.lt" | head -1)
                    if [ -n "$TUNNEL_URL" ]; then
                        echo "$TUNNEL_URL" > "$PID_DIR/tunnel.url"
                        echo "$(date '+%Y-%m-%d %H:%M:%S') Tunnel URL: $TUNNEL_URL" >> "$LOG_DIR/tunnel.log"
                    fi
                fi
            done
        ) &
        TUNNEL_PID=$!
        ;;
        
    *)
        echo -e "${RED}❌ Unknown tunnel type: $TUNNEL_TYPE${NC}"
        echo "   Use 'cloudflared' or 'localtunnel'"
        exit 1
        ;;
esac

echo $TUNNEL_PID > "$PID_DIR/tunnel.pid"
echo -e "${GREEN}✅ Tunnel started! (PID: $TUNNEL_PID)${NC}"

# Wait a bit for tunnel URL
sleep 8

# Show status
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Everything is running in the background!${NC}"
echo ""
echo -e "${BLUE}📊 Status:${NC}"
echo "   Backend PID: $(cat "$PID_DIR/backend.pid")"
echo "   Tunnel PID: $(cat "$PID_DIR/tunnel.pid")"
echo "   Backend URL: http://localhost:$PORT"
if [ -f "$PID_DIR/tunnel.url" ]; then
    echo "   Tunnel URL: $(cat "$PID_DIR/tunnel.url")"
else
    echo "   Tunnel URL: Check logs (may take a few seconds)"
fi
echo ""
echo -e "${BLUE}💡 Commands:${NC}"
echo "   Stop: ./bin/stop-background.sh"
echo "   View backend logs: tail -f $LOG_DIR/backend.log"
echo "   View tunnel logs: tail -f $LOG_DIR/tunnel.log"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

