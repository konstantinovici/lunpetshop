# 👨‍💻 Developer Guide - LùnPetShop KittyCat Chatbot

**For developers and site owners reviewing the codebase**

---

## 📁 Project Structure

```
lunpetshop/
├── backend/                    # Python FastAPI backend (API server)
│   ├── src/
│   │   ├── api.py             # FastAPI routes & endpoints
│   │   ├── chatbot.py         # LangGraph chatbot implementation
│   │   └── knowledge_base.py  # Product/business data
│   ├── main.py                # Entry point (run from here)
│   ├── requirements.txt       # Python dependencies
│   └── test_chatbot.py        # Test suite
│
├── widget/                    # ⭐ SINGLE SOURCE OF TRUTH for widget UI
│   ├── assets/
│   │   ├── css/
│   │   │   └── chat-widget.css    # Widget styles (edit here!)
│   │   └── js/
│   │       └── chat-widget.js      # Widget JavaScript (edit here!)
│   ├── index.html             # Demo/test page
│   └── demo.css               # Demo page styles (not widget)
│
├── wordpress-plugin/           # WordPress plugin (uses widget files)
│   └── lunpetshop-chatbot/
│       ├── lunpetshop-chatbot.php  # WordPress plugin PHP
│       └── assets/                 # Symlinks to widget/assets/
│
├── bin/                        # Utility scripts
│   ├── build-plugin.sh        # Build WordPress plugin zip
│   ├── start.sh               # Start backend server
│   └── start-all.sh           # Start backend + tunnel
│
└── static/                     # ⚠️ DEPRECATED - Use widget/ instead
```

---

## 🎯 Key Principles

### 1. **Single Source of Truth**
- **Widget UI code lives in `widget/` directory**
- WordPress plugin uses **symlinks** to widget files
- Local dev demo uses the **same widget files**
- **Edit widget code in ONE place** → changes everywhere

### 2. **Separation of Concerns**
- **Backend** (`backend/`): Python FastAPI API server
- **Widget** (`widget/`): Frontend UI (CSS, JS, HTML)
- **WordPress Plugin** (`wordpress-plugin/`): WordPress integration layer

### 3. **Development Workflow**
1. Edit widget files in `widget/assets/`
2. Test locally with `python backend/main.py`
3. Widget automatically works in WordPress (via symlinks)
4. Build plugin zip with `./bin/build-plugin.sh`

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- [uv](https://github.com/astral-sh/uv) package manager
- xAI API Key (get from https://console.x.ai/)

### Setup

```bash
# 1. Create virtual environment
uv venv
source .venv/bin/activate  # Mac/Linux
# or
.venv\Scripts\activate      # Windows

# 2. Install dependencies
uv pip install -r backend/requirements.txt

# 3. Create .env file
cp .env.example .env
# Edit .env and add: XAI_API_KEY=your_key_here

# 4. Start backend server
cd backend
python main.py
# Or from root: ./run.sh
```

### Test Locally

1. Backend starts at `http://localhost:8000`
2. Open browser → see demo page with widget
3. Widget uses same code as WordPress version

---

## 📝 Making Changes

### Editing Widget UI

**To change widget appearance or behavior:**

1. **Edit CSS**: `widget/assets/css/chat-widget.css`
2. **Edit JavaScript**: `widget/assets/js/chat-widget.js`
3. **Test locally**: Refresh browser at `http://localhost:8000`
4. **WordPress automatically gets changes** (via symlinks)

**Example: Change button color**
```css
/* Edit widget/assets/css/chat-widget.css */
.lunpetshop-chat-widget .chat-toggle {
    background: #FF0000; /* Change from gold to red */
}
```

### Editing Backend Logic

**To change chatbot behavior:**

1. **Edit chatbot logic**: `backend/src/chatbot.py`
2. **Edit knowledge base**: `backend/src/knowledge_base.py`
3. **Edit API endpoints**: `backend/src/api.py`
4. **Restart server**: Changes auto-reload (uvicorn reload=True)

**Example: Add new product category**
```python
# Edit backend/src/knowledge_base.py
CAT_PRODUCTS = {
    # ... existing categories ...
    "new_category": {
        "name_vi": "Tên mới",
        "name_en": "New Category",
        "count": 10,
        "examples": [...]
    }
}
```

---

## 🔧 Building WordPress Plugin

### Automatic Build

```bash
./bin/build-plugin.sh
```

This creates `lunpetshop-chatbot.zip` ready to upload to WordPress.

### Manual Build

```bash
cd wordpress-plugin/lunpetshop-chatbot
zip -r ../../lunpetshop-chatbot.zip . \
    -x "*.git*" \
    -x "*.DS_Store"
```

**Note**: The build script copies widget files (replaces symlinks) so the zip contains actual files.

---

## 🏗️ Architecture Overview

### Backend (Python FastAPI)

```
Request Flow:
Browser/WordPress → FastAPI (backend/src/api.py)
                  → LangGraph (backend/src/chatbot.py)
                  → Knowledge Base (backend/src/knowledge_base.py)
                  → xAI API (Grok model)
                  → Response back to client
```

**Key Files:**
- `backend/src/api.py`: HTTP endpoints (`/api/chat`, `/api/greeting`)
- `backend/src/chatbot.py`: LangGraph state machine, AI logic
- `backend/src/knowledge_base.py`: Product data, business info

### Widget (Frontend)

```
Widget Structure:
widget/assets/css/chat-widget.css  → Styles (single source)
widget/assets/js/chat-widget.js    → JavaScript logic (single source)
widget/index.html                  → Demo page (for local testing)
```

**Key Features:**
- Bilingual (Vietnamese/English)
- Language auto-detection
- Markdown support in messages
- Error handling with debug mode
- Responsive design (mobile-friendly)

### WordPress Integration

```
WordPress Plugin:
wordpress-plugin/lunpetshop-chatbot/
├── lunpetshop-chatbot.php       → WordPress hooks, settings page
└── assets/                       → Symlinks to widget/assets/
    ├── css/chat-widget.css      → Points to widget/assets/css/
    └── js/chat-widget.js        → Points to widget/assets/js/
```

**How it works:**
1. WordPress plugin enqueues CSS/JS from `assets/`
2. Files are symlinked to `widget/assets/`
3. Edit widget files → WordPress gets changes automatically
4. Build zip → symlinks replaced with actual files

---

## 🧪 Testing

### Run Test Suite

```bash
cd backend
python test_chatbot.py
```

Tests all 5 core questions in both Vietnamese and English.

### Manual Testing

1. **Local**: `http://localhost:8000` → test widget UI
2. **WordPress**: Install plugin → test on actual site
3. **API**: `curl http://localhost:8000/api/chat` → test backend

---

## 🌐 Deployment

### Backend Deployment (Vietnam Hosting)

**Option 1: Same Server as WordPress**
```bash
# On server
cd /path/to/lunpetshop/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Use systemd or PM2 to keep running
# Configure nginx reverse proxy:
# location /api/ {
#     proxy_pass http://localhost:8000/api/;
# }
```

**Option 2: Separate Server**
```bash
# Deploy backend to separate server
# Update WordPress plugin settings:
# API Base URL: https://api.lunpetshop.com
```

### WordPress Plugin Deployment

1. Build plugin: `./bin/build-plugin.sh`
2. Upload `lunpetshop-chatbot.zip` to WordPress admin
3. Activate plugin
4. Configure API Base URL in Settings → KittyCat Chatbot

---

## 📚 File Reference

### Backend Files

| File | Purpose |
|------|---------|
| `backend/main.py` | Entry point, starts uvicorn server |
| `backend/src/api.py` | FastAPI routes, CORS, static file serving |
| `backend/src/chatbot.py` | LangGraph implementation, AI logic |
| `backend/src/knowledge_base.py` | Product data, business information |
| `backend/test_chatbot.py` | Automated tests |

### Widget Files

| File | Purpose |
|------|---------|
| `widget/assets/css/chat-widget.css` | **Widget styles** (edit here!) |
| `widget/assets/js/chat-widget.js` | **Widget JavaScript** (edit here!) |
| `widget/index.html` | Demo page for local testing |
| `widget/demo.css` | Demo page styles (not widget) |

### WordPress Files

| File | Purpose |
|------|---------|
| `wordpress-plugin/lunpetshop-chatbot/lunpetshop-chatbot.php` | WordPress plugin PHP |
| `wordpress-plugin/lunpetshop-chatbot/assets/` | Symlinks to widget files |

---

## 🐛 Troubleshooting

### Widget Not Appearing in WordPress

1. **Check plugin is activated**: WordPress Admin → Plugins
2. **Check API Base URL**: Settings → KittyCat Chatbot
3. **Check browser console**: F12 → Console tab → look for errors
4. **Check file permissions**: Ensure PHP can read plugin files

### Backend Not Responding

1. **Check server is running**: `curl http://localhost:8000/health`
2. **Check API key**: Ensure `.env` has `XAI_API_KEY`
3. **Check logs**: Look at terminal output or `logs/backend.log`
4. **Check port**: Ensure port 8000 is not in use

### Widget UI Different Between Local and WordPress

**This should NOT happen** if using the new structure!

If it does:
1. Check symlinks: `ls -la wordpress-plugin/lunpetshop-chatbot/assets/`
2. Ensure WordPress is using widget files (not old static/)
3. Clear WordPress cache
4. Hard refresh browser (Cmd+Shift+R)

---

## 🔄 Development Workflow

### Daily Workflow

```bash
# Morning: Start development
cd backend
python main.py

# Edit widget files
# widget/assets/css/chat-widget.css
# widget/assets/js/chat-widget.js

# Test in browser: http://localhost:8000
# Refresh to see changes

# When ready: Build plugin
./bin/build-plugin.sh

# Deploy to WordPress
# Upload lunpetshop-chatbot.zip
```

### Making Widget Changes

1. Edit `widget/assets/css/chat-widget.css` or `widget/assets/js/chat-widget.js`
2. Test locally: Refresh `http://localhost:8000`
3. Changes automatically available in WordPress (via symlinks)
4. Build plugin zip when ready to deploy

### Making Backend Changes

1. Edit files in `backend/src/`
2. Server auto-reloads (uvicorn reload=True)
3. Test API endpoints
4. Deploy backend to server

---

## 📖 Code Style

### Python (Backend)
- Follow PEP 8
- Use type hints where possible
- Docstrings for functions/classes

### JavaScript (Widget)
- ES6+ syntax
- Use `const`/`let`, avoid `var`
- Comment complex logic

### CSS (Widget)
- Use CSS variables (defined in `:root`)
- BEM-like naming: `.lunpetshop-chat-widget .component-name`
- Mobile-first responsive design

---

## 🔐 Security Notes

- **API Key**: Never commit `.env` file (already in `.gitignore`)
- **CORS**: Currently allows all origins (`*`) - restrict in production
- **Input Validation**: FastAPI validates request models
- **XSS Protection**: Markdown sanitized by `marked` library

---

## 📞 Support

For questions or issues:
1. Check this guide first
2. Review code comments
3. Check `logs/backend.log` for errors
4. Contact development team

---

## 🎯 Key Takeaways

1. **Widget code is in `widget/`** - edit there, not in `static/` or WordPress plugin
2. **Symlinks connect WordPress to widget files** - one source of truth
3. **Backend is separate** - Python FastAPI in `backend/`
4. **Test locally first** - `http://localhost:8000` shows exact WordPress widget
5. **Build plugin zip** - `./bin/build-plugin.sh` creates deployment package

---

**Happy Coding! 🐱**

*Last Updated: November 2025*

