#!/bin/bash

# Quick start script for LùnPetShop KittyCat Chatbot

echo "🐾 Starting LùnPetShop KittyCat Chatbot..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    
    # Create .env from template if it exists
    if [ -f .env.example ]; then
        echo "Creating .env from template..."
        cp .env.example .env
    else
        echo "Creating .env file..."
        cat > .env << EOF
# LùnPetShop KittyCat Chatbot - Environment Variables
XAI_API_KEY=your_api_key_here
EOF
    fi
    
    echo ""
    echo "📝 Please edit .env and add your XAI_API_KEY:"
    echo "   XAI_API_KEY=your_api_key_here"
    echo ""
    echo "Get your API key from: https://console.x.ai/"
    echo ""
    read -p "Press Enter after you've added your API key..."
fi

# Check if virtual environment exists
if [ ! -d .venv ]; then
    echo "📦 Creating virtual environment..."
    uv venv
    echo ""
fi

# Activate virtual environment and install dependencies
echo "📦 Installing dependencies..."
source .venv/bin/activate
uv pip install -r backend/requirements.txt -q

echo ""
echo "🚀 Starting server..."
echo ""

# Run the application from backend directory
cd backend
python main.py

