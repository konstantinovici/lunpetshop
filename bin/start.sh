#!/bin/bash

# Simple start script for LùnPetShop KittyCat Chatbot

cd "$(dirname "$0")/.." || exit 1

# Activate virtual environment if it exists
if [ -d .venv ]; then
    source .venv/bin/activate
else
    echo "⚠️  Virtual environment not found. Run './run.sh' first to set up."
    exit 1
fi

# Function to check if a port is available
check_port() {
    local port=$1
    if command -v lsof >/dev/null 2>&1; then
        lsof -i :"$port" >/dev/null 2>&1
        return $?
    elif command -v netstat >/dev/null 2>&1; then
        netstat -an | grep -q ":$port.*LISTEN"
        return $?
    else
        # Fallback: try to connect to the port
        (echo >/dev/tcp/localhost/"$port") >/dev/null 2>&1
        return $?
    fi
}

# Find an available port starting from 8000
find_available_port() {
    local start_port=${1:-8000}
    local max_port=${2:-8010}
    local port=$start_port
    
    while [ $port -le $max_port ]; do
        if ! check_port "$port"; then
            echo "$port"
            return 0
        fi
        port=$((port + 1))
    done
    
    echo ""
    return 1
}

# Check if PORT is already set in environment
if [ -z "$PORT" ]; then
    # Try to find an available port
    DEFAULT_PORT=8000
    AVAILABLE_PORT=$(find_available_port $DEFAULT_PORT 8010)
    
    if [ -z "$AVAILABLE_PORT" ]; then
        echo "❌ Error: No available ports found (tried $DEFAULT_PORT-8010)"
        echo "   Please free up a port or set PORT environment variable:"
        echo "   PORT=8080 ./bin/start.sh"
        exit 1
    fi
    
    if [ "$AVAILABLE_PORT" != "$DEFAULT_PORT" ]; then
        echo "⚠️  Port $DEFAULT_PORT is already in use, using port $AVAILABLE_PORT instead"
    fi
    
    export PORT=$AVAILABLE_PORT
fi

# Start the server from backend directory
cd backend
python main.py

