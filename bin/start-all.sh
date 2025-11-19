#!/bin/bash

# Unified startup script for LùnPetShop - starts backend + tunnel with auto-restart and health checks
# Usage: ./bin/start-all.sh [tunnel-type] [port]
#   tunnel-type: cloudflared (default) or localtunnel
#   port: server port (default: 8000)

set -eo pipefail

cd "$(dirname "$0")/.." || exit 1

# Configuration
TUNNEL_TYPE=${1:-cloudflared}
PORT=${2:-8000}
SUBDOMAIN=${3:-lunpetshop-chatbot}
LOG_DIR="./logs"
PID_DIR="./.pids"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create directories
mkdir -p "$LOG_DIR" "$PID_DIR"

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down...${NC}"
    
    # Kill backend
    if [ -f "$PID_DIR/backend.pid" ]; then
        BACKEND_PID=$(cat "$PID_DIR/backend.pid")
        if kill -0 "$BACKEND_PID" 2>/dev/null; then
            echo "   Stopping backend (PID: $BACKEND_PID)..."
            kill "$BACKEND_PID" 2>/dev/null || true
            wait "$BACKEND_PID" 2>/dev/null || true
        fi
        rm -f "$PID_DIR/backend.pid"
    fi
    
    # Kill tunnel
    if [ -f "$PID_DIR/tunnel.pid" ]; then
        TUNNEL_PID=$(cat "$PID_DIR/tunnel.pid")
        if kill -0 "$TUNNEL_PID" 2>/dev/null; then
            echo "   Stopping tunnel (PID: $TUNNEL_PID)..."
            kill "$TUNNEL_PID" 2>/dev/null || true
            wait "$TUNNEL_PID" 2>/dev/null || true
        fi
        rm -f "$PID_DIR/tunnel.pid"
    fi
    
    # Kill status monitor
    if [ -n "${STATUS_PID:-}" ] && kill -0 "$STATUS_PID" 2>/dev/null; then
        kill "$STATUS_PID" 2>/dev/null || true
    fi
    
    # Kill all child processes
    pkill -P $$ 2>/dev/null || true
    
    # Clean up PID files
    rm -rf "$PID_DIR"
    
    echo -e "${GREEN}✅ Cleanup complete${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM EXIT

# Check prerequisites
if [ ! -d .venv ]; then
    echo -e "${RED}❌ Virtual environment not found. Run './run.sh' first.${NC}"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Health check function
health_check() {
    local service=$1
    local url=$2
    local max_attempts=${3:-10}
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -sf "$url" >/dev/null 2>&1; then
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    return 1
}

# Start backend with auto-restart
start_backend() {
    local port=$1
    
    while true; do
        set +e  # Don't exit on errors in monitoring loop
        if [ ! -f "$PID_DIR/backend.pid" ] || ! kill -0 "$(cat "$PID_DIR/backend.pid" 2>/dev/null)" 2>/dev/null; then
            echo -e "${BLUE}🚀 Starting backend server on port $port...${NC}"
            
            # Start backend in background
            (
                export PORT=$port
                cd backend
                python main.py >> "../$LOG_DIR/backend.log" 2>&1
            ) &
            
            local backend_pid=$!
            echo $backend_pid > "$PID_DIR/backend.pid"
            
            # Wait a bit for server to start
            sleep 5
            
            # Health check
            if health_check "backend" "http://localhost:$port/health" 15; then
                echo -e "${GREEN}✅ Backend is healthy! (PID: $backend_pid)${NC}"
            else
                echo -e "${YELLOW}⚠️  Backend health check failed, will retry...${NC}"
            fi
        fi
        set -e  # Re-enable error exit
        sleep 5
    done
}

# Start tunnel with auto-restart
start_tunnel() {
    local port=$1
    local tunnel_type=$2
    local subdomain=$3
    
    while true; do
        set +e  # Don't exit on errors in monitoring loop
        if [ ! -f "$PID_DIR/tunnel.pid" ] || ! kill -0 "$(cat "$PID_DIR/tunnel.pid" 2>/dev/null)" 2>/dev/null; then
            case $tunnel_type in
                cloudflared|cf)
                    echo -e "${BLUE}🌐 Starting Cloudflare Tunnel...${NC}"
                    
                    (
                        cloudflared tunnel --url "http://localhost:$port" 2>&1 | \
                        while IFS= read -r line; do
                            echo "$line" | tee -a "$LOG_DIR/tunnel.log"
                            # Extract and display tunnel URL
                            if echo "$line" | grep -qE "https://.*\.trycloudflare\.com"; then
                                TUNNEL_URL=$(echo "$line" | grep -oE "https://[a-zA-Z0-9-]+\.trycloudflare\.com" | head -1)
                                if [ -n "$TUNNEL_URL" ]; then
                                    echo -e "${GREEN}✅ Tunnel URL: $TUNNEL_URL${NC}" >&2
                                    echo "$TUNNEL_URL" > "$PID_DIR/tunnel.url"
                                fi
                            fi
                        done
                    ) &
                    ;;
                    
                localtunnel|lt)
                    echo -e "${BLUE}🌐 Starting LocalTunnel...${NC}"
                    local LT_BIN="/Users/konstantinovichi/.bun/bin/lt"
                    
                    if [ ! -f "$LT_BIN" ]; then
                        echo -e "${RED}❌ LocalTunnel not found at $LT_BIN${NC}"
                        echo "   Install with: bun install -g localtunnel"
                        sleep 10
                        continue
                    fi
                    
                    (
                        "$LT_BIN" --port "$port" --subdomain "$subdomain" 2>&1 | \
                        while IFS= read -r line; do
                            echo "$line" | tee -a "$LOG_DIR/tunnel.log"
                            # Extract and display tunnel URL
                            if echo "$line" | grep -qE "https://.*\.loca\.lt"; then
                                TUNNEL_URL=$(echo "$line" | grep -oE "https://[a-zA-Z0-9-]+\.loca\.lt" | head -1)
                                if [ -n "$TUNNEL_URL" ]; then
                                    echo -e "${GREEN}✅ Tunnel URL: $TUNNEL_URL${NC}" >&2
                                    echo "$TUNNEL_URL" > "$PID_DIR/tunnel.url"
                                fi
                            fi
                        done || true
                    ) &
                    ;;
                    
                *)
                    echo -e "${RED}❌ Unknown tunnel type: $tunnel_type${NC}"
                    exit 1
                    ;;
            esac
            
            local tunnel_pid=$!
            echo $tunnel_pid > "$PID_DIR/tunnel.pid"
            echo -e "${BLUE}   Tunnel process started (PID: $tunnel_pid)${NC}"
            
            # Wait a bit for tunnel to establish
            sleep 8
            
            # Check if tunnel URL was captured
            if [ -f "$PID_DIR/tunnel.url" ]; then
                TUNNEL_URL=$(cat "$PID_DIR/tunnel.url")
                echo -e "${GREEN}✅ Tunnel is active: $TUNNEL_URL${NC}"
            fi
        fi
        set -e  # Re-enable error exit
        sleep 5
    done
}

# Monitor processes
monitor_processes() {
    while true; do
        set +e  # Don't exit on errors in monitoring loop
        sleep 10
        
        # Check backend
        if [ -f "$PID_DIR/backend.pid" ]; then
            BACKEND_PID=$(cat "$PID_DIR/backend.pid")
            if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
                echo -e "${RED}❌ Backend process died! Will restart...${NC}"
                rm -f "$PID_DIR/backend.pid"
            elif ! health_check "backend" "http://localhost:$PORT/health" 2; then
                echo -e "${YELLOW}⚠️  Backend health check failed! Will restart...${NC}"
                kill "$BACKEND_PID" 2>/dev/null || true
                rm -f "$PID_DIR/backend.pid"
            fi
        fi
        
        # Check tunnel
        if [ -f "$PID_DIR/tunnel.pid" ]; then
            TUNNEL_PID=$(cat "$PID_DIR/tunnel.pid")
            if ! kill -0 "$TUNNEL_PID" 2>/dev/null; then
                echo -e "${RED}❌ Tunnel process died! Will restart...${NC}"
                rm -f "$PID_DIR/tunnel.pid"
            fi
        fi
        set -e  # Re-enable error exit
    done
}

# Main execution
echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║   🐱 LùnPetShop KittyCat Chatbot - Unified Startup       ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${BLUE}📋 Configuration:${NC}"
echo "   Backend Port: $PORT"
echo "   Tunnel Type: $TUNNEL_TYPE"
echo "   Logs: $LOG_DIR/"
echo ""

# Start backend in background
start_backend "$PORT" &
BACKEND_MONITOR_PID=$!

# Wait a bit for backend to be ready
sleep 5

# Start tunnel in background
start_tunnel "$PORT" "$TUNNEL_TYPE" "$SUBDOMAIN" &
TUNNEL_MONITOR_PID=$!

# Start process monitor
monitor_processes &
MONITOR_PID=$!

# Show status
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ All services starting...${NC}"
echo ""
echo -e "${BLUE}📊 Status:${NC}"
echo "   Backend: http://localhost:$PORT"
echo "   Health:  http://localhost:$PORT/health"
echo "   Logs:    tail -f $LOG_DIR/backend.log"
echo "   Tunnel:  tail -f $LOG_DIR/tunnel.log"
echo ""
echo -e "${YELLOW}💡 Tips:${NC}"
echo "   - Press Ctrl+C to stop all services"
echo "   - Check logs in $LOG_DIR/ for details"
echo "   - Services will auto-restart on failure"
echo "   - Tunnel URL will appear above when ready"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Periodic status updates
(
    while true; do
        set +e  # Don't exit on errors in status loop
        sleep 30
        echo ""
        echo -e "${BLUE}📊 Status Update:${NC}"
        
        # Backend status
        if [ -f "$PID_DIR/backend.pid" ] && kill -0 "$(cat "$PID_DIR/backend.pid")" 2>/dev/null; then
            if health_check "backend" "http://localhost:$PORT/health" 2; then
                echo -e "   ${GREEN}✅ Backend: Running & Healthy${NC}"
            else
                echo -e "   ${YELLOW}⚠️  Backend: Running but unhealthy${NC}"
            fi
        else
            echo -e "   ${RED}❌ Backend: Not running${NC}"
        fi
        
        # Tunnel status
        if [ -f "$PID_DIR/tunnel.pid" ] && kill -0 "$(cat "$PID_DIR/tunnel.pid")" 2>/dev/null; then
            if [ -f "$PID_DIR/tunnel.url" ]; then
                TUNNEL_URL=$(cat "$PID_DIR/tunnel.url")
                echo -e "   ${GREEN}✅ Tunnel: Running - $TUNNEL_URL${NC}"
            else
                echo -e "   ${YELLOW}⚠️  Tunnel: Running (URL not yet available)${NC}"
            fi
        else
            echo -e "   ${RED}❌ Tunnel: Not running${NC}"
        fi
        set -e  # Re-enable error exit
        echo ""
    done
) &
STATUS_PID=$!

# Wait for all background processes
wait

