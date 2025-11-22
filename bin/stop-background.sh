#!/bin/bash

# Stop the backend server and tunnel running in background
# Usage: ./bin/stop-background.sh

cd "$(dirname "$0")/.." || exit 1

PID_DIR="./.pids"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

stop_process() {
    local name=$1
    local pid_file="$PID_DIR/$name.pid"
    
    if [ ! -f "$pid_file" ]; then
        echo -e "${YELLOW}⚠️  No $name process found${NC}"
        return 1
    fi
    
    PID=$(cat "$pid_file")
    
    if [ -z "$PID" ]; then
        echo -e "${YELLOW}⚠️  $name PID file is empty${NC}"
        rm -f "$pid_file"
        return 1
    fi
    
    if kill -0 "$PID" 2>/dev/null; then
        echo -e "${YELLOW}🛑 Stopping $name (PID: $PID)...${NC}"
        kill "$PID" 2>/dev/null || true
        
        # Wait for graceful shutdown
        for i in {1..5}; do
            if ! kill -0 "$PID" 2>/dev/null; then
                break
            fi
            sleep 1
        done
        
        # Force kill if still running
        if kill -0 "$PID" 2>/dev/null; then
            echo -e "${YELLOW}   Force killing $name...${NC}"
            kill -9 "$PID" 2>/dev/null || true
            sleep 1
        fi
        
        if ! kill -0 "$PID" 2>/dev/null; then
            echo -e "${GREEN}✅ $name stopped${NC}"
            rm -f "$pid_file"
            return 0
        else
            echo -e "${RED}❌ Failed to stop $name${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️  $name process (PID: $PID) is not running${NC}"
        rm -f "$pid_file"
        return 1
    fi
}

# Stop tunnel first, then backend
stop_process "tunnel"
stop_process "backend"

# Clean up tunnel URL file
rm -f "$PID_DIR/tunnel.url"

echo ""
echo -e "${GREEN}✅ All services stopped${NC}"

