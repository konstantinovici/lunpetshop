#!/usr/bin/env python3
"""Standalone Discord health monitoring script.

This can be run separately from the main API if needed.
Useful for monitoring production deployments.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from src.discord_monitor import DiscordHealthMonitor


async def main():
    """Run standalone health monitor."""
    # Get configuration
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    health_url = os.getenv("HEALTH_CHECK_URL", "http://localhost:8000/health/metrics")
    interval = int(os.getenv("DISCORD_CHECK_INTERVAL", "3600"))  # Default 1 hour
    
    if not webhook_url:
        print("❌ Error: DISCORD_WEBHOOK_URL environment variable not set!")
        print("\nTo set up Discord monitoring:")
        print("1. Create a webhook in your Discord server:")
        print("   Server Settings → Integrations → Webhooks → New Webhook")
        print("2. Copy the webhook URL")
        print("3. Set it in your .env file:")
        print("   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...")
        sys.exit(1)
    
    print("🐱 LùnPetShop Chatbot - Discord Health Monitor")
    print("=" * 50)
    print(f"📊 Health URL: {health_url}")
    print(f"⏰ Check Interval: {interval}s ({interval/3600:.1f} hours)")
    print("=" * 50)
    print()
    
    monitor = DiscordHealthMonitor(webhook_url=webhook_url, health_url=health_url)
    await monitor.start_monitoring(interval_seconds=interval)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Shutting down health monitor...")
        sys.exit(0)

