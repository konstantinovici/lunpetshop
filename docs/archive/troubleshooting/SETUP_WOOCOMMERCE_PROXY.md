# Setup WooCommerce Proxy Solution

## Problem Solved

Your backend (local machine) can't connect to WooCommerce API (remote server) due to firewall/security blocking. The solution: use WordPress as a proxy!

## Architecture

```
Widget (Browser) 
  → Backend API (localhost:8000) 
  → WordPress Proxy Endpoint (lunpetshop.com/wp-json/lunpetshop/v1/woocommerce-proxy/...)
  → WooCommerce API (internal, same server) ✅ WORKS!
```

## Setup Steps

### 1. Update WordPress Plugin

The plugin has been updated with a proxy endpoint. Make sure you have the latest version installed.

**Endpoint:** `https://lunpetshop.com/wp-json/lunpetshop/v1/woocommerce-proxy/{endpoint}`

### 2. Configure Backend

Add to your `.env` file:

```bash
# Use WordPress proxy endpoint (recommended for remote backend)
WOOCOMMERCE_API_PROXY_URL=https://lunpetshop.com/wp-json/lunpetshop/v1/woocommerce-proxy
```

### 3. Test the Proxy

```bash
# Test the proxy endpoint directly
curl "https://lunpetshop.com/wp-json/lunpetshop/v1/woocommerce-proxy/products/categories"

# Should return WooCommerce categories
```

### 4. Test from Backend

```bash
cd backend
source ../.venv/bin/activate
export WOOCOMMERCE_API_PROXY_URL=https://lunpetshop.com/wp-json/lunpetshop/v1/woocommerce-proxy
python3 -c "from src.woocommerce import WooCommerceClient; c = WooCommerceClient(); print(c.get_categories())"
```

## How It Works

1. **Backend** calls WordPress proxy endpoint (public, accessible)
2. **WordPress** receives request and calls WooCommerce API internally (same server, no blocking)
3. **WordPress** returns WooCommerce data to backend
4. **Backend** processes and returns to widget

## Benefits

- ✅ Bypasses firewall/security blocks
- ✅ No CORS issues
- ✅ WordPress handles internal connection
- ✅ Can add caching/rate limiting in WordPress if needed
- ✅ Secure (WordPress can add authentication if needed)

## Alternative Options

If proxy doesn't work, you can also try:

### Option 1: Internal URL (if backend moves to same server)
```bash
WOOCOMMERCE_API_INTERNAL_URL=http://localhost/wp-json/wc/store/v1
```

### Option 2: Direct URL (may be blocked)
```bash
WOOCOMMERCE_API_BASE_URL=https://lunpetshop.com/wp-json/wc/store/v1
```

## Troubleshooting

### Proxy returns 404
- Check that WordPress plugin is activated
- Verify REST API is enabled: `https://lunpetshop.com/wp-json/`

### Proxy returns 500
- Check WordPress error logs
- Verify WooCommerce is installed and Store API is enabled
- Test WooCommerce directly: `https://lunpetshop.com/wp-json/wc/store/v1/products/categories`

### Still getting connection errors
- Check that `WOOCOMMERCE_API_PROXY_URL` is set correctly in `.env`
- Restart backend after changing `.env`
- Check backend logs for detailed error messages

## Next Steps

1. ✅ Plugin updated with proxy endpoint
2. ✅ Backend code updated to support proxy URL
3. ⏳ Add `WOOCOMMERCE_API_PROXY_URL` to `.env`
4. ⏳ Test the connection
5. ⏳ Deploy and verify

