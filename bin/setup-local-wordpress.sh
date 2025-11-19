#!/bin/bash
# Setup script for Local by Flywheel WordPress development

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PLUGIN_DIR="$PROJECT_ROOT/wordpress-plugin/lunpetshop-chatbot"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🐱 KittyCat Chatbot - Local WordPress Setup${NC}"
echo ""

# Check if Local is installed
if ! command -v local &> /dev/null; then
    echo -e "${YELLOW}⚠️  Local by Flywheel CLI not found.${NC}"
    echo "Please install Local from: https://localwp.com/"
    echo "Or install via Homebrew: brew install --cask local"
    exit 1
fi

# Find Local sites directory
LOCAL_SITES_DIR="$HOME/Local Sites"
if [ ! -d "$LOCAL_SITES_DIR" ]; then
    echo -e "${RED}❌ Local Sites directory not found at: $LOCAL_SITES_DIR${NC}"
    echo "Please create a site in Local first, then run this script again."
    exit 1
fi

# List available sites
echo "Available Local sites:"
ls -1 "$LOCAL_SITES_DIR" | nl
echo ""

# Prompt for site name
read -p "Enter site name (or press Enter for 'lunpetshop-local'): " SITE_NAME
SITE_NAME=${SITE_NAME:-lunpetshop-local}
SITE_PATH="$LOCAL_SITES_DIR/$SITE_NAME"

if [ ! -d "$SITE_PATH" ]; then
    echo -e "${YELLOW}⚠️  Site '$SITE_NAME' not found.${NC}"
    echo "Please create it in Local first, or choose an existing site."
    exit 1
fi

PLUGINS_DIR="$SITE_PATH/app/public/wp-content/plugins"
TARGET_PLUGIN_DIR="$PLUGINS_DIR/lunpetshop-chatbot"

echo -e "${GREEN}📦 Installing plugin to: $TARGET_PLUGIN_DIR${NC}"

# Remove existing plugin if it exists
if [ -d "$TARGET_PLUGIN_DIR" ]; then
    echo -e "${YELLOW}⚠️  Removing existing plugin installation...${NC}"
    rm -rf "$TARGET_PLUGIN_DIR"
fi

# Copy plugin
cp -r "$PLUGIN_DIR" "$TARGET_PLUGIN_DIR"

echo -e "${GREEN}✅ Plugin installed successfully!${NC}"
echo ""
echo "Next steps:"
echo "1. Open Local and start the site: $SITE_NAME"
echo "2. Go to WordPress admin: http://$SITE_NAME.local/wp-admin"
echo "3. Navigate to: Plugins → Activate 'LùnPetShop KittyCat Chatbot'"
echo "4. Configure: Settings → KittyCat Chatbot → Set API Base URL"
echo ""
echo -e "${YELLOW}💡 Tip: Enable WP_DEBUG in wp-config.php to see debug logs${NC}"
echo "   Logs location: $SITE_PATH/logs/php/error.log"

