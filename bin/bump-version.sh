#!/bin/bash

# Interactive version bumping tool for LùnPetShop KittyCat Chatbot
# Updates versions in WordPress plugin and backend API

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

PLUGIN_FILE="$PROJECT_ROOT/wordpress-plugin/lunpetshop-chatbot/lunpetshop-chatbot.php"
API_FILE="$PROJECT_ROOT/backend/src/api.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to extract version from file
extract_version() {
    local file=$1
    local pattern=$2
    
    if [ -f "$file" ]; then
        grep -o "$pattern" "$file" | head -1 | sed -E 's/.*["'\'']?([0-9]+\.[0-9]+\.[0-9]+)["'\'']?.*/\1/'
    else
        echo ""
    fi
}

# Function to bump version
bump_version() {
    local version=$1
    local bump_type=$2
    
    IFS='.' read -r -a parts <<< "$version"
    major=${parts[0]}
    minor=${parts[1]}
    patch=${parts[2]}
    
    case $bump_type in
        major)
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        minor)
            minor=$((minor + 1))
            patch=0
            ;;
        patch)
            patch=$((patch + 1))
            ;;
        *)
            echo "$version"
            return
            ;;
    esac
    
    echo "$major.$minor.$patch"
}

# Extract current versions
echo -e "${BLUE}📦 Current Version:${NC}"
echo ""

PLUGIN_VERSION=$(extract_version "$PLUGIN_FILE" "Version: [0-9]\+\.[0-9]\+\.[0-9]\+")
API_VERSION=$(extract_version "$API_FILE" 'version="[0-9]\+\.[0-9]\+\.[0-9]\+"')

if [ -z "$PLUGIN_VERSION" ]; then
    echo -e "${RED}❌ Could not read plugin version from $PLUGIN_FILE${NC}"
    exit 1
fi

if [ -z "$API_VERSION" ]; then
    echo -e "${RED}❌ Could not read API version from $API_FILE${NC}"
    exit 1
fi

# Check if versions are synchronized
if [ "$PLUGIN_VERSION" != "$API_VERSION" ]; then
    echo -e "${YELLOW}⚠️  Warning: Versions are out of sync!${NC}"
    echo -e "  WordPress Plugin: ${YELLOW}$PLUGIN_VERSION${NC}"
    echo -e "  Backend API:      ${YELLOW}$API_VERSION${NC}"
    echo ""
    echo -e "${BLUE}Using plugin version ($PLUGIN_VERSION) as primary.${NC}"
    echo ""
fi

CURRENT_VERSION=$PLUGIN_VERSION

echo -e "  Current Version: ${YELLOW}$CURRENT_VERSION${NC} (synchronized across all components)"
echo ""

echo -e "${BLUE}🎯 Bump Type:${NC}"
echo "  1) Major ($(bump_version "$CURRENT_VERSION" major))"
echo "  2) Minor ($(bump_version "$CURRENT_VERSION" minor))"
echo "  3) Patch ($(bump_version "$CURRENT_VERSION" patch))"
echo "  4) Custom version"
echo ""
read -p "Select [1-4]: " choice

case $choice in
    1)
        NEW_VERSION=$(bump_version "$CURRENT_VERSION" major)
        BUMP_TYPE="major"
        ;;
    2)
        NEW_VERSION=$(bump_version "$CURRENT_VERSION" minor)
        BUMP_TYPE="minor"
        ;;
    3)
        NEW_VERSION=$(bump_version "$CURRENT_VERSION" patch)
        BUMP_TYPE="patch"
        ;;
    4)
        read -p "Enter new version (e.g., 1.2.3): " NEW_VERSION
        
        # Validate version format
        if ! [[ "$NEW_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
            echo -e "${RED}❌ Invalid version format. Use semver (e.g., 1.2.3)${NC}"
            exit 1
        fi
        BUMP_TYPE="custom"
        ;;
    *)
        echo -e "${RED}❌ Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}📝 New Version:${NC}"
echo -e "  ${GREEN}$CURRENT_VERSION${NC} → ${GREEN}$NEW_VERSION${NC} ($BUMP_TYPE)"
echo -e "  (Will update WordPress plugin and backend API)"
echo ""
read -p "Confirm update? [y/N]: " confirm

if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}❌ Cancelled${NC}"
    exit 0
fi

# Update WordPress plugin file (2 locations)
echo ""
echo -e "${BLUE}🔄 Updating WordPress plugin...${NC}"
sed -i.bak "s/Version: $PLUGIN_VERSION/Version: $NEW_VERSION/" "$PLUGIN_FILE"
sed -i.bak "s/private const VERSION = '$PLUGIN_VERSION'/private const VERSION = '$NEW_VERSION'/" "$PLUGIN_FILE"
rm -f "${PLUGIN_FILE}.bak"
echo -e "${GREEN}✅ Updated plugin header and VERSION constant${NC}"

# Update backend API file
echo -e "${BLUE}🔄 Updating backend API...${NC}"
sed -i.bak "s/version=\"$API_VERSION\"/version=\"$NEW_VERSION\"/" "$API_FILE"
rm -f "${API_FILE}.bak"
echo -e "${GREEN}✅ Updated FastAPI version${NC}"

echo ""
echo -e "${GREEN}✨ Version bump complete!${NC}"
echo ""
echo -e "${BLUE}📋 Summary:${NC}"
echo -e "  Version: ${GREEN}$CURRENT_VERSION${NC} → ${GREEN}$NEW_VERSION${NC} ($BUMP_TYPE)"
echo -e "  Updated: WordPress plugin + Backend API"
echo ""

