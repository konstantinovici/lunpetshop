#!/usr/bin/env python3
"""Test Discord webhook connection."""

import asyncio
import httpx
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

async def test_webhook():
    """Send a test message to Discord."""
    if not WEBHOOK_URL:
        print("❌ Error: DISCORD_WEBHOOK_URL not found in .env file!")
        print("Please add it to your .env file:")
        print("DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...")
        return False
    
    print(f"🔗 Testing webhook: {WEBHOOK_URL[:50]}...")
    print()
    
    message = {
        "embeds": [{
            "title": "✅ Discord Webhook Test - LùnPetShop",
            "description": "Testing connection to Discord webhook!",
            "color": 0x00ff00,  # Green
            "timestamp": datetime.utcnow().isoformat(),
            "fields": [
                {
                    "name": "Status",
                    "value": "Webhook is working! 🎉",
                    "inline": False
                },
                {
                    "name": "Next Steps",
                    "value": "Health monitoring will start automatically when you run the backend server.",
                    "inline": False
                }
            ],
            "footer": {
                "text": "LùnPetShop KittyCat Chatbot"
            }
        }]
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            print("📤 Sending test message...")
            response = await client.post(
                WEBHOOK_URL,
                json=message,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            print("✅ SUCCESS! Check your Discord channel - you should see a test message!")
            print(f"   Response status: {response.status_code}")
            return True
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP Error: {e.response.status_code}")
        print(f"   Response: {e.response.text}")
        if e.response.status_code == 404:
            print("   → Webhook URL might be invalid or expired")
        elif e.response.status_code == 401:
            print("   → Webhook token might be invalid")
        return False
    except httpx.TimeoutException:
        print("❌ Timeout: Discord API didn't respond in time")
        return False
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_webhook())
    exit(0 if success else 1)

