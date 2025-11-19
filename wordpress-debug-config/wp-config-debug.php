<?php
// Debug configuration - will be appended to wp-config.php
// Enable WordPress debugging
define('WP_DEBUG', true);
define('WP_DEBUG_LOG', true);
define('WP_DEBUG_DISPLAY', false);
@ini_set('display_errors', 0);

// Enable theme conflict simulator to test CSS collisions locally (same as production)
define('LUNPETSHOP_SIMULATE_THEME_CONFLICTS', true);

