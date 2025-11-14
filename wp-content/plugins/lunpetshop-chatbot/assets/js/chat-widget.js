// Chat Widget JavaScript

class ChatWidget {
    constructor(options = {}) {
        // Merge with global config from WordPress plugin if available
        const globalConfig = window.KittyCatChatbotConfig || {};
        const mergedOptions = { ...globalConfig, ...options };
        
        this.config = {
            apiBaseUrl: mergedOptions.apiBaseUrl || '',
            initialLanguage: mergedOptions.initialLanguage || 'vi'
        };

        this.isOpen = false;
        this.threadId = null;
        this.language = this.config.initialLanguage;
        this.conversationStarted = false;
        this.apiBaseUrl = this.normalizeBaseUrl(this.config.apiBaseUrl);
        
        // Debug log to verify config is loaded
        console.log('🐱 KittyCat Chatbot initialized:', {
            apiBaseUrl: this.apiBaseUrl,
            initialLanguage: this.language,
            configSource: window.KittyCatChatbotConfig ? 'WordPress config' : 'default',
            rawConfig: window.KittyCatChatbotConfig
        });
        
        this.initElements();
        this.attachEventListeners();
        this.updateInputPlaceholder();
        this.updateLanguageDisplay();
        this.loadGreeting();
    }

    normalizeBaseUrl(baseUrl) {
        if (!baseUrl) return '';
        try {
            const trimmed = baseUrl.trim();
            if (!trimmed) return '';
            const withoutTrailingSlash = trimmed.endsWith('/')
                ? trimmed.slice(0, -1)
                : trimmed;
            return withoutTrailingSlash;
        } catch (error) {
            console.warn('Invalid apiBaseUrl provided to ChatWidget:', error);
            return '';
        }
    }

    buildApiUrl(path) {
        const cleanPath = path.startsWith('/') ? path : `/${path}`;
        if (!this.apiBaseUrl) {
            console.warn('⚠️ No API base URL configured. Using relative path:', cleanPath);
            return cleanPath;
        }
        const fullUrl = `${this.apiBaseUrl}${cleanPath}`;
        console.log('🔗 Building API URL:', { path, apiBaseUrl: this.apiBaseUrl, fullUrl });
        return fullUrl;
    }

    initElements() {
        this.widget = document.getElementById('chat-widget');
        this.toggleBtn = document.getElementById('chat-toggle');
        this.closeBtn = document.getElementById('close-chat');
        this.messagesContainer = document.getElementById('chat-messages');
        this.inputField = document.getElementById('chat-input');
        this.sendBtn = document.getElementById('send-button');
        this.quickActions = document.getElementById('quick-actions');
        this.languageBtn = document.getElementById('language-toggle');
        this.currentLangSpan = document.getElementById('current-lang');
    }

    attachEventListeners() {
        // Toggle chat window
        this.toggleBtn.addEventListener('click', () => this.toggleChat());
        this.closeBtn.addEventListener('click', () => this.toggleChat());

        // Send message
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.inputField.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Quick actions
        const quickActionBtns = document.querySelectorAll('.quick-action-btn');
        quickActionBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const action = btn.dataset.action;
                this.handleQuickAction(action);
            });
        });

        // Language toggle
        this.languageBtn.addEventListener('click', () => this.toggleLanguage());
    }

    toggleChat() {
        this.isOpen = !this.isOpen;
        this.widget.classList.toggle('open', this.isOpen);

        if (this.isOpen && !this.conversationStarted) {
            // Focus input when opening
            setTimeout(() => this.inputField.focus(), 100);
        }
    }

    async loadGreeting() {
        try {
            const response = await fetch(this.buildApiUrl('/api/greeting'), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'bypass-tunnel-reminder': '1',
                },
                body: JSON.stringify({
                    language: this.language
                })
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error('❌ Greeting API Error:', {
                    status: response.status,
                    statusText: response.statusText,
                    body: errorText,
                    url: this.buildApiUrl('/api/greeting')
                });
                throw new Error(`Failed to load greeting: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();
            this.threadId = data.thread_id;
            this.addMessage('assistant', data.greeting);
        } catch (error) {
            console.error('❌ Error loading greeting:', {
                message: error.message,
                stack: error.stack,
                apiUrl: this.buildApiUrl('/api/greeting'),
                language: this.language
            });
            this.addMessage('assistant', this.getDefaultGreeting());
        }
    }

    getDefaultGreeting() {
        if (this.language === 'vi') {
            return `Xin chào! 🐱 Mình là KittyCat, trợ lý AI của LùnPetShop. 

Mình có thể giúp bạn:
• Tìm sản phẩm cho mèo 🐱
• Tìm sản phẩm cho chó 🐕
• Thông tin về cửa hàng 🏪
• Thông tin liên hệ 📞

Bạn cần mình hỗ trợ gì nào? 🐾`;
        } else {
            return `Hello! 🐱 I'm KittyCat, your personal AI assistant for LùnPetShop. 

I can help you with:
• Cat products 🐱
• Dog products 🐕
• Store information 🏪
• Contact information 📞

How can I help you today? 🐾`;
        }
    }

    handleQuickAction(action) {
        const messages = {
            vi: {
                cat: 'Bạn có sản phẩm gì cho mèo của tôi?',
                dog: 'Bạn có sản phẩm gì cho chó của tôi?',
                business: 'Cho tôi biết về cửa hàng của bạn?',
                contact: 'Làm thế nào để liên hệ với bạn?'
            },
            en: {
                cat: 'What products do you have for my cat?',
                dog: 'What products do you have for my dog?',
                business: 'Tell me about your business?',
                contact: 'How can I contact you?'
            }
        };

        const message = messages[this.language][action];
        this.inputField.value = message;
        this.sendMessage();
    }

    async sendMessage() {
        const message = this.inputField.value.trim();
        if (!message) return;

        // Clear input and disable send button
        this.inputField.value = '';
        this.sendBtn.disabled = true;

        // Hide quick actions after first message
        if (!this.conversationStarted) {
            this.conversationStarted = true;
            this.quickActions.classList.add('hidden');
        }

        // Add user message to chat
        this.addMessage('user', message);

        // Show typing indicator
        const typingId = this.showTypingIndicator();

        try {
            const response = await fetch(this.buildApiUrl('/api/chat'), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'bypass-tunnel-reminder': '1',
                },
                body: JSON.stringify({
                    message: message,
                    thread_id: this.threadId,
                    language: this.language
                })
            });

            if (!response.ok) {
                let errorBody = '';
                try {
                    errorBody = await response.text();
                    const errorJson = JSON.parse(errorBody);
                    console.error('❌ API Error Response:', {
                        status: response.status,
                        statusText: response.statusText,
                        detail: errorJson.detail || errorJson,
                        url: this.buildApiUrl('/api/chat')
                    });
                } catch (e) {
                    console.error('❌ API Error (non-JSON):', {
                        status: response.status,
                        statusText: response.statusText,
                        body: errorBody,
                        url: this.buildApiUrl('/api/chat')
                    });
                }
                throw new Error(`API Error ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            // Update thread_id if it's a new conversation
            if (!this.threadId) {
                this.threadId = data.thread_id;
            }

            // Update language if detected differently
            if (data.language !== this.language) {
                this.language = data.language;
                this.updateLanguageDisplay();
            }

            // Remove typing indicator and add response
            this.removeTypingIndicator(typingId);
            this.addMessage('assistant', data.response);

        } catch (error) {
            // Enhanced error logging for observability
            const errorDetails = {
                message: error.message,
                stack: error.stack,
                timestamp: new Date().toISOString(),
                apiUrl: this.buildApiUrl('/api/chat'),
                userMessage: message,
                threadId: this.threadId,
                language: this.language
            };
            
            console.error('❌ Chat Widget Error:', errorDetails);
            console.error('Full error object:', error);
            
            // Try to get more details from response if available
            if (error.response) {
                console.error('Response status:', error.response.status);
                console.error('Response body:', error.response.body);
            }
            
            this.removeTypingIndicator(typingId);
            
            // Show detailed error message (can be expanded for debugging)
            const errorMessage = this.getErrorMessage(error);
            this.addMessage('assistant', errorMessage, { isError: true, errorDetails });
        } finally {
            this.sendBtn.disabled = false;
            this.inputField.focus();
        }
    }

    getErrorMessage(error = null) {
        // Check if we're in development mode (can be enabled via config)
        const isDevMode = window.KittyCatChatbotConfig?.debugMode || 
                         window.location.hostname === 'localhost' ||
                         window.location.hostname.includes('127.0.0.1') ||
                         window.location.hostname.includes('loca.lt');
        
        const baseMessage = this.language === 'vi' 
            ? 'Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau. 😔'
            : 'Sorry, an error occurred. Please try again later. 😔';
        
        if (isDevMode && error) {
            const errorInfo = error.message || 'Unknown error';
            return `${baseMessage}\n\n🔍 [Debug] ${errorInfo}`;
        }
        
        return baseMessage;
    }

    addMessage(role, content, options = {}) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        if (options.isError) {
            messageDiv.classList.add('error-message');
        }

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.textContent = role === 'assistant' ? '🐱' : '👤';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Parse markdown for assistant messages, plain text for user messages
        if (role === 'assistant' && typeof marked !== 'undefined') {
            contentDiv.innerHTML = marked.parse(content);
        } else {
            contentDiv.textContent = content;
        }
        
        // Add error details toggle for debugging
        if (options.isError && options.errorDetails) {
            const detailsBtn = document.createElement('button');
            detailsBtn.className = 'error-details-btn';
            detailsBtn.textContent = this.language === 'vi' ? 'Chi tiết lỗi' : 'Error Details';
            detailsBtn.onclick = () => {
                console.log('Full error details:', options.errorDetails);
                alert(`Error Details:\n\n${JSON.stringify(options.errorDetails, null, 2)}`);
            };
            contentDiv.appendChild(document.createElement('br'));
            contentDiv.appendChild(detailsBtn);
        }

        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);

        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    showTypingIndicator() {
        const typingId = 'typing-' + Date.now();
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant';
        messageDiv.id = typingId;

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.textContent = '🐱';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'typing-indicator';
        typingIndicator.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';
        
        contentDiv.appendChild(typingIndicator);
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);

        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();

        return typingId;
    }

    removeTypingIndicator(typingId) {
        const typingElement = document.getElementById(typingId);
        if (typingElement) {
            typingElement.remove();
        }
    }

    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    toggleLanguage() {
        this.language = this.language === 'vi' ? 'en' : 'vi';
        this.updateLanguageDisplay();
        this.updateInputPlaceholder();
    }

    updateLanguageDisplay() {
        this.currentLangSpan.textContent = this.language.toUpperCase();
    }

    updateInputPlaceholder() {
        this.inputField.placeholder = this.language === 'vi' 
            ? 'Nhập tin nhắn của bạn...' 
            : 'Type your message...';
    }
}

// Initialize chat widget when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Read config from WordPress plugin if available
    const config = window.KittyCatChatbotConfig || {};
    new ChatWidget(config);
});

