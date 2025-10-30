// Chat Widget JavaScript

class ChatWidget {
    constructor() {
        this.isOpen = false;
        this.threadId = null;
        this.language = 'vi';
        this.conversationStarted = false;
        
        this.initElements();
        this.attachEventListeners();
        this.loadGreeting();
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
            const response = await fetch('/api/greeting', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    language: this.language
                })
            });

            if (!response.ok) throw new Error('Failed to load greeting');

            const data = await response.json();
            this.threadId = data.thread_id;
            this.addMessage('assistant', data.greeting);
        } catch (error) {
            console.error('Error loading greeting:', error);
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
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    thread_id: this.threadId,
                    language: this.language
                })
            });

            if (!response.ok) throw new Error('Failed to send message');

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
            console.error('Error sending message:', error);
            this.removeTypingIndicator(typingId);
            this.addMessage('assistant', this.getErrorMessage());
        } finally {
            this.sendBtn.disabled = false;
            this.inputField.focus();
        }
    }

    getErrorMessage() {
        if (this.language === 'vi') {
            return 'Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau. 😔';
        } else {
            return 'Sorry, an error occurred. Please try again later. 😔';
        }
    }

    addMessage(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;

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
    new ChatWidget();
});

