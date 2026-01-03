#!/bin/bash
# =============================================================================
# LùnPetShop Cron Job Setup
# =============================================================================
# 
# Sets up daily cron job for automatic product sync from WooCommerce.
# Run this once on the server to enable automatic daily syncing.
#
# Usage:
#   ./bin/setup-cron.sh
#
# The cron job runs at 2:00 AM daily.
# =============================================================================

set -e  # Exit on error

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SYNC_SCRIPT="$PROJECT_DIR/backend/scripts/trigger_sync.sh"
LOG_FILE="$PROJECT_DIR/logs/sync.log"

echo "=========================================="
echo "LùnPetShop Cron Setup"
echo "=========================================="
echo ""
echo "Project directory: $PROJECT_DIR"
echo "Sync script: $SYNC_SCRIPT"
echo "Log file: $LOG_FILE"
echo ""

# Check if sync script exists
if [ ! -f "$SYNC_SCRIPT" ]; then
    echo "ERROR: Sync script not found at $SYNC_SCRIPT"
    exit 1
fi

# Ensure logs directory exists
mkdir -p "$PROJECT_DIR/logs"

# Create cron entry
# Format: minute hour day month weekday command
# 0 2 * * * = 2:00 AM every day
CRON_ENTRY="0 2 * * * $SYNC_SCRIPT >> $LOG_FILE 2>&1"

echo "Cron entry to add:"
echo "  $CRON_ENTRY"
echo ""

# Check if cron entry already exists
if crontab -l 2>/dev/null | grep -q "$SYNC_SCRIPT"; then
    echo "Cron job already exists. Skipping."
else
    # Add to crontab
    echo "Adding cron job..."
    (crontab -l 2>/dev/null || true; echo "$CRON_ENTRY") | crontab -
    echo "Cron job added successfully!"
fi

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "The sync script will run automatically at 2:00 AM daily."
echo ""
echo "To verify, run: crontab -l"
echo "To remove, run: crontab -e (and delete the line)"
echo ""
echo "Manual sync: ./backend/scripts/trigger_sync.sh"
echo "Check logs: tail -f $LOG_FILE"


