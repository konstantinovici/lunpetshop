# WooCommerce API Connection Issue

## Problem Summary

The WooCommerce API connection is failing with "Connection reset by peer" errors during the TLS handshake. This occurs consistently across all connection methods (httpx, requests, curl, urllib).

## Diagnostic Results

**Date:** 2025-01-XX  
**Server:** `lunpetshop.com`  
**IP:** `137.59.106.220`  
**Endpoint:** `https://lunpetshop.com/wp-json/wc/store/v1/products/categories`

### Test Results:
- ✅ DNS Resolution: Working (lunpetshop.com → 137.59.106.220)
- ❌ HTTPS Connection: Failing (Connection reset during TLS handshake)
- ❌ HTTP Connection: Failing (Connection reset)
- ❌ All HTTP clients: Failing (httpx, requests, curl, urllib)

### Error Pattern:
```
Connection reset by peer [Errno 54]
Occurs during TLS handshake (Client Hello → Server closes connection)
```

## Root Cause Analysis

This is a **server-side issue**. The server is actively closing the connection during the TLS handshake, which suggests:

1. **Firewall/Security Rules**: The server or hosting provider may be blocking connections
2. **Cloudflare/Security Service**: If using Cloudflare or similar, it may be blocking automated clients
3. **Server Configuration**: The web server (nginx/apache) may have security rules blocking certain clients
4. **IP Blocking**: Your IP address may be blocked or rate-limited
5. **TLS/SSL Configuration**: Server may have strict TLS requirements that aren't being met

## Solutions

### Immediate Workarounds (Client-Side)

1. **Mock Data Fallback**: The code now has improved error handling that gracefully handles connection failures
2. **Retry Logic**: Added exponential backoff retry (3 attempts)
3. **User-Friendly Errors**: Vietnamese error messages guide users to contact support

### Server-Side Fixes Required

1. **Check Firewall Rules**: Review server firewall and security rules
2. **Cloudflare Settings**: If using Cloudflare, check:
   - Security level settings
   - Bot fight mode
   - Rate limiting rules
   - IP access rules
3. **Web Server Configuration**: Check nginx/apache logs and security modules
4. **WordPress Security Plugins**: Disable or configure security plugins that might block API access
5. **Whitelist IP**: If the backend server has a static IP, whitelist it
6. **API Authentication**: Consider if the Store API requires authentication (it shouldn't, but check)

### Testing from Different Locations

Try accessing the API from:
- Different network (mobile hotspot, VPN)
- Different IP address
- Browser developer tools (Network tab)
- Online API testing tools (Postman, etc.)

## Current Implementation Status

✅ **Completed:**
- Retry logic with exponential backoff (3 attempts)
- Improved error handling and logging
- User-friendly Vietnamese error messages
- Connection timeout configuration
- Browser-like headers

✅ **Error Handling:**
- Connection errors are caught and logged
- Users see friendly messages in Vietnamese
- Zalo contact information provided as fallback

## Next Steps

1. **Contact Hosting Provider**: Ask them to check firewall/security rules
2. **Check Server Logs**: Review WordPress/WooCommerce server logs for connection attempts
3. **Test from Browser**: Verify the API endpoint works in a browser
4. **Alternative Endpoint**: Check if there's a different API endpoint or authentication method
5. **VPN Test**: Try connecting from a different IP/location to rule out IP blocking

## Code Changes Made

### `backend/src/woocommerce.py`
- Added retry logic (3 attempts)
- Improved error handling for connection failures
- Better logging with connection attempt details
- Improved timeout and SSL configuration

### `backend/src/woocommerce_tools.py`
- Updated error messages to Vietnamese
- Better connection error detection
- User-friendly fallback messages with Zalo contact

## Testing

Run the diagnostic script:
```bash
cd backend
source ../.venv/bin/activate
python3 test_woocommerce_connection.py
```

## References

- WooCommerce Store API: https://woocommerce.github.io/woocommerce-rest-api-docs/
- Error: `[Errno 54] Connection reset by peer`
- TLS Handshake: Connection fails during Client Hello phase

