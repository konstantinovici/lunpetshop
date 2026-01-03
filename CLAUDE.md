# CLAUDE.md - LunPetShop AI Chatbot

## Project Status: IN PROGRESS

**What works:**
- Business info queries (100%)
- Contact info queries (100%)
- General conversation (100%)
- Widget UI deployed

**What's left to finish:**
1. Build `sync_products.py` - WooCommerce → local cache (daily/manual)
2. Simplify chatbot - read from cache instead of live API calls
3. Deploy final version

See: `docs/REFLECTION_2024_Chatbot_Goals_and_Architecture.md` for full context.

## Business Context

**Reality of LunPetShop:**
- Sales happen in-store or via Zalo (not website)
- Website is informational, not transactional
- Owner doesn't always update WooCommerce inventory
- This is a demo/favor for a friend, not critical business tool

**What chatbot needs to do:**
- Answer "what products do you have for cats/dogs?"
- Answer "what's your address/Zalo/hours?"
- Be friendly and bilingual (Vietnamese/English)

**What it does NOT need:**
- Real-time inventory checks
- Complex tool-calling orchestration
- E-commerce checkout flow

## Target Architecture

```
Daily Sync Job (or manual)
sync_products.py: WooCommerce API → products_cache.json
                         ↓
User → Chatbot → LLM → Local lookup → fast, reliable
```

No live WooCommerce API calls at runtime.

## Tech Stack

- **Backend**: Python 3.9+, FastAPI, LangGraph
- **LLM**: xAI Grok
- **Frontend**: Vanilla JS widget
- **WordPress**: PHP plugin

## Project Structure

```
lunpetshop/
├── backend/
│   ├── src/
│   │   ├── api.py           # FastAPI routes
│   │   ├── chatbot.py       # LangGraph implementation
│   │   ├── knowledge_base.py # Product & business data
│   │   └── woocommerce.py   # WooCommerce integration (to be simplified)
│   ├── data/
│   │   └── products_cache.json  # Cached product data
│   └── main.py
├── widget/            # Widget UI (single source of truth)
├── wordpress-plugin/
├── bin/
└── docs/
    └── REFLECTION_2024_Chatbot_Goals_and_Architecture.md  # READ THIS
```

## Commands

```bash
# Start server
cd backend && python main.py

# Run tests
cd backend && python test_chatbot.py

# Build WordPress plugin
./bin/build-plugin.sh
```

## Environment

Required in `.env`:
- `XAI_API_KEY` - from https://console.x.ai/
