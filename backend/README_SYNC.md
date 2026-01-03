# Product Sync System

The LùnPetShop chatbot uses a **daily sync** system to keep product data up-to-date.

## Overview

```
WooCommerce API  →  sync_products.py  →  products_cache.json  →  Chatbot
     (remote)         (daily/manual)         (local file)        (reads cache)
```

**Why this approach?**
- Chatbot never waits on WooCommerce API (fast responses)
- Works even if WooCommerce is down
- Daily sync is more than enough (owner doesn't update products often)
- Simple to debug (check the JSON file)

## Quick Start

### Manual Sync (When Products Change)

```bash
# From project root
./backend/scripts/trigger_sync.sh

# Or directly
cd backend
python scripts/sync_products.py
```

### Setup Daily Automatic Sync

```bash
# Run once to add cron job
./bin/setup-cron.sh
```

This adds a cron job that runs at 2:00 AM daily.

## Files

| File | Purpose |
|------|---------|
| `backend/scripts/sync_products.py` | Main sync script |
| `backend/scripts/trigger_sync.sh` | Manual trigger wrapper |
| `backend/data/products_cache.json` | Cached product data |
| `bin/setup-cron.sh` | Cron job setup script |
| `logs/sync.log` | Sync log file |

## Cache File Structure

```json
{
  "last_sync": "2024-12-23T15:30:00Z",
  "total_products": 245,
  "sync_status": "success",
  "categories": {
    "cat": {
      "food": {
        "count": 31,
        "products": [
          {
            "id": 123,
            "name": "Thức ăn hạt GV trộn siêu cấp cho mèo",
            "price": "80.000 ₫",
            "description": "...",
            "url": "https://lunpetshop.com/product/...",
            "in_stock": true
          }
        ]
      }
    },
    "dog": { ... },
    "general": { ... }
  }
}
```

## Checking Sync Status

### Check Last Sync Time

```bash
# View cache file header
head -5 backend/data/products_cache.json
```

### Check Sync Logs

```bash
# View recent sync logs
tail -50 logs/sync.log
```

### Check Product Counts

```bash
# Quick summary
cat backend/data/products_cache.json | python -c "
import json, sys
data = json.load(sys.stdin)
print(f\"Last sync: {data.get('last_sync', 'Never')}\")
print(f\"Total products: {data.get('total_products', 0)}\")
for pet in ['cat', 'dog', 'general']:
    cats = data.get('categories', {}).get(pet, {})
    total = sum(c.get('count', 0) for c in cats.values())
    print(f\"  {pet}: {total} products\")
"
```

## Troubleshooting

### Sync Failed

1. **Check WooCommerce connection:**
   ```bash
   # Test API connection
   curl -s "https://lunpetshop.com/wp-json/wc/store/v1/products?per_page=1" | head -100
   ```

2. **Check environment variables:**
   ```bash
   # Verify .env has WooCommerce settings
   cat backend/.env | grep WOOCOMMERCE
   ```

3. **Check logs:**
   ```bash
   tail -100 logs/sync.log
   ```

### Cache File Missing

If `products_cache.json` doesn't exist, the chatbot uses fallback data (hardcoded product counts). Run a manual sync to create it:

```bash
./backend/scripts/trigger_sync.sh
```

### Chatbot Shows Old Data

1. Check when last sync happened:
   ```bash
   head -3 backend/data/products_cache.json
   ```

2. Run manual sync:
   ```bash
   ./backend/scripts/trigger_sync.sh
   ```

3. Restart the backend server to reload cache.

## For Tam Anh (Shop Owner)

**Khi nào cần chạy sync?**
- Khi thêm sản phẩm mới
- Khi thay đổi giá
- Khi xóa sản phẩm

**Cách chạy:**
```bash
cd lunpetshop
./backend/scripts/trigger_sync.sh
```

**Không cần lo:**
- Sync tự động chạy mỗi ngày lúc 2:00 sáng
- Nếu quên sync, dữ liệu cũ vẫn hoạt động bình thường

## Architecture Notes

### Why Not Real-Time API?

1. **Business reality:** Most sales happen in-store or via Zalo, not website
2. **Data freshness:** Owner doesn't update WooCommerce frequently
3. **Reliability:** Cached data always available, even if WooCommerce is down
4. **Performance:** No API latency for chatbot responses

### Fallback Behavior

If cache is missing or invalid:
1. Chatbot uses hardcoded fallback data (approximate product counts)
2. Still answers business info questions correctly
3. Guides users to contact Zalo for specific product questions

---

*Last updated: December 2024*


