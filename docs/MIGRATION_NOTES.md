# 🔄 Migration Notes - Folder Reorganization

**Date**: November 2025  
**Status**: ✅ Complete

---

## What Changed?

### Before (Old Structure)
```
lunpetshop/
├── src/              # Backend code
├── static/           # Widget files (duplicated)
├── wp-content/       # WordPress plugin (duplicated widget files)
└── main.py           # Entry point
```

**Problems:**
- Widget files duplicated in `static/` and `wp-content/plugins/`
- UI differences between local dev and WordPress
- No single source of truth
- Manual syncing required

### After (New Structure)
```
lunpetshop/
├── backend/          # Python FastAPI backend
├── widget/           # ⭐ SINGLE SOURCE OF TRUTH for widget
├── wordpress-plugin/ # WordPress plugin (uses widget via symlinks)
└── static/           # ⚠️ DEPRECATED (kept for reference)
```

**Benefits:**
- ✅ Single source of truth for widget code
- ✅ Local dev matches WordPress exactly
- ✅ Edit once, works everywhere
- ✅ No sync issues

---

## What You Need to Do

### If You're Starting Fresh

Just follow the **DEVELOPER_GUIDE.md** - everything is already set up!

### If You Have Existing Code

1. **Backend code moved**: `src/` → `backend/src/`
2. **Entry point moved**: `main.py` → `backend/main.py`
3. **Widget files**: Now in `widget/assets/` (use WordPress version as source)
4. **Run scripts**: Updated to use new paths

### Updating Your Workflow

**Old way:**
```bash
python main.py  # From root
```

**New way:**
```bash
cd backend
python main.py
# Or use: ./run.sh (from root)
```

---

## File Mapping

| Old Location | New Location | Notes |
|-------------|--------------|-------|
| `src/` | `backend/src/` | Backend code |
| `main.py` | `backend/main.py` | Entry point |
| `requirements.txt` | `backend/requirements.txt` | Dependencies |
| `static/chat-widget.css` | `widget/assets/css/chat-widget.css` | ⭐ Edit here |
| `static/chat.js` | `widget/assets/js/chat-widget.js` | ⭐ Edit here |
| `wp-content/plugins/.../chat-widget.css` | `widget/assets/css/chat-widget.css` | Symlink |
| `wp-content/plugins/.../chat-widget.js` | `widget/assets/js/chat-widget.js` | Symlink |

---

## Breaking Changes

### None! 🎉

The reorganization is **backward compatible**:
- Old `static/` files still exist (but deprecated)
- Backend API still works the same
- WordPress plugin still works (now uses symlinks)

---

## Verification

To verify everything works:

```bash
# 1. Start backend
cd backend
python main.py

# 2. Open browser
# http://localhost:8000

# 3. Check widget appears and works

# 4. Verify symlinks
ls -la wordpress-plugin/lunpetshop-chatbot/assets/
# Should show symlinks to widget/assets/

# 5. Build plugin
./bin/build-plugin.sh
# Should create lunpetshop-chatbot.zip
```

---

## Questions?

See **DEVELOPER_GUIDE.md** for detailed documentation.

