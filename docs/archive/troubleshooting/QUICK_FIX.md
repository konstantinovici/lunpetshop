# Quick Fix: Use Localhost for WooCommerce API

## The Problem
The backend is trying to connect to `https://lunpetshop.com/wp-json/wc/store/v1` but the connection is being reset (firewall/security blocking external connections).

## The Solution
If your backend runs on the **same server** as WordPress, use `localhost` instead!

## How It Works

### Current Flow:
```
Widget (Browser) → Backend API (localhost:8000) → WooCommerce API (https://lunpetshop.com) ❌ BLOCKED
```

### Fixed Flow:
```
Widget (Browser) → Backend API (localhost:8000) → WooCommerce API (http://localhost) ✅ WORKS!
```

## Setup

Add this to your `.env` file:

```bash
# Use internal URL when backend is on same server as WordPress
WOOCOMMERCE_API_INTERNAL_URL=http://localhost/wp-json/wc/store/v1
```

Or if WordPress is on a different port:
```bash
WOOCOMMERCE_API_INTERNAL_URL=http://localhost:8080/wp-json/wc/store/v1
```

## Test It

```bash
# Test if localhost works
curl http://localhost/wp-json/wc/store/v1/products/categories

# If it works, add to .env and restart backend
echo "WOOCOMMERCE_API_INTERNAL_URL=http://localhost/wp-json/wc/store/v1" >> .env
```

## Why This Works

1. **Same Server**: Backend and WordPress on same server = use localhost
2. **Bypasses Security**: Internal requests don't go through:
   - Cloudflare
   - Firewall rules
   - TLS handshake issues
   - IP blocking
3. **Faster**: Direct internal connection

## Widget Behavior

The widget runs in the **user's browser** and makes requests to your backend API. The backend then connects to WooCommerce. If backend and WordPress are on the same server, using localhost solves the connection issue!

