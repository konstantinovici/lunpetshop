#!/usr/bin/env python3
"""Test script to reproduce production error scenario.

This simulates what happens when:
1. Backend is running locally
2. Tunnel is down or unreachable
3. Widget tries to connect to tunnel URL
"""

import asyncio
import httpx
import os
from pathlib import Path

# Try to get tunnel URL from file
tunnel_url_file = Path(__file__).parent.parent / ".pids" / "tunnel.url"
tunnel_url = None
if tunnel_url_file.exists():
    tunnel_url = tunnel_url_file.read_text().strip()

async def test_scenario():
    """Test different scenarios that could cause the error."""
    print("🔍 Testing Production Error Scenarios")
    print("=" * 60)
    print()
    
    # Scenario 1: Test local backend
    print("📋 Scenario 1: Local Backend Health")
    print("-" * 60)
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:8000/health/metrics")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Local backend is running")
                print(f"   Status: {data.get('status')}")
                print(f"   Chat endpoint test: {data.get('endpoints', {}).get('chat', {}).get('status', 'unknown')}")
            else:
                print(f"❌ Local backend returned {response.status_code}")
    except Exception as e:
        print(f"❌ Local backend not accessible: {e}")
    print()
    
    # Scenario 2: Test tunnel URL (if available)
    if tunnel_url:
        print(f"📋 Scenario 2: Tunnel URL ({tunnel_url})")
        print("-" * 60)
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Test health endpoint
                response = await client.get(f"{tunnel_url}/health")
                if response.status_code == 200:
                    print(f"✅ Tunnel is accessible")
                    print(f"   Response: {response.json()}")
                else:
                    print(f"⚠️  Tunnel returned {response.status_code}")
        except httpx.TimeoutException:
            print(f"❌ Tunnel timeout - tunnel is likely down!")
            print(f"   This is probably the error you're seeing in production")
        except httpx.ConnectError:
            print(f"❌ Tunnel connection error - tunnel is down!")
            print(f"   This is probably the error you're seeing in production")
        except Exception as e:
            print(f"❌ Tunnel error: {type(e).__name__}: {e}")
    else:
        print("📋 Scenario 2: No tunnel URL found")
        print("-" * 60)
        print("⚠️  No tunnel URL file found - tunnel might not be running")
    print()
    
    # Scenario 3: Test chat endpoint via tunnel
    if tunnel_url:
        print(f"📋 Scenario 3: Chat Endpoint via Tunnel")
        print("-" * 60)
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{tunnel_url}/api/chat",
                    json={"message": "hi", "language": "vi"},
                    headers={"Content-Type": "application/json"}
                )
                if response.status_code == 200:
                    print(f"✅ Chat endpoint works via tunnel")
                    print(f"   Response: {response.json().get('response', '')[:50]}...")
                else:
                    print(f"❌ Chat endpoint returned {response.status_code}")
                    print(f"   Error: {response.text[:200]}")
        except httpx.TimeoutException:
            print(f"❌ TIMEOUT - This is the error users see!")
            print(f"   Widget shows: 'Xin lỗi, đã có lỗi xảy ra...'")
        except httpx.ConnectError:
            print(f"❌ CONNECTION ERROR - This is the error users see!")
            print(f"   Widget shows: 'Xin lỗi, đã có lỗi xảy ra...'")
        except Exception as e:
            print(f"❌ Error: {type(e).__name__}: {e}")
    print()
    
    # Scenario 4: Test chat endpoint locally
    print("📋 Scenario 4: Chat Endpoint Locally")
    print("-" * 60)
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                "http://localhost:8000/api/chat",
                json={"message": "hi", "language": "vi"},
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Local chat endpoint works")
                print(f"   Response: {data.get('response', '')[:50]}...")
            else:
                print(f"❌ Local chat endpoint returned {response.status_code}")
    except Exception as e:
        print(f"❌ Local chat endpoint error: {e}")
    print()
    
    print("=" * 60)
    print("💡 Diagnosis:")
    print()
    if tunnel_url:
        print("If Scenario 2 or 3 failed with timeout/connection error:")
        print("  → Tunnel is down - this is why production shows errors")
        print("  → Solution: Restart tunnel or check network connection")
    else:
        print("No tunnel URL found:")
        print("  → Tunnel is not running")
        print("  → Production widget can't reach backend")
        print("  → Solution: Start tunnel with: ./bin/start-tunnel.sh")
    print()
    print("Health metrics show 'healthy' because:")
    print("  → Local backend is running fine")
    print("  → But tunnel (public URL) is down")
    print("  → Production widget can't reach backend through tunnel")

if __name__ == "__main__":
    asyncio.run(test_scenario())

