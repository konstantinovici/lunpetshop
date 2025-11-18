# 🐾 LùnPetShop KittyCat Chatbot - Project Overview

**Reorganized Structure - November 2025**

---

## 🎯 Quick Start

```bash
# 1. Setup
uv venv
source .venv/bin/activate
uv pip install -r backend/requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env: XAI_API_KEY=your_key_here

# 3. Run
./run.sh
# Or: cd backend && python main.py

# 4. Open browser
# http://localhost:8000
```

---

## 📁 Project Structure

```
lunpetshop/
├── backend/              # Python FastAPI backend
│   ├── src/              # Backend source code
│   ├── main.py           # Entry point
│   └── requirements.txt  # Python dependencies
│
├── widget/               # ⭐ Widget UI (SINGLE SOURCE OF TRUTH)
│   ├── assets/
│   │   ├── css/          # Widget styles (edit here!)
│   │   └── js/           # Widget JavaScript (edit here!)
│   └── index.html        # Demo page
│
├── wordpress-plugin/      # WordPress plugin
│   └── lunpetshop-chatbot/
│       ├── lunpetshop-chatbot.php
│       └── assets/       # Symlinks to widget/assets/
│
└── bin/                  # Utility scripts
    └── build-plugin.sh   # Build WordPress plugin zip
```

---

## 🎨 Key Principle: Single Source of Truth

**Widget UI code lives in `widget/` directory**

- ✅ Edit widget CSS/JS in ONE place: `widget/assets/`
- ✅ WordPress plugin uses symlinks → automatic updates
- ✅ Local dev demo uses same files → exact match
- ✅ No sync issues, no duplicates

---

## 📚 Documentation

- **DEVELOPER_GUIDE.md** - Complete developer documentation
- **MIGRATION_NOTES.md** - What changed and why
- **QUICKSTART.md** - Quick start guide (legacy)
- **README.md** - Original README (legacy)

---

## 🚀 Common Tasks

### Edit Widget UI
```bash
# Edit widget files
widget/assets/css/chat-widget.css
widget/assets/js/chat-widget.js

# Test locally
# Refresh http://localhost:8000
```

### Build WordPress Plugin
```bash
./bin/build-plugin.sh
# Creates: lunpetshop-chatbot.zip
```

### Run Tests
```bash
cd backend
python test_chatbot.py
```

---

## 🔧 Architecture

```
┌─────────────┐
│  WordPress  │
│    Site     │
└──────┬──────┘
       │ HTTPS API calls
       ▼
┌─────────────┐
│   Backend   │  Python FastAPI
│  (backend/) │  Port 8000
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    xAI      │  Grok API
│     API     │
└─────────────┘

Widget UI (widget/) → Embedded in WordPress & Local Demo
```

---

## 📖 For Developers

See **DEVELOPER_GUIDE.md** for:
- Detailed architecture
- Development workflow
- File reference
- Troubleshooting
- Code style guide

---

## 🌐 Deployment

### Backend (Vietnam Hosting)
- Deploy `backend/` directory
- Run with Python 3.9+
- Configure API Base URL in WordPress plugin settings

### WordPress Plugin
- Build: `./bin/build-plugin.sh`
- Upload `lunpetshop-chatbot.zip` to WordPress
- Configure API Base URL

---

## ✅ Status

- ✅ Folder reorganization complete
- ✅ Single source of truth established
- ✅ Symlinks configured
- ✅ Build scripts ready
- ✅ Documentation updated

---

**Built with ❤️ for LùnPetShop** 🐱🐕🐾

