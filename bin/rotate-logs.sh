#!/bin/bash

# Rotate logs if they exceed a certain size
# Usage: ./bin/rotate-logs.sh [max-size-mb]
#   max-size-mb: maximum size in MB before rotation (default: 50)

cd "$(dirname "$0")/.." || exit 1

MAX_SIZE_MB=${1:-50}
LOG_DIR="./logs"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

rotate_log() {
    local logfile=$1
    
    if [ ! -f "$logfile" ]; then
        return 0
    fi
    
    # Get size in MB
    local size_mb=$(du -m "$logfile" 2>/dev/null | cut -f1 || echo "0")
    
    if [ "$size_mb" -gt "$MAX_SIZE_MB" ]; then
        local timestamp=$(date +%Y%m%d_%H%M%S)
        local rotated_file="${logfile}.${timestamp}"
        
        mv "$logfile" "$rotated_file"
        echo -e "${GREEN}📦 Rotated ${logfile} (${size_mb}MB) → ${rotated_file}${NC}"
        
        # Keep only last 5 rotated logs
        ls -t "${logfile}".* 2>/dev/null | tail -n +6 | xargs rm -f 2>/dev/null || true
    else
        echo -e "${BLUE}✓ ${logfile} is ${size_mb}MB (OK)${NC}"
    fi
}

echo -e "${BLUE}🔍 Checking logs (max size: ${MAX_SIZE_MB}MB)...${NC}"
echo ""

rotate_log "$LOG_DIR/backend.log"
rotate_log "$LOG_DIR/tunnel.log"

echo ""
echo -e "${GREEN}✅ Log rotation complete${NC}"











