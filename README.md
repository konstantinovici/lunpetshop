# 🐱 LùnPetShop AI Chatbot - KittyCat

> **Powered by xAI Grok-4-fast** | Mobile-First | Bilingual (EN/VI)

An intelligent AI chatbot widget for LùnPetShop pet store in Đà Nẵng, Vietnam. Built with xAI's Grok API for natural, conversational customer support.

![Status](https://img.shields.io/badge/status-MVP-success)
![AI](https://img.shields.io/badge/AI-xAI%20Grok--4--fast-blue)
![Language](https://img.shields.io/badge/language-EN%20%7C%20VI-orange)

---

## 🚀 **INSTANT START** - See It With Your Own Eyes!

### Option 1: One-Command Local Test (Fastest)

```bash
cd /workspace
python3 server.py
```

Then open: **http://localhost:8000** 🎉

### Option 2: One-Click Cloud Deploy

**Netlify (Drag & Drop):**
1. Go to https://app.netlify.com/drop
2. Drag `/workspace` folder
3. **LIVE IN 10 SECONDS!**

**Vercel:**
```bash
npx vercel --prod
```

**See full deployment options:** [DEPLOYMENT.md](./DEPLOYMENT.md)

---

## ✅ Features

### 🎯 Core Functionality
- ✅ **xAI Grok Integration** - Real AI-powered responses using Grok-4-fast
- ✅ **Bilingual Support** - Seamless English ↔️ Vietnamese switching
- ✅ **Mobile-First Design** - Beautiful responsive widget
- ✅ **Quick Actions** - 4 preset buttons for common questions
- ✅ **Conversation Memory** - Context-aware multi-turn conversations
- ✅ **Typing Indicators** - Natural chat experience

### 💼 Business Knowledge Base
- ✅ **210+ Products** across 15+ categories
- ✅ **Cat & Dog Products** with prices and examples
- ✅ **Business Information** - Address, hours, services
- ✅ **Contact Details** - Zalo, phone, Facebook, website

### 🎨 Design
- ✅ **Gold/Yellow (#FFC107)** + **Dark Blue/Black** theme
- ✅ **Bottom-right expandable widget**
- ✅ **Smooth animations** and transitions
- ✅ **Custom scrollbars** with brand colors
- ✅ **Emoji support** 🐱🐕🐾

---

## 📋 Requirements Met

### ✅ All 5 MVP Success Metrics:

1. ✅ "What products do you have for my cat?"
2. ✅ "What products do you have for my dog?"
3. ✅ "What can you tell me about the business?"
4. ✅ "What's your address?"
5. ✅ "How can I reach you on Zalo?"

**Plus:** Natural conversation, context awareness, and multilingual support!

---

## 🔑 Setup

### 1. Get Your xAI API Key

1. Go to: https://console.x.ai/
2. Sign up/Login
3. Create API key
4. Copy it (starts with `xai-...`)

### 2. Configure in App

When you open the chatbot, you'll see a setup screen:
1. Paste your API key
2. Click "Save API Key"
3. Start chatting!

**Security:** API key is stored in browser localStorage only. Never sent to any server except xAI.

---

## 📂 Project Structure

```
/workspace/
├── index.html           # Main chatbot application (xAI integrated)
├── server.py            # Local development server
├── package.json         # NPM scripts and metadata
├── vercel.json          # Vercel deployment config
├── netlify.toml         # Netlify deployment config
├── DEPLOYMENT.md        # Comprehensive deployment guide
├── README.md            # This file
└── files/origins/       # Original requirements
    └── pre-mvp--prd/
        └── prd--01.vc   # Product Requirements Document
```

---

## 🎮 Usage

### Test Commands (English)
```
- What products do you have for my cat?
- What products do you have for my dog?
- Tell me about the business
- What's your address?
- How can I reach you on Zalo?
- Do you have cat litter?
- What are your operating hours?
```

### Test Commands (Vietnamese)
```
- Có sản phẩm gì cho mèo của mình?
- Có sản phẩm gì cho chó của mình?
- Cho mình biết về cửa hàng
- Địa chỉ ở đâu?
- Làm sao liên hệ qua Zalo?
- Có cát vệ sinh không?
- Giờ mở cửa khi nào?
```

---

## 🏪 Business Information

**Business Name:** Lùn PetShop (Lùn PetShop Phụ kiện thức ăn chó mèo)

**Tagline:** "Thức ăn, phụ kiện, spa, lưu trú"

**Location:** 46 Văn Cận, Khuê Trung, Cẩm Lệ, Đà Nẵng 550000, Vietnam

**Contact:**
- 📱 Phone/Zalo: 0935005762
- 📘 Facebook: https://www.facebook.com/lunpetshop
- 🌐 Website: https://lunpetshop.com/
- ⏰ Hours: 8:00 AM – 9:30 PM (Daily)

---

## 🧠 AI Model Details

**Model:** Grok-4-fast (xAI)
**API:** https://api.x.ai/v1/chat/completions
**Features:**
- Natural language understanding
- Context-aware conversations
- Bilingual support (EN/VI)
- Product knowledge integration
- Business information retrieval

**System Prompt:** Comprehensive knowledge base with:
- 210+ products across 15+ categories
- Complete business details
- Prices in Vietnamese Dong (₫)
- Friendly, helpful personality

---

## 🛠️ Technical Stack

**Frontend:**
- Pure HTML5, CSS3, JavaScript (ES6+)
- No build step required
- No external dependencies
- Single-file deployment

**AI Integration:**
- xAI Grok-4-fast API
- Fetch API for HTTP requests
- Conversation history management
- Automatic language detection

**State Management:**
- LocalStorage for API key
- In-memory conversation history
- Language preference persistence

---

## 📱 Browser Support

- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Mobile browsers (iOS Safari, Chrome Android)
- ✅ Works offline after initial load (except AI calls)

---

## 🔮 Future Enhancements

As outlined in the PRD:
- [ ] Backend API proxy for key security
- [ ] Direct booking for services
- [ ] Image recognition for pet recommendations
- [ ] Appointment scheduling
- [ ] Order tracking integration
- [ ] E-commerce system integration
- [ ] Voice chat capability
- [ ] Admin dashboard for analytics

---

## 🎨 Customization

Edit `index.html` to customize:

**Colors:**
```css
/* Primary color */
#FFC107 → Your color

/* Background colors */
#1a1a2e, #16213e → Your colors
```

**Business Info:**
```javascript
// Update systemPrompt object (line ~380)
const systemPrompt = {
  en: `Your business info...`,
  vi: `Thông tin của bạn...`
}
```

**Translations:**
```javascript
// Update translations object (line ~360)
const translations = {
  en: { ... },
  vi: { ... }
}
```

---

## 🐛 Troubleshooting

**"Please configure your xAI API key first!"**
- Get key from: https://console.x.ai/
- Make sure it starts with `xai-`

**API connection errors:**
- Check API key is correct
- Verify xAI API status: https://status.x.ai/
- Ensure you have API credits

**Chat widget not showing:**
- Check browser console for errors
- Ensure JavaScript is enabled
- Try hard refresh (Ctrl+F5)

**CORS errors:**
- Don't open as `file://` - use a server
- Use `python3 server.py` for local testing

---

## 📄 License

MIT License - Free to use and modify

---

## 🤝 Contributing

This is an MVP. Improvements welcome!

**Areas for contribution:**
- Additional languages (Thai, Chinese, etc.)
- More product categories
- UI/UX improvements
- Performance optimizations
- Accessibility enhancements

---

## 📞 Support & Contact

**For xAI API issues:**
- Docs: https://docs.x.ai/
- Console: https://console.x.ai/

**For business inquiries:**
- LùnPetShop Zalo: 0935005762
- Facebook: facebook.com/lunpetshop

---

## 🎉 Credits

**Developed for:** LùnPetShop, Đà Nẵng, Vietnam
**Powered by:** xAI Grok-4-fast
**Design:** Mobile-first, modern pet care aesthetic

---

**Ready to deploy?** Check [DEPLOYMENT.md](./DEPLOYMENT.md) for all options!

**Want to test locally?** Run: `python3 server.py` and open http://localhost:8000
