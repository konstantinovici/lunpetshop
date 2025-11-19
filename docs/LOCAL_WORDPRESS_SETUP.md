# Local WordPress Development Setup

This guide helps you set up a local WordPress environment to test the KittyCat chatbot plugin without uploading to production.

## Quick Setup Options

### Option 1: Local by Flywheel (Recommended - Easiest) 🚀

**Best for:** macOS users who want zero-config setup

1. **Download Local by Flywheel:**
   ```bash
   # Visit: https://localwp.com/
   # Or install via Homebrew:
   brew install --cask local
   ```

2. **Create a new site:**
   - Open Local
   - Click "Create a new site"
   - Name it: `lunpetshop-local`
   - Choose PHP 8.1+ and MySQL
   - Set admin email/password

3. **Install the plugin:**
   ```bash
   # Navigate to your plugin directory
   cd /Users/konstantinovichi/0x8/0x81/lunpetshop/wordpress-plugin
   
   # Copy plugin to WordPress plugins directory
   # Local sites are usually in: ~/Local Sites/lunpetshop-local/app/public/wp-content/plugins/
   cp -r lunpetshop-chatbot ~/Local\ Sites/lunpetshop-local/app/public/wp-content/plugins/
   ```

4. **Activate plugin:**
   - Go to WordPress admin: `http://lunpetshop-local.local/wp-admin`
   - Plugins → Activate "LùnPetShop KittyCat Chatbot"
   - Settings → KittyCat Chatbot → Set API Base URL

5. **Enable debugging:**
   - Local → Open Site Shell
   - Edit `wp-config.php`:
   ```php
   define('WP_DEBUG', true);
   define('WP_DEBUG_LOG', true);
   define('WP_DEBUG_DISPLAY', false);
   ```
   - Check logs: `~/Local Sites/lunpetshop-local/logs/php/error.log`

---

### Option 2: Docker Compose (Fast & Portable) 🐳

**Best for:** Cross-platform, consistent environments

1. **Create `docker-compose.yml` in project root:**
   ```yaml
   version: '3.8'
   
   services:
     wordpress:
       image: wordpress:latest
       ports:
         - "8080:80"
       environment:
         WORDPRESS_DB_HOST: db
         WORDPRESS_DB_USER: wordpress
         WORDPRESS_DB_PASSWORD: wordpress
         WORDPRESS_DB_NAME: wordpress
       volumes:
         - wordpress_data:/var/www/html
         - ./wordpress-plugin/lunpetshop-chatbot:/var/www/html/wp-content/plugins/lunpetshop-chatbot
       depends_on:
         - db
   
     db:
       image: mysql:8.0
       environment:
         MYSQL_DATABASE: wordpress
         MYSQL_USER: wordpress
         MYSQL_PASSWORD: wordpress
         MYSQL_ROOT_PASSWORD: rootpassword
       volumes:
         - db_data:/var/lib/mysql
   
   volumes:
     wordpress_data:
     db_data:
   ```

2. **Start WordPress:**
   ```bash
   docker-compose up -d
   ```

3. **Access WordPress:**
   - Frontend: http://localhost:8080
   - Admin: http://localhost:8080/wp-admin
   - Default credentials: admin / (set during first install)

4. **Enable debugging:**
   ```bash
   # Edit wp-config.php in container
   docker-compose exec wordpress bash
   # Then edit wp-config.php to add debug constants
   ```

---

### Option 3: MAMP/XAMPP (Traditional) 🖥️

**Best for:** Users familiar with traditional LAMP stacks

1. **Install MAMP (macOS) or XAMPP:**
   ```bash
   # MAMP
   brew install --cask mamp
   
   # Or download from: https://www.mamp.info/
   ```

2. **Download WordPress:**
   ```bash
   cd ~/Sites  # or wherever MAMP serves from
   curl -O https://wordpress.org/latest.tar.gz
   tar -xzf latest.tar.gz
   mv wordpress lunpetshop-local
   ```

3. **Create database:**
   - Open MAMP → Start Servers
   - Go to phpMyAdmin: http://localhost:8888/phpMyAdmin
   - Create database: `lunpetshop_local`

4. **Install WordPress:**
   - Visit: http://localhost:8888/lunpetshop-local
   - Follow WordPress installer
   - Database: `lunpetshop_local`, user: `root`, password: `root`

5. **Install plugin:**
   ```bash
   cp -r wordpress-plugin/lunpetshop-chatbot ~/Sites/lunpetshop-local/wp-content/plugins/
   ```

---

## Debugging Setup

### Enable WordPress Debug Logging

Add to `wp-config.php` (before "That's all, stop editing!"):

```php
// Enable WordPress debugging
define('WP_DEBUG', true);
define('WP_DEBUG_LOG', true);
define('WP_DEBUG_DISPLAY', false);
@ini_set('display_errors', 0);
```

### Check Logs

**Local by Flywheel:**
```bash
tail -f ~/Local\ Sites/lunpetshop-local/logs/php/error.log
```

**Docker:**
```bash
docker-compose logs -f wordpress
```

**MAMP/XAMPP:**
```bash
tail -f ~/Sites/lunpetshop-local/wp-content/debug.log
```

### Browser Console

Open browser DevTools (F12) → Console tab to see:
- Image loading errors (from `onerror` handlers we added)
- JavaScript errors
- Network requests

---

## Quick Test Checklist

After setup, verify:

- [ ] Plugin appears in WordPress admin → Plugins
- [ ] Plugin activates without errors
- [ ] Settings page loads: Settings → KittyCat Chatbot
- [ ] Widget appears on frontend (bottom-right corner)
- [ ] KittyCat logo loads (check browser console for errors)
- [ ] Send button SVG renders correctly
- [ ] Chat functionality works with backend API

---

## Troubleshooting

### Images not loading?

1. **Check file permissions:**
   ```bash
   ls -la wordpress-plugin/lunpetshop-chatbot/assets/KittyCatLogo.png
   chmod 644 wordpress-plugin/lunpetshop-chatbot/assets/KittyCatLogo.png
   ```

2. **Check URL in browser:**
   - Right-click broken image → Inspect
   - Check the `src` attribute
   - Try opening URL directly in browser

3. **Check WordPress debug log:**
   - Look for `[KittyCat Chatbot]` entries
   - Compare `plugins_url()` vs `plugin_dir_url()` URLs

### Plugin not appearing?

1. **Check plugin directory:**
   ```bash
   ls -la wp-content/plugins/lunpetshop-chatbot/
   ```

2. **Check plugin header:**
   - Ensure `lunpetshop-chatbot.php` has correct header
   - Check for PHP syntax errors

### CSS/JS not loading?

1. **Clear WordPress cache:**
   - Deactivate/reactivate plugin
   - Clear browser cache (Cmd+Shift+R)

2. **Check enqueue in browser:**
   - View page source
   - Search for `chat-widget.css` and `chat-widget.js`
   - Verify URLs are correct

---

## Recommended Workflow

1. **Make changes locally** → Test in Local/Docker
2. **Verify everything works** → Check console & logs
3. **Build plugin zip** → Use `bin/build-plugin.sh`
4. **Upload to production** → Only when confident

This saves you from the upload → test → debug → re-upload cycle! 🎉

