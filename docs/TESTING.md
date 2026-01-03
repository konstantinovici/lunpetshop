# LunPetShop Chatbot - Testing Guide

## Overview

This document describes how to verify the chatbot is working correctly on production.

## Test Environment

- **Production URL**: lunpetshop.com
- **Backend Health**: `{API_BASE_URL}/health`
- **Chat Endpoint**: `{API_BASE_URL}/api/chat`

## Running Tests

### Quick Health Check

```bash
curl -s {API_BASE_URL}/health
# Expected: {"status":"healthy","service":"LùnPetShop KittyCat Chatbot"}
```

### Product Query Tests

These tests verify the chatbot returns real product data from the cache (not hallucinations).

#### 1. Cat Pate Query (Vietnamese)

```bash
curl -s -X POST "{API_BASE_URL}/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Co pate meo nao?", "language": "vi"}'
```

**Expected products (from cache):**
- Pate Kucinta gói 80g: 11.000 ₫
- Pate wanpy happy 100 70g: 11.000 ₫
- Pate Snappy Tom vị trái cây 70g: 16.000 ₫
- Pate Mèo mọi lứa tuổi MeowCat 70g: 12.000 ₫
- Pate Whiskas 85g: 12.000 ₫
- Pate Ciao 40g: 12.000 ₫

#### 2. Dog Food Query (English)

```bash
curl -s -X POST "{API_BASE_URL}/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What dog food do you have?", "language": "en"}'
```

**Expected products (from cache):**
- Hạt Today's Dinner cho chó mọi lứa tuổi 1kg: 100.000 ₫
- Thức Ăn Hạt Maxime Elite Cho Chó Trưởng Thành – Vị Bò: 55.000 ₫
- Thức Ăn Hạt Cho Chó Mọi Lứa Tuổi HUG Túi 2kg Hàn Quốc: 150.000 ₫
- HẠT MỀM CHO CHÓ ISKHAN 400g: 60.000 ₫

#### 3. Spa Services Query

```bash
curl -s -X POST "{API_BASE_URL}/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Dich vu spa?", "language": "vi"}'
```

**Expected services (from cache):**
- Spa Cạo lông mèo dưới 2kg: 100.000 ₫
- Spa Cạo lông mèo trên 4kg: 180.000 ₫
- Spa Combo tắm cạo lông mèo: 180.000 - 280.000 ₫
- Spa Bấm móng: 20.000 ₫

### Business Info Tests

#### 4. Store Address

```bash
curl -s -X POST "{API_BASE_URL}/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Dia chi cua hang?", "language": "vi"}'
```

**Expected:** 46 Văn Cận, Khuê Trung, Cẩm Lệ, Đà Nẵng 550000

#### 5. Contact Info (Zalo)

```bash
curl -s -X POST "{API_BASE_URL}/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Zalo?", "language": "en"}'
```

**Expected:** 0935005762

#### 6. Business Hours

```bash
curl -s -X POST "{API_BASE_URL}/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Mo cua may gio?", "language": "vi"}'
```

**Expected:** 8:00 AM – 9:30 PM

### Conversation Tests

#### 7. Vietnamese Greeting

```bash
curl -s -X POST "{API_BASE_URL}/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Xin chao", "language": "vi"}'
```

**Expected:** Friendly greeting in Vietnamese, mentions can help with products/info

#### 8. English Greeting

```bash
curl -s -X POST "{API_BASE_URL}/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "language": "en"}'
```

**Expected:** Friendly greeting in English

## Verifying Data Parity

To ensure chatbot responses match actual WooCommerce data:

### 1. Check Cache Freshness

```bash
cat backend/data/products_cache.json | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(f'Last sync: {d[\"last_sync\"]}')
print(f'Total products: {d[\"total_products\"]}')
print(f'Status: {d[\"sync_status\"]}')
"
```

### 2. Re-sync from WooCommerce (if needed)

```bash
cd backend && uv run python scripts/sync_products.py
```

### 3. Compare with Live WooCommerce

The cache should be synced regularly. To verify a specific product:

1. Check product in cache: `grep "product_name" backend/data/products_cache.json`
2. Verify on website: `https://lunpetshop.com/sanpham/`
3. If discrepancy found, re-run sync

## Test Checklist

Use this checklist when deploying or after changes:

- [ ] Backend health endpoint responds
- [ ] Cat product query returns real products with correct prices
- [ ] Dog product query returns real products with correct prices
- [ ] Address query returns correct address
- [ ] Zalo query returns 0935005762
- [ ] Hours query returns 8:00 AM – 9:30 PM
- [ ] Vietnamese queries get Vietnamese-friendly responses
- [ ] English queries get English responses
- [ ] No hallucinated product names or prices
- [ ] Cache is less than 7 days old (or manually synced)

## Automated Test Script

Save as `test_production.sh`:

```bash
#!/bin/bash
API_BASE="${1:-https://your-tunnel-url.trycloudflare.com}"

echo "Testing: $API_BASE"
echo "========================"

# Health check
echo -n "Health check: "
HEALTH=$(curl -s "$API_BASE/health" | grep -o '"status":"healthy"')
[ -n "$HEALTH" ] && echo "PASS" || echo "FAIL"

# Product query
echo -n "Product query: "
PRODUCTS=$(curl -s -X POST "$API_BASE/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "pate meo", "language": "vi"}' | grep -o "Kucinta\|Whiskas\|Snappy")
[ -n "$PRODUCTS" ] && echo "PASS" || echo "FAIL"

# Address query
echo -n "Address query: "
ADDR=$(curl -s -X POST "$API_BASE/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "dia chi", "language": "vi"}' | grep -o "46 Văn Cận\|Khuê Trung\|Đà Nẵng")
[ -n "$ADDR" ] && echo "PASS" || echo "FAIL"

# Zalo query
echo -n "Zalo query: "
ZALO=$(curl -s -X POST "$API_BASE/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "zalo", "language": "en"}' | grep -o "0935005762")
[ -n "$ZALO" ] && echo "PASS" || echo "FAIL"

echo "========================"
echo "Done"
```

## Known Limitations

1. **Cache-based**: Data is only as fresh as last sync (not real-time inventory)
2. **Tunnel URL changes**: Quick tunnels rotate URLs on restart
3. **No transaction capability**: Chatbot is informational only, purchases via Zalo

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Failed to fetch" | Backend not running or tunnel down |
| Wrong prices | Re-run sync_products.py |
| Old products | Check last_sync date, re-sync if stale |
| No response | Check API logs, verify XAI_API_KEY |
