# 🛠️ Local WordPress Development Guide

**Problem**: Installing the plugin zip file every time you make a change is tedious and slow.

**Solution**: Use WordPress plugin symlinks or direct file editing for faster iteration.

---

## 🎯 Quick Setup (Recommended)

### Option 1: Direct File Editing (Easiest)

If your WordPress site is on the same machine or accessible via network:

1. **Locate your WordPress plugins directory**:
   ```bash
   # Usually something like:
   /path/to/wordpress/wp-content/plugins/
   ```

2. **Create a symlink** (if on same machine):
   ```bash
   cd /path/to/wordpress/wp-content/plugins/
   ln -s /Users/konstantinovichi/0x8/0x81/lunpetshop/wp-content/plugins/lunpetshop-chatbot lunpetshop-chatbot
   ```

3. **Or copy the plugin directory**:
   ```bash
   cp -r /Users/konstantinovichi/0x8/0x81/lunpetshop/wp-content/plugins/lunpetshop-chatbot /path/to/wordpress/wp-content/plugins/
   ```

4. **Activate once** in WordPress admin, then:
   - Edit files directly in your project directory
   - Changes reflect immediately (just refresh browser)
   - No need to re-upload zip!

---

## 🚀 Development Workflow

### Daily Development Cycle

1. **Start your backend**:
   ```bash
   # Terminal 1: FastAPI backend
   cd /Users/konstantinovichi/0x8/0x81/lunpetshop
   python main.py
   ```

2. **Start tunnel** (if needed):
   ```bash
   # Terminal 2: Public tunnel
   lt --port 8000 --subdomain lunpetshop-chatbot
   ```

3. **Make changes** to plugin files:
   - Edit `wp-content/plugins/lunpetshop-chatbot/assets/js/chat-widget.js`
   - Edit `wp-content/plugins/lunpetshop-chatbot/assets/css/chat-widget.css`
   - Edit `wp-content/plugins/lunpetshop-chatbot/lunpetshop-chatbot.php`

4. **Test immediately**:
   - Hard refresh browser (Cmd+Shift+R / Ctrl+Shift+R)
   - Check console for changes
   - No plugin reinstall needed!

5. **When done**, create zip for production:
   ```bash
   cd wp-content/plugins
   zip -r ../../lunpetshop-chatbot.zip lunpetshop-chatbot
   ```

---

## 🔧 Advanced: Using Git for WordPress

If your WordPress site is in a git repo or you can access it:

### Setup Git Submodule (Best for Teams)

```bash
# In WordPress root
cd wp-content/plugins
git submodule add <your-repo-url>/lunpetshop.git lunpetshop-chatbot
```

### Or Use Git Worktree

```bash
# In your project
git worktree add ../wordpress-plugins/lunpetshop-chatbot
# Then symlink or copy to WordPress
```

---

## 🌐 Remote WordPress Development

If WordPress is on a remote server:

### Option 1: SFTP/SCP Sync Script

Create `sync-plugin.sh`:
```bash
#!/bin/bash
# Sync plugin to remote WordPress
REMOTE_HOST="your-server.com"
REMOTE_PATH="/var/www/html/wp-content/plugins"
LOCAL_PATH="wp-content/plugins/lunpetshop-chatbot"

rsync -avz --exclude '.git' \
  $LOCAL_PATH/ \
  $REMOTE_HOST:$REMOTE_PATH/lunpetshop-chatbot/
```

Then run: `./sync-plugin.sh` after each change.

### Option 2: VS Code Remote SSH

1. Install "Remote - SSH" extension
2. Connect to your WordPress server
3. Edit files directly on remote
4. Changes reflect immediately

---

## 📝 File Watching & Auto-Sync

### Using `watch` command (Mac/Linux)

```bash
# Watch for changes and sync automatically
watch -n 2 'rsync -avz --exclude ".git" wp-content/plugins/lunpetshop-chatbot/ user@server:/path/to/wp-content/plugins/lunpetshop-chatbot/'
```

### Using `nodemon` or similar

Create `watch-plugin.js`:
```javascript
const { exec } = require('child_process');
const chokidar = require('chokidar');

chokidar.watch('wp-content/plugins/lunpetshop-chatbot/**/*').on('change', () => {
  exec('./sync-plugin.sh', (err) => {
    if (err) console.error(err);
    else console.log('✅ Plugin synced!');
  });
});
```

---

## 🎨 CSS/JS Cache Busting

WordPress caches assets by version. To force reload during development:

### Method 1: Change Version in PHP
```php
// In lunpetshop-chatbot.php
private const VERSION = '0.1.2-dev'; // Add -dev suffix
```

### Method 2: Use Query String
```php
wp_enqueue_script(
    'lunpetshop-chatbot',
    $plugin_url . 'assets/js/chat-widget.js',
    [],
    self::VERSION . '-' . time() // Forces reload every time
);
```

### Method 3: Browser DevTools
- Open DevTools → Network tab
- Check "Disable cache" checkbox
- Keep DevTools open while developing

---

## 🐛 Debugging Tips

### 1. Check if WordPress is Loading Your Files

Add this to your PHP file temporarily:
```php
public function enqueue_assets(): void {
    error_log('KittyCat Chatbot: Loading assets, version ' . self::VERSION);
    // ... rest of code
}
```

Check WordPress debug log: `wp-content/debug.log`

### 2. Verify Config is Passed to JavaScript

In browser console:
```javascript
console.log(window.KittyCatChatbotConfig);
// Should show: {apiBaseUrl: "...", initialLanguage: "vi"}
```

### 3. Check Network Requests

- Open DevTools → Network tab
- Filter by "api" or "chat"
- Verify requests go to correct URL
- Check response status codes

### 4. WordPress Debug Mode

Add to `wp-config.php`:
```php
define('WP_DEBUG', true);
define('WP_DEBUG_LOG', true);
define('SCRIPT_DEBUG', true); // Loads unminified scripts
```

---

## 📦 Creating Production Zip

When ready to deploy:

```bash
cd /Users/konstantinovichi/0x8/0x81/lunpetshop/wp-content/plugins
zip -r ../../lunpetshop-chatbot.zip lunpetshop-chatbot \
  -x "*.git*" \
  -x "*.DS_Store" \
  -x "*__pycache__*" \
  -x "*.pyc"
```

---

## ✅ Recommended Setup

**For fastest iteration**:

1. ✅ Use symlink or direct copy (if local WordPress)
2. ✅ Enable WordPress debug mode
3. ✅ Use browser DevTools with cache disabled
4. ✅ Keep backend running in separate terminal
5. ✅ Use version bumping for cache busting when needed

**Example daily workflow**:
```bash
# Morning: Start everything
./start-backend.sh  # Starts FastAPI + tunnel

# During day: Edit files, refresh browser
# No plugin reinstall needed!

# Evening: Commit changes
git add .
git commit -m "feat: add new feature"
```

---

## 🚨 Common Issues

### Issue: Changes not showing up

**Solutions**:
- Hard refresh browser (Cmd+Shift+R)
- Clear WordPress cache (if using caching plugin)
- Check file permissions
- Verify you're editing the right file

### Issue: JavaScript errors after changes

**Solutions**:
- Check browser console for syntax errors
- Verify file was saved correctly
- Check WordPress debug log
- Try incrementing version number

### Issue: Backend connection fails

**Solutions**:
- Verify backend is running (`curl http://localhost:8000/health`)
- Check tunnel is active
- Verify API base URL in WordPress settings
- Check CORS configuration in backend

---

## 📚 Additional Resources

- [WordPress Plugin Development Handbook](https://developer.wordpress.org/plugins/)
- [WordPress Debugging](https://wordpress.org/support/article/debugging-in-wordpress/)
- [FastAPI CORS Configuration](https://fastapi.tiangolo.com/tutorial/cors/)

---

**Happy Developing! 🐱**

*Last Updated: November 14, 2025*

