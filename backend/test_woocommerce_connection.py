"""Diagnostic script to test WooCommerce API connection and identify issues."""

import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

import httpx
import ssl
from src.woocommerce import WooCommerceClient

def test_direct_connection():
    """Test direct connection to WooCommerce API with various methods."""
    base_url = "https://lunpetshop.com/wp-json/wc/store/v1"
    endpoint = "/products/categories"
    url = f"{base_url}{endpoint}"
    
    print("=" * 60)
    print("WooCommerce API Connection Diagnostic")
    print("=" * 60)
    print(f"Testing connection to: {url}\n")
    
    # Test 1: Basic httpx request
    print("Test 1: Basic httpx request")
    print("-" * 60)
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
            print(f"✅ Success! Status: {response.status_code}")
            print(f"   Response length: {len(response.content)} bytes")
            if response.status_code == 200:
                data = response.json()
                print(f"   Found {len(data)} categories")
            return True
    except httpx.ConnectError as e:
        print(f"❌ Connection Error: {str(e)}")
    except httpx.TimeoutException as e:
        print(f"❌ Timeout: {str(e)}")
    except Exception as e:
        print(f"❌ Error: {type(e).__name__} - {str(e)}")
    
    print()
    
    # Test 2: With custom headers
    print("Test 2: With custom headers (browser-like)")
    print("-" * 60)
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }
        with httpx.Client(timeout=10.0, headers=headers) as client:
            response = client.get(url)
            print(f"✅ Success! Status: {response.status_code}")
            return True
    except Exception as e:
        print(f"❌ Error: {type(e).__name__} - {str(e)}")
    
    print()
    
    # Test 3: With SSL context
    print("Test 3: With custom SSL context")
    print("-" * 60)
    try:
        ssl_context = ssl.create_default_context()
        with httpx.Client(timeout=10.0, verify=ssl_context) as client:
            response = client.get(url)
            print(f"✅ Success! Status: {response.status_code}")
            return True
    except Exception as e:
        print(f"❌ Error: {type(e).__name__} - {str(e)}")
    
    print()
    
    # Test 4: Using WooCommerceClient
    print("Test 4: Using WooCommerceClient class")
    print("-" * 60)
    try:
        client = WooCommerceClient()
        categories = client.get_categories()
        print(f"✅ Success! Found {len(categories)} categories")
        if categories:
            print(f"   First category: {categories[0].get('name', 'N/A')}")
        return True
    except Exception as e:
        print(f"❌ Error: {type(e).__name__} - {str(e)}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # Test 5: Check DNS resolution
    print("Test 5: DNS Resolution")
    print("-" * 60)
    try:
        import socket
        hostname = "lunpetshop.com"
        ip = socket.gethostbyname(hostname)
        print(f"✅ DNS resolved: {hostname} -> {ip}")
    except Exception as e:
        print(f"❌ DNS Error: {str(e)}")
    
    print()
    
    # Test 6: Test HTTP (non-HTTPS) endpoint
    print("Test 6: Testing HTTP endpoint (should redirect)")
    print("-" * 60)
    try:
        http_url = url.replace("https://", "http://")
        with httpx.Client(timeout=10.0, follow_redirects=True) as client:
            response = client.get(http_url)
            print(f"✅ HTTP endpoint accessible (redirected to HTTPS)")
            print(f"   Final URL: {response.url}")
            return True
    except Exception as e:
        print(f"❌ Error: {type(e).__name__} - {str(e)}")
    
    print()
    print("=" * 60)
    print("Diagnostic complete!")
    print("=" * 60)
    
    return False


if __name__ == "__main__":
    success = test_direct_connection()
    sys.exit(0 if success else 1)

