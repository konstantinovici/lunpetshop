#!/bin/bash
# =============================================================================
# LùnPetShop Product Sync Trigger
# =============================================================================
# 
# Manual trigger for syncing products from WooCommerce to local cache.
# Run this whenever products are updated in WooCommerce.
#
# Usage:
#   ./scripts/trigger_sync.sh
#
# =============================================================================

set -e  # Exit on error

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "LùnPetShop Product Sync"
echo "=========================================="
echo ""
echo "Backend directory: $BACKEND_DIR"
echo ""

# Change to backend directory
cd "$BACKEND_DIR"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
elif [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Run sync script
echo "Starting product sync..."
echo ""
python3 scripts/sync_products.py

echo ""
echo "=========================================="
echo "Sync complete!"
echo "=========================================="


