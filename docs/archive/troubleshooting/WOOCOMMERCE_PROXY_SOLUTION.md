# WooCommerce API Connection Solution

## Architecture

- **Backend**: Runs on your local machine (`localhost:8000`)
- **WordPress & Widget**: Run on remote server (`lunpetshop.com`)
- **Widget**: Runs in user's browser when they visit the site

## The Problem

```
Widget (Browser on lunpetshop.com) 
  → Backend API (localhost:8000 via tunnel) 
  → WooCommerce API (https://lunpetshop.com) ❌ BLOCKED
```

The backend (local machine) tries to connect to WooCommerce API (remote server) and gets blocked by firewall/security.

## Solution Options

### Option 1: WordPress Proxy Endpoint (Recommended)

Create a WordPress plugin endpoint that proxies WooCommerce requests. The backend calls this proxy instead of WooCommerce directly.

**Advantages:**
- ✅ Backend calls WordPress (same server), not blocked
- ✅ WordPress proxy calls WooCommerce (internal, works)
- ✅ No CORS issues
- ✅ Server-side caching possible

**Implementation:**
Add to WordPress plugin:
```php
// Proxy endpoint for backend to access WooCommerce
add_action('rest_api_init', function() {
    register_rest_route('lunpetshop/v1', '/woocommerce-proxy/(?P<endpoint>.*)', [
        'methods' => 'GET',
        'callback' => 'lunpetshop_woocommerce_proxy',
        'permission_callback' => '__return_true'
    ]);
});

function lunpetshop_woocommerce_proxy($request) {
    $endpoint = $request['endpoint'];
    $params = $request->get_query_params();
    
    // Build WooCommerce API URL
    $wc_url = home_url('/wp-json/wc/store/v1/' . $endpoint);
    if (!empty($params)) {
        $wc_url .= '?' . http_build_query($params);
    }
    
    // Make internal request to WooCommerce
    $response = wp_remote_get($wc_url);
    
    if (is_wp_error($response)) {
        return new WP_Error('proxy_error', $response->get_error_message(), ['status' => 500]);
    }
    
    $body = wp_remote_retrieve_body($response);
    $status = wp_remote_retrieve_response_code($response);
    
    return new WP_REST_Response(json_decode($body), $status);
}
```

Then backend uses:
```python
# In .env
WOOCOMMERCE_API_BASE_URL=https://lunpetshop.com/wp-json/lunpetshop/v1/woocommerce-proxy
```

### Option 2: Widget Direct Requests (If CORS Allows)

Have the widget make direct requests to WooCommerce API from the browser.

**Advantages:**
- ✅ Same-origin requests (no CORS if configured)
- ✅ Bypasses backend connection issues
- ✅ Faster (direct connection)

**Disadvantages:**
- ❌ Requires CORS configuration on WooCommerce
- ❌ No server-side caching
- ❌ Exposes API structure to client

**Implementation:**
Modify widget to call WooCommerce directly when on same origin:
```javascript
// In chat-widget.js
async fetchWooCommerceData(endpoint) {
    // If on same origin, call directly
    if (window.location.origin === 'https://lunpetshop.com') {
        const response = await fetch(`/wp-json/wc/store/v1/${endpoint}`);
        return response.json();
    }
    // Otherwise go through backend
    return this.fetchFromBackend(endpoint);
}
```

### Option 3: Fix Server-Side Blocking

Contact hosting provider to:
1. Whitelist your backend's IP address
2. Check Cloudflare security settings
3. Review firewall rules

## Recommended: Option 1 (WordPress Proxy)

This is the cleanest solution that:
- Works with current architecture
- No CORS issues
- Maintains security
- Allows caching

## Quick Test

Test if WordPress can access WooCommerce internally:
```bash
# SSH into WordPress server and test
curl http://localhost/wp-json/wc/store/v1/products/categories
```

If that works, the proxy solution will work!

