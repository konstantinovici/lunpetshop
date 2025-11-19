#!/bin/bash

# Build script for WordPress plugin
# Creates a zip file from the WordPress plugin directory

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PLUGIN_DIR="$PROJECT_ROOT/wordpress-plugin/lunpetshop-chatbot"
OUTPUT_DIR="$PROJECT_ROOT"
PLUGIN_NAME="lunpetshop-chatbot"

cd "$PROJECT_ROOT"

echo "📦 Building WordPress plugin..."

# Check if plugin directory exists
if [ ! -d "$PLUGIN_DIR" ]; then
    echo "❌ Error: Plugin directory not found at $PLUGIN_DIR"
    exit 1
fi

# Check if widget files exist (they should be symlinked)
if [ ! -f "$PLUGIN_DIR/assets/css/chat-widget.css" ]; then
    echo "⚠️  Warning: chat-widget.css not found. Make sure symlinks are set up."
    echo "   Run: cd wordpress-plugin/lunpetshop-chatbot && mkdir -p assets/css assets/js"
    echo "   Then: ln -sf ../../../widget/assets/css/chat-widget.css assets/css/"
    echo "   And: ln -sf ../../../widget/assets/js/chat-widget.js assets/js/"
fi

# Create zip file
ZIP_FILE="$OUTPUT_DIR/${PLUGIN_NAME}.zip"

# Remove old zip if exists
if [ -f "$ZIP_FILE" ]; then
    rm "$ZIP_FILE"
    echo "🗑️  Removed old zip file"
fi

# Create zip (exclude symlinks, git files, etc.)
cd "$PLUGIN_DIR"
zip -r "$ZIP_FILE" . \
    -x "*.git*" \
    -x "*.DS_Store" \
    -x "*__pycache__*" \
    -x "*.pyc" \
    -x "*.log" \
    > /dev/null

# Follow symlinks and add actual files
if [ -L "$PLUGIN_DIR/assets/css/chat-widget.css" ]; then
    # Add widget CSS file
    cd "$PROJECT_ROOT"
    zip -j "$ZIP_FILE" widget/assets/css/chat-widget.css
    # Rename in zip to correct path
    zip -d "$ZIP_FILE" chat-widget.css > /dev/null 2>&1 || true
    cd "$PLUGIN_DIR"
    zip "$ZIP_FILE" assets/css/chat-widget.css > /dev/null 2>&1 || true
    # Actually, let's copy the files instead of using symlinks for the zip
    cp "$PROJECT_ROOT/widget/assets/css/chat-widget.css" assets/css/ 2>/dev/null || true
    cp "$PROJECT_ROOT/widget/assets/js/chat-widget.js" assets/js/ 2>/dev/null || true
    zip -r "$ZIP_FILE" . -x "*.git*" "*.DS_Store" > /dev/null
    # Restore symlinks
    rm assets/css/chat-widget.css assets/js/chat-widget.js 2>/dev/null || true
    ln -sf ../../../../widget/assets/css/chat-widget.css assets/css/chat-widget.css 2>/dev/null || true
    ln -sf ../../../../widget/assets/js/chat-widget.js assets/js/chat-widget.js 2>/dev/null || true
fi

echo "✅ Plugin built successfully: $ZIP_FILE"
echo "📦 File size: $(du -h "$ZIP_FILE" | cut -f1)"
echo ""
echo "🚀 Ready to upload to WordPress!"

