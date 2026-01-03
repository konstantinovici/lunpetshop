# CLAUDE.md - LunPetShop AI Chatbot

## Project Status: SHIPPED v1.1.0

**Deployed:** January 3, 2026

**What works:**
- Product queries from cached data (555 products)
- Business info queries (address, hours, Zalo)
- Bilingual conversation (Vietnamese/English)
- Widget UI on lunpetshop.com

**Production URLs:**
- Widget: https://lunpetshop.com (WordPress plugin installed)
- Backend: https://media.bluume.space/lunpetshop (on HW server)

## Architecture

```
Daily/Manual Sync:
  sync_products.py → products_cache.json (555 products)

Runtime:
  User → Widget → Backend API → LLM + cached context → Response
         ↓
  https://media.bluume.space/lunpetshop/api/chat
```

No live WooCommerce API calls at runtime. Fast and reliable.

## Project Structure

```
lunpetshop/
├── CLAUDE.md              # This file
├── README.md
├── backend/
│   ├── main.py            # FastAPI entry point
│   ├── README_SYNC.md     # Sync guide
│   ├── data/
│   │   └── products_cache.json
│   ├── scripts/
│   │   └── sync_products.py
│   └── src/
│       ├── api.py         # Routes
│       ├── chatbot.py     # LangGraph
│       ├── knowledge_base.py
│       └── prompts.py
├── bin/                   # Utility scripts
├── docs/
│   ├── TESTING.md         # Test guide
│   ├── SERVER_DEPLOYMENT.md
│   └── archive/           # Old docs
├── widget/                # Chat widget UI
└── wordpress-plugin/      # WP plugin
```

## Commands

```bash
# Local development
cd backend && uv run python main.py

# Sync products from WooCommerce
cd backend && uv run python scripts/sync_products.py

# Build WordPress plugin
./bin/build-plugin.sh

# Run tests (see docs/TESTING.md)
curl https://media.bluume.space/lunpetshop/health
```

## Server Deployment

Backend runs on HW's server at `/var/www/lunpetshop/`

See: `docs/SERVER_DEPLOYMENT.md` for full details.

**TODO:** Fix env loading issue - add `PORT=3002` to server's `.env` file.

## Environment

Required in `.env`:
- `XAI_API_KEY` - from https://console.x.ai/
- `PORT` - 8000 locally, 3002 on server

## Key Documents

- `docs/TESTING.md` - How to verify the chatbot works
- `docs/SERVER_DEPLOYMENT.md` - Server setup and nginx config
- `docs/REFLECTION_2024_Chatbot_Goals_and_Architecture.md` - Why we chose this architecture
