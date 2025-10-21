# LùnPetShop AI Chatbot MVP 🐱

## Overview

KittyCat is an AI-powered chat widget for LùnPetShop - a Vietnamese pet shop in Đà Nẵng. The chatbot helps customers find products for their pets and learn about the business.

## ✅ MVP Success Metrics - ALL IMPLEMENTED

The MVP successfully answers all 5 core questions:

1. ✅ **"What products do you have for my cat?"**
   - Lists 8 product categories with counts
   - Shows sample products with prices
   - Available in English & Vietnamese

2. ✅ **"What products do you have for my dog?"**
   - Lists 8 product categories with counts
   - Shows sample products with prices
   - Available in English & Vietnamese

3. ✅ **"What can you tell me about the business?"**
   - Business tagline and services
   - Operating hours
   - Website information
   - Available in both languages

4. ✅ **"What's your address?"**
   - Full address: 46 Văn Cận, Khuê Trung, Cẩm Lệ, Đà Nẵng 550000
   - Operating hours
   - Available in both languages

5. ✅ **"How can I reach you on Zalo?"**
   - Zalo number: 0935005762
   - Phone, Facebook, and website links
   - Operating hours
   - Available in both languages

## 🎨 Features

### Core Functionality
- ✅ **Bilingual Support**: English & Vietnamese with instant language toggle
- ✅ **Mobile-First Design**: Responsive widget that works on all devices
- ✅ **Quick Action Buttons**: 4 preset questions for easy interaction
- ✅ **Chat Interface**: Bot messages on left, user messages on right
- ✅ **Typing Indicator**: Visual feedback while bot is "thinking"
- ✅ **Knowledge Base**: Complete product catalog and business information

### UI/UX Design
- ✅ **Color Scheme**: Gold/Yellow (#FFC107) + Dark Blue/Black (#1a1a2e, #16213e)
- ✅ **Chat Widget**: Bottom-right expandable icon (60px circular button)
- ✅ **Smooth Animations**: Slide-up, fade-in effects
- ✅ **Custom Scrollbar**: Themed with gold accent
- ✅ **Emoji Support**: 🐱 🐕 🐾 for personality

### Product Knowledge
**Cat Products (8 categories):**
- Cat Food (31 products)
- Cat Pâté (29 products)
- Treats & Snacks (25 products)
- Shampoo (26 products)
- Cat Litter (15 products)
- Toys (34 products)
- Clothing (35 products)
- Beds & Mats (15 products)

**Dog Products (8 categories):**
- Dog Food (8 products)
- Dog Pâté (5 products)
- Treats & Snacks (25 products)
- Shampoo (26 products)
- Toys (34 products)
- Clothing (35 products)
- Beds & Mats (15 products)
- Leashes & Collars (56 products)

## 🚀 How to Use

### Run the MVP

1. Open `lunpetshop-chatbot.html` in any modern web browser
2. Click the 🐱 chat icon in the bottom-right corner
3. Choose a quick action or type your own question
4. Toggle language using the EN/VI button in the header

### Test Commands (English)
- "What products do you have for my cat?"
- "What products do you have for my dog?"
- "Tell me about the business"
- "What's your address?"
- "How can I reach you on Zalo?"

### Test Commands (Vietnamese)
- "Có sản phẩm gì cho mèo của mình?"
- "Có sản phẩm gì cho chó của mình?"
- "Cho mình biết về cửa hàng"
- "Địa chỉ ở đâu?"
- "Làm sao liên hệ qua Zalo?"

## 📱 Mobile Responsiveness

- ✅ Adapts to screen sizes below 480px
- ✅ Full-screen chat on mobile devices
- ✅ Touch-optimized buttons and inputs
- ✅ Vertical quick action buttons on mobile

## 🎯 Technical Implementation

**Stack:**
- Pure HTML5, CSS3, JavaScript (ES6+)
- No external dependencies
- Single-file application (easy deployment)
- Works offline after initial load

**Architecture:**
- State management for language and conversation
- Intent detection based on keywords
- Modular knowledge base structure
- Simulated typing delays for natural feel

**Browser Support:**
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Android)

## 🔮 Future Enhancements (Post-MVP)

As outlined in the PRD:
- Integration with real AI model (Grok-4-fast from xAI)
- Direct booking for services
- Image recognition for pet recommendations
- Appointment scheduling
- Order tracking
- E-commerce integration
- Voice chat capability

## 📊 Business Information

**Business Name:** Lùn PetShop (Lùn PetShop Phụ kiện thức ăn chó mèo)

**Tagline:** "Thức ăn, phụ kiện, spa, lưu trú"

**Location:** 46 Văn Cận, Khuê Trung, Cẩm Lệ, Đà Nẵng 550000, Vietnam

**Contact:**
- Phone/Zalo: 0935005762
- Facebook: https://www.facebook.com/lunpetshop
- Website: https://lunpetshop.com/
- Hours: 8:00 AM – 9:30 PM (Daily)

## 📝 Notes

This MVP is a functional prototype demonstrating the core chatbot capabilities. It uses a rule-based intent detection system with keyword matching. For production, this would be replaced with a real AI model (as specified: Grok-4-fast from xAI) for more natural conversations and better understanding of user intent.

The chatbot is designed to be embedded as a widget on the LùnPetShop website, providing 24/7 customer support for common questions about products and services.
