# WooCommerce API Connection Solution

## The Problem

The backend server is trying to connect to WooCommerce API via the public HTTPS URL (`https://lunpetshop.com/wp-json/wc/store/v1`), but the connection is being reset during TLS handshake. This is likely due to:
- Firewall rules blocking external connections
- Cloudflare/security services blocking automated clients
- Server security configuration

## The Solution: Use Internal/Localhost URL

**Key Insight:** If the backend runs on the same server as WordPress, it should use the **internal/localhost URL** instead of the public HTTPS URL!

### Why This Works

1. **Same-Origin Requests**: When backend and WordPress are on the same server, use `localhost` or internal network
2. **Bypasses Security**: Internal requests don't go through:
   - Cloudflare
   - Public firewall rules
   - TLS handshake issues
   - IP blocking
3. **Faster**: Direct internal connection is faster than going through public internet

## Implementation

The code now supports two environment variables:

### Option 1: Internal URL (Recommended for Same Server)
```bash
# In .env file
WOOCOMMERCE_API_INTERNAL_URL=http://localhost/wp-json/wc/store/v1
# OR if WordPress is on a different port:
WOOCOMMERCE_API_INTERNAL_URL=http://localhost:8080/wp-json/wc/store/v1
# OR if using Docker/internal network:
WOOCOMMERCE_API_INTERNAL_URL=http://wordpress:80/wp-json/wc/store/v1
```

### Option 2: Public URL (For Remote Backend)
```bash
# In .env file
WOOCOMMERCE_API_BASE_URL=https://lunpetshop.com/wp-json/wc/store/v1
```

### Priority Order
1. `WOOCOMMERCE_API_INTERNAL_URL` (if set, use this - for same-server deployments)
2. `base_url` parameter (if passed to constructor)
3. `WOOCOMMERCE_API_BASE_URL` (if set)
4. Default: `https://lunpetshop.com/wp-json/wc/store/v1`

## Deployment Scenarios

### Scenario 1: Backend on Same Server as WordPress
```bash
# .env
WOOCOMMERCE_API_INTERNAL_URL=http://localhost/wp-json/wc/store/v1
```
✅ **This will work!** Internal connection bypasses all security blocks.

### Scenario 2: Backend on Different Server (Remote)
```bash
# .env
WOOCOMMERCE_API_BASE_URL=https://lunpetshop.com/wp-json/wc/store/v1
```
⚠️ **May have connection issues** if server blocks external connections.

### Scenario 3: Docker/Container Setup
```bash
# .env
WOOCOMMERCE_API_INTERNAL_URL=http://wordpress-container:80/wp-json/wc/store/v1
# OR if using docker-compose service name:
WOOCOMMERCE_API_INTERNAL_URL=http://wordpress:80/wp-json/wc/store/v1
```

## Testing

### Test Internal Connection
```bash
# If WordPress is on localhost
curl http://localhost/wp-json/wc/store/v1/products/categories

# If WordPress is on port 8080
curl http://localhost:8080/wp-json/wc/store/v1/products/categories
```

### Test from Backend
```bash
cd backend
source ../.venv/bin/activate
export WOOCOMMERCE_API_INTERNAL_URL=http://localhost/wp-json/wc/store/v1
python3 -c "from src.woocommerce import WooCommerceClient; c = WooCommerceClient(); print(c.get_categories())"
```

## Widget Behavior

The widget itself runs in the **user's browser**, so:
- Widget → Backend API: Works (via tunnel or public URL)
- Backend → WooCommerce: **Should use internal URL** if on same server

The widget doesn't directly access WooCommerce - it goes through the backend, which then accesses WooCommerce.

## Next Steps

1. **Check your deployment**: Is the backend on the same server as WordPress?
2. **Set internal URL**: Add `WOOCOMMERCE_API_INTERNAL_URL` to `.env` if on same server
3. **Test connection**: Run the test script with internal URL
4. **Verify**: Check that WooCommerce API is accessible via localhost/internal network

## Alternative: Browser-Based Approach (Not Recommended)

If you wanted the widget to access WooCommerce directly from the browser:
- ❌ CORS issues (WooCommerce API may not allow cross-origin)
- ❌ Security concerns (exposing API endpoints to client)
- ❌ No server-side caching/optimization
- ✅ Would work if CORS is configured, but not recommended

**Better approach**: Keep widget → backend → WooCommerce flow, but use internal URL for backend → WooCommerce connection.

