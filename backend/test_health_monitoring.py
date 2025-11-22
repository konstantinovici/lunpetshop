#!/usr/bin/env python3
"""Test the complete health monitoring system with Discord integration."""

import os
import sys
import asyncio
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
project_root = backend_dir.parent
sys.path.insert(0, str(backend_dir))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(project_root / ".env")

from src.discord_monitor import DiscordHealthMonitor


async def test_health_monitoring():
    """Test the health monitoring system."""
    print("🐱 LùnPetShop Chatbot - Health Monitoring Test")
    print("=" * 60)
    print()
    
    # Check webhook URL
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("❌ Error: DISCORD_WEBHOOK_URL not found in .env file!")
        return False
    
    print(f"✅ Discord webhook URL found")
    print(f"   {webhook_url[:50]}...")
    print()
    
    # Initialize monitor
    health_url = os.getenv("HEALTH_CHECK_URL", "http://localhost:8000/health/metrics")
    monitor = DiscordHealthMonitor(webhook_url=webhook_url, health_url=health_url)
    
    if not monitor.enabled:
        print("❌ Monitor not enabled!")
        return False
    
    print(f"✅ Monitor initialized")
    print(f"   Health URL: {health_url}")
    print()
    
    # Test 1: Check if health endpoint is accessible
    print("🔍 Test 1: Checking health endpoint...")
    try:
        metrics = await monitor.check_health()
        if metrics and "error" in metrics:
            print(f"   ⚠️  Health endpoint not accessible: {metrics.get('error')}")
            print("   → This is OK if the backend isn't running")
            print("   → We'll send an error report to Discord")
        else:
            print("   ✅ Health endpoint accessible!")
            print(f"   Status: {metrics.get('status', 'unknown')}")
    except Exception as e:
        print(f"   ⚠️  Error checking health: {e}")
    
    print()
    
    # Test 2: Send test report to Discord
    print("📤 Test 2: Sending test health report to Discord...")
    success = await monitor.send_report(metrics if 'metrics' in locals() else None)
    
    if success:
        print("   ✅ Test report sent successfully!")
        print("   → Check your Discord channel for the health report")
    else:
        print("   ❌ Failed to send report")
        return False
    
    print()
    print("=" * 60)
    print("✅ All tests completed!")
    print()
    print("Next steps:")
    print("1. Start your backend server: cd backend && python main.py")
    print("2. The Discord monitor will start automatically")
    print("3. Health reports will be sent every hour (configurable)")
    print()
    
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(test_health_monitoring())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Test interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

