<?php
/**
 * Plugin Name: LùnPetShop KittyCat Chatbot
 * Description: Adds the KittyCat AI chatbot widget to the public-facing site.
 * Version: 0.4.2
 * Author: LùnPetShop
 */

if (!defined('ABSPATH')) {
    exit;
}

final class LunPetshop_KittyCat_Chatbot {
    private const VERSION = '0.4.2';
    private const OPTION_API_BASE = 'lunpetshop_chatbot_api_base';
    private const OPTION_LANGUAGE = 'lunpetshop_chatbot_initial_language';

    public function __construct() {
        add_action('wp_enqueue_scripts', [$this, 'enqueue_assets']);
        add_action('wp_footer', [$this, 'render_widget'], 20);
        add_action('admin_menu', [$this, 'register_settings_page']);
        add_action('admin_init', [$this, 'register_settings']);
    }

    public function enqueue_assets(): void {
        if (is_admin()) {
            return;
        }

        $plugin_url = plugin_dir_url(__FILE__);

        wp_enqueue_style(
            'lunpetshop-chatbot',
            $plugin_url . 'assets/css/chat-widget.css',
            [],
            self::VERSION
        );

        wp_enqueue_script(
            'lunpetshop-chatbot-marked',
            'https://cdn.jsdelivr.net/npm/marked@12.0.0/marked.min.js',
            [],
            '12.0.0',
            true
        );

        wp_enqueue_script(
            'lunpetshop-chatbot',
            $plugin_url . 'assets/js/chat-widget.js',
            ['lunpetshop-chatbot-marked'],
            self::VERSION,
            true
        );

        $config = [
            'apiBaseUrl' => $this->get_api_base_url(),
            'initialLanguage' => $this->get_initial_language(),
        ];

        wp_add_inline_script(
            'lunpetshop-chatbot',
            'window.KittyCatChatbotConfig = ' . wp_json_encode($config) . ';',
            'before'
        );
    }

    public function render_widget(): void {
        if (is_admin()) {
            return;
        }

        // Use plugins_url() for better WordPress compatibility
        $logo_url = plugins_url('assets/KittyCatLogo.png', __FILE__);
        $plugin_url = plugin_dir_url(__FILE__);
        
        // Debug logging (check WordPress debug.log or enable WP_DEBUG_LOG)
        if (defined('WP_DEBUG') && WP_DEBUG) {
            error_log('[KittyCat Chatbot] Plugin URL: ' . $plugin_url);
            error_log('[KittyCat Chatbot] Logo URL (plugins_url): ' . $logo_url);
            error_log('[KittyCat Chatbot] Logo URL (plugin_dir_url): ' . $plugin_url . 'assets/KittyCatLogo.png');
        }
        $style_url = $plugin_url . 'assets/css/chat-widget.css';
        ?>
        <div
            id="chat-widget"
            class="lunpetshop-chat-widget chat-widget"
            data-style-url="<?php echo esc_url($style_url); ?>"
        >
            <button id="chat-toggle" class="chat-toggle" aria-label="<?php esc_attr_e('Toggle chat', 'lunpetshop-chatbot'); ?>">
                <img src="<?php echo esc_url($logo_url); ?>" alt="KittyCat Logo" onerror="console.error('Failed to load KittyCat logo from: <?php echo esc_js($logo_url); ?>');">
                <span class="close-icon">✕</span>
            </button>

            <div id="chat-window" class="chat-window" role="dialog" aria-live="polite" aria-label="<?php esc_attr_e('KittyCat chatbot window', 'lunpetshop-chatbot'); ?>">
                <div class="chat-header">
                    <div class="chat-header-content">
                        <div class="avatar">
                            <img src="<?php echo esc_url($logo_url); ?>" alt="KittyCat Avatar" onerror="console.error('Failed to load KittyCat avatar from: <?php echo esc_js($logo_url); ?>');">
                        </div>
                        <div class="header-text">
                            <h3><?php esc_html_e('KittyCat', 'lunpetshop-chatbot'); ?></h3>
                            <p><?php esc_html_e('AI Assistant', 'lunpetshop-chatbot'); ?></p>
                        </div>
                    </div>
                    <div class="header-actions">
                        <button id="language-toggle" class="language-btn" title="<?php esc_attr_e('Switch language', 'lunpetshop-chatbot'); ?>">
                            <span id="current-lang">VI</span>
                        </button>
                        <button id="close-chat" class="close-btn" aria-label="<?php esc_attr_e('Close chat', 'lunpetshop-chatbot'); ?>">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="M6 6 18 18"/></svg>
                        </button>
                    </div>
                </div>

                <div id="chat-messages" class="chat-messages custom-scrollbar"></div>

                <div id="quick-actions" class="quick-actions">
                    <button class="quick-action-btn" data-action="cat">
                        <span>🐱</span> <?php esc_html_e('Products for my cat', 'lunpetshop-chatbot'); ?>
                    </button>
                    <button class="quick-action-btn" data-action="dog">
                        <span>🐕</span> <?php esc_html_e('Products for my dog', 'lunpetshop-chatbot'); ?>
                    </button>
                    <button class="quick-action-btn" data-action="business">
                        <span>ℹ️</span> <?php esc_html_e('About the business', 'lunpetshop-chatbot'); ?>
                    </button>
                    <button class="quick-action-btn" data-action="contact">
                        <span>📞</span> <?php esc_html_e('Contact info', 'lunpetshop-chatbot'); ?>
                    </button>
                </div>

                <div class="chat-input-container">
                    <input
                        type="text"
                        id="chat-input"
                        class="chat-input"
                        placeholder="<?php esc_attr_e('Type your message...', 'lunpetshop-chatbot'); ?>"
                        autocomplete="off"
                    />
                    <button id="send-button" class="send-button" aria-label="<?php esc_attr_e('Send message', 'lunpetshop-chatbot'); ?>">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>
                    </button>
                </div>
            </div>
        </div>
        <?php
    }

    public function register_settings_page(): void {
        add_options_page(
            __('KittyCat Chatbot', 'lunpetshop-chatbot'),
            __('KittyCat Chatbot', 'lunpetshop-chatbot'),
            'manage_options',
            'lunpetshop-chatbot',
            [$this, 'render_settings_page']
        );
    }

    public function register_settings(): void {
        register_setting(
            'lunpetshop_chatbot',
            self::OPTION_API_BASE,
            [
                'type' => 'string',
                'sanitize_callback' => [$this, 'sanitize_api_base'],
                'default' => '',
            ]
        );

        register_setting(
            'lunpetshop_chatbot',
            self::OPTION_LANGUAGE,
            [
                'type' => 'string',
                'sanitize_callback' => [$this, 'sanitize_language'],
                'default' => 'vi',
            ]
        );
    }

    public function render_settings_page(): void {
        if (!current_user_can('manage_options')) {
            return;
        }

        $api_base = get_option(self::OPTION_API_BASE, '');
        $language = $this->get_language_option();
        ?>
        <div class="wrap">
            <h1><?php esc_html_e('KittyCat Chatbot Settings', 'lunpetshop-chatbot'); ?></h1>
            <form method="post" action="options.php">
                <?php settings_fields('lunpetshop_chatbot'); ?>
                <table class="form-table" role="presentation">
                    <tr>
                        <th scope="row">
                            <label for="lunpetshop-chatbot-api-base"><?php esc_html_e('API Base URL', 'lunpetshop-chatbot'); ?></label>
                        </th>
                        <td>
                            <input
                                type="url"
                                id="lunpetshop-chatbot-api-base"
                                name="<?php echo esc_attr(self::OPTION_API_BASE); ?>"
                                value="<?php echo esc_attr($api_base); ?>"
                                class="regular-text"
                                placeholder="https://lunpetshop-chatbot.loca.lt"
                            />
                            <p class="description">
                                <?php esc_html_e('Public HTTPS URL where the FastAPI backend is reachable. Leave empty to use relative /api requests.', 'lunpetshop-chatbot'); ?>
                            </p>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row">
                            <label for="lunpetshop-chatbot-language"><?php esc_html_e('Default Language', 'lunpetshop-chatbot'); ?></label>
                        </th>
                        <td>
                            <select id="lunpetshop-chatbot-language" name="<?php echo esc_attr(self::OPTION_LANGUAGE); ?>">
                                <option value="vi" <?php selected($language, 'vi'); ?>><?php esc_html_e('Vietnamese', 'lunpetshop-chatbot'); ?></option>
                                <option value="en" <?php selected($language, 'en'); ?>><?php esc_html_e('English', 'lunpetshop-chatbot'); ?></option>
                            </select>
                            <p class="description">
                                <?php esc_html_e('Initial UI language for the widget. Visitors can still switch languages from the widget.', 'lunpetshop-chatbot'); ?>
                            </p>
                        </td>
                    </tr>
                </table>
                <?php submit_button(); ?>
            </form>
        </div>
        <?php
    }

    private function get_api_base_url(): string {
        $value = get_option(self::OPTION_API_BASE, '');

        if (!$value && defined('LUNPETSHOP_CHATBOT_API_BASE')) {
            $value = (string) LUNPETSHOP_CHATBOT_API_BASE;
        }

        $value = $this->sanitize_api_base($value);

        /** @var string $filtered */
        $filtered = apply_filters('lunpetshop_chatbot_api_base_url', $value);

        return $filtered;
    }

    private function get_initial_language(): string {
        $value = get_option(self::OPTION_LANGUAGE, 'vi');

        if (!$value && defined('LUNPETSHOP_CHATBOT_INITIAL_LANGUAGE')) {
            $value = (string) LUNPETSHOP_CHATBOT_INITIAL_LANGUAGE;
        }

        $value = $this->sanitize_language($value);

        /** @var string $filtered */
        $filtered = apply_filters('lunpetshop_chatbot_initial_language', $value);

        return $filtered;
    }

    private function get_language_option(): string {
        $value = get_option(self::OPTION_LANGUAGE, 'vi');
        return $this->sanitize_language($value);
    }

    public function sanitize_api_base($value): string {
        $value = is_scalar($value) ? (string) $value : '';
        $value = trim($value);

        if ($value === '') {
            return '';
        }

        return esc_url_raw($value);
    }

    public function sanitize_language($value): string {
        $value = is_scalar($value) ? strtolower((string) $value) : '';
        return in_array($value, ['vi', 'en'], true) ? $value : 'vi';
    }
}

new LunPetshop_KittyCat_Chatbot();

