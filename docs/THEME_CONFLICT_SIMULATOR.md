# Theme Conflict Simulator

## Overview

The theme conflict simulator replicates CSS conflicts from production themes (cosmobit/lazypress) in your local development environment. This allows you to test and fix CSS issues locally before deploying to production.

## How It Works

When enabled, the simulator CSS file (`theme-conflict-simulator.css`) is loaded **after** the main widget CSS, simulating the same CSS conflicts that occur in production:

- Image width collapsing to 0px
- Toggle button resizing from 64x64px to 56x40px
- Flex container conflicts
- Theme-specific image sizing rules

## Enabling the Simulator

The simulator is **automatically enabled** in local Docker development when:
- `WP_DEBUG` is `true` (already set in `wordpress-debug-config/wp-config-debug.php`)
- `LUNPETSHOP_SIMULATE_THEME_CONFLICTS` is `true` (already set in debug config)

### Manual Enable/Disable

To enable manually, add to your `wp-config.php`:

```php
define('LUNPETSHOP_SIMULATE_THEME_CONFLICTS', true);
```

To disable:

```php
define('LUNPETSHOP_SIMULATE_THEME_CONFLICTS', false);
```

Or simply remove the constant (it defaults to disabled).

## Testing Workflow

1. **Start local WordPress:**
   ```bash
   docker-compose up -d
   ```

2. **Visit local site:** http://localhost:8080

3. **Check browser DevTools:**
   - Open DevTools (F12)
   - Go to Network tab → Filter by CSS
   - Verify `theme-conflict-simulator.css` is loaded
   - Check Console for any errors

4. **Verify conflicts are active:**
   - Inspect the chat toggle button
   - Image width should be `0px` (simulating production issue)
   - Toggle button should be `56x40px` instead of `64x64px`

5. **Test your fixes:**
   - Make CSS changes in `chat-widget.css`
   - Refresh the page
   - Verify fixes work against the simulated conflicts

6. **Disable simulator to verify normal behavior:**
   ```php
   // In wp-config.php
   define('LUNPETSHOP_SIMULATE_THEME_CONFLICTS', false);
   ```
   - Refresh page
   - Widget should look perfect (no conflicts)

## Production Theme Details

The simulator is based on conflicts observed with:
- **Parent Theme:** cosmobit
- **Child Theme:** lazypress
- **WooCommerce:** Enabled

### Known Conflicts

1. **Button Image Width Collapse:**
   ```css
   button img {
       width: auto;
   }
   .chat-toggle img {
       width: 0px; /* Collapsed! */
   }
   ```

2. **Toggle Button Resizing:**
   ```css
   button[class*="toggle"] {
       width: auto !important;
       height: auto !important;
   }
   ```

3. **Flex Container Conflicts:**
   ```css
   *[class*="flex"] img {
       flex: 0 1 auto;
       min-width: 0;
   }
   ```

## Fixes Applied

The main widget CSS (`chat-widget.css`) includes fixes with `!important` flags:

```css
.lunpetshop-chat-widget .chat-toggle {
    width: 4rem !important;
    height: 4rem !important;
    min-width: 4rem !important;
    min-height: 4rem !important;
}

.lunpetshop-chat-widget .chat-toggle img {
    width: 100% !important;
    height: 100% !important;
    min-width: 44px !important;
    min-height: 44px !important;
    flex-shrink: 0;
}
```

## Troubleshooting

### Simulator not loading?

1. **Check wp-config.php:**
   ```bash
   docker-compose exec wordpress cat /var/www/html/wp-config.php | grep LUNPETSHOP
   ```

2. **Check browser console:**
   - Look for CSS file loading errors
   - Verify `theme-conflict-simulator.css` appears in Network tab

3. **Clear browser cache:**
   - Hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)

### Conflicts not appearing?

1. **Verify simulator CSS is loaded:**
   ```javascript
   // In browser console
   Array.from(document.styleSheets).find(s => s.href && s.href.includes('theme-conflict-simulator'))
   ```

2. **Check CSS specificity:**
   - Simulator CSS should load AFTER main widget CSS
   - Check Network tab load order

3. **Verify constants:**
   ```php
   // Add temporarily to wp-config.php
   error_log('WP_DEBUG: ' . (WP_DEBUG ? 'true' : 'false'));
   error_log('LUNPETSHOP_SIMULATE_THEME_CONFLICTS: ' . (defined('LUNPETSHOP_SIMULATE_THEME_CONFLICTS') && LUNPETSHOP_SIMULATE_THEME_CONFLICTS ? 'true' : 'false'));
   ```

## Files

- **Simulator CSS:** `wordpress-plugin/lunpetshop-chatbot/assets/css/theme-conflict-simulator.css`
- **Main Widget CSS:** `wordpress-plugin/lunpetshop-chatbot/assets/css/chat-widget.css`
- **Plugin PHP:** `wordpress-plugin/lunpetshop-chatbot/lunpetshop-chatbot.php` (lines 40-47)
- **Debug Config:** `wordpress-debug-config/wp-config-debug.php`

## Best Practices

1. **Always test with simulator enabled** before deploying to production
2. **Use `!important` sparingly** - only when necessary to override theme conflicts
3. **Test with simulator disabled** to ensure normal behavior still works
4. **Keep simulator CSS updated** as new production conflicts are discovered

