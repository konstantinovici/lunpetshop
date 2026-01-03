# Devlog: LunPetShop Chatbot - From Overengineering to Done

**Date:** January 2, 2026
**Status:** SHIPPED
**Tags:** `lunpetshop`, `devlog`, `ai-chatbot`, `lessons-learned`

---

## The Journey

### Where We Started

Built a "proper" e-commerce chatbot with:
- LangGraph + xAI Grok integration
- Real-time WooCommerce API tool calling
- Retry logic, connection pooling, error handling
- A measurability framework tracking 8 industry metrics
- Discord health monitoring

The metrics looked terrible:
- Tool Selection Accuracy: 29% (target: 95%)
- Product Search Success: 17% (target: 80%)

I spent weeks trying to fix tool-calling reliability.

### The Realization

Then I asked Tam Anh how sales actually happen:

> "People walk into the shop. Or they message on Zalo. Nobody buys through the website."

The website is informational. The WooCommerce database isn't even accurate - she doesn't always update it when items sell in-store.

**I was optimizing for a use case that doesn't exist.**

### The Fix

Decoupled sync from runtime:

```
BEFORE (complex, unreliable):
User → Chatbot → LLM → Tool Call → WooCommerce API → Response
                         ↓
              (network failures, timeouts, retries)

AFTER (simple, fast):
Daily: sync_products.py → products_cache.json
Runtime: User → Chatbot → LLM → Local JSON → Response
```

No more API calls at runtime. No more tool-calling failures. No more connection issues.

---

## How It Works Now

### Architecture

```
┌─────────────────────────────────────────────────┐
│  sync_products.py (daily or manual)             │
│  WooCommerce API → products_cache.json          │
└─────────────────────────────────────────────────┘
                    ↓ (555 products)
              [products_cache.json]
                    ↓
┌─────────────────────────────────────────────────┐
│  Chatbot (runtime)                              │
│  User message → LLM + cached context → Response │
│  No network calls. No tool calling. Fast.       │
└─────────────────────────────────────────────────┘
```

### Key Files

| File | Purpose |
|------|---------|
| `backend/scripts/sync_products.py` | Pulls products from WooCommerce, saves to JSON |
| `backend/scripts/trigger_sync.sh` | Wrapper script for manual sync |
| `backend/data/products_cache.json` | 555 products, refreshed daily |
| `backend/src/knowledge_base.py` | Loads cache, provides product text to LLM |
| `backend/src/chatbot.py` | Simple LangGraph flow, no tools |
| `backend/src/prompts.py` | Injects full product catalog into system prompt |

### To Sync Products

```bash
cd backend && ./scripts/trigger_sync.sh
```

Takes ~8 seconds. Fetches 555 products across 6 API pages.

### What the Chatbot Can Do

1. **Product queries:** "Có sản phẩm gì cho mèo?" → Lists cat products with prices
2. **Contact info:** "Địa chỉ cửa hàng?" → Address, Zalo, hours
3. **Business info:** "Giờ mở cửa?" → 8:00 AM - 9:30 PM
4. **Bilingual:** Responds in Vietnamese or English based on user's language

---

## What We Learned

### 1. Understand the business before architecting

I assumed e-commerce chatbot = real-time inventory. Wrong. Sales happen via Zalo and foot traffic.

### 2. "Proper engineering" means matching solution to problem

Real-time API calls aren't "better" than cached data. For a shop that updates products sporadically, daily sync is more than sufficient.

### 3. Metrics can mislead

I built a framework measuring tool-calling accuracy. But improving that metric wouldn't have improved actual user value.

### 4. The demo trap

When building for a friend, it's easy to scope-creep into enterprise patterns. Fight it.

### 5. Done > Perfect

The best architecture is the one that lets you call something "done" and move on.

---

## Current State

| Component | Status |
|-----------|--------|
| Product sync | ✅ Working (555 products) |
| Chatbot | ✅ Simplified, no API calls |
| Widget UI | ✅ Deployed |
| WordPress plugin | ✅ Ready |

**Last sync:** January 2, 2026
**Cache size:** 244KB
**Response time:** Fast (no network calls)

---

## Next Steps

### Immediate
- [ ] Show Tam Anh the working chatbot
- [ ] Deploy to production (lunpetshop.com)
- [ ] Set up daily cron for `sync_products.py` (optional)

### Future (only if needed)
- [ ] Improve category detection (currently uses keyword matching)
- [ ] Add product search within chatbot responses
- [ ] Template this pattern for other local businesses

### Not Doing
- ❌ Chasing 95% tool-calling accuracy
- ❌ Real-time inventory checks
- ❌ Complex retry/fallback logic
- ❌ Enterprise-grade monitoring

---

## The Meta-Lesson

This project stalled for weeks because I was solving the wrong problem. The breakthrough came from asking:

> "What are we actually trying to achieve?"

Not "how do we improve the metrics?" but "what does Tam Anh need?"

The answer: A friendly chatbot that tells customers what products exist and how to contact the shop.

That's it. That's the product. And now it's done.

---

*Deadline was December 31. Shipped January 2. Two days late, but done is done.*
