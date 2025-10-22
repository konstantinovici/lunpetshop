# ⚡ QUICKSTART - See It NOW!

## 🎯 **3 Ways to See the Chatbot in Action**

---

### 🏃 Method 1: Local (30 seconds)

```bash
cd /workspace
./START.sh
```

Or manually:
```bash
python3 server.py
```

Then open: **http://localhost:8000**

✅ Enter your xAI API key (get from https://console.x.ai/)
✅ Click the chat icon 🐱
✅ Start chatting!

---

### ☁️ Method 2: Netlify Drop (1 minute)

1. Open: https://app.netlify.com/drop
2. **Drag the `/workspace` folder** onto the page
3. Wait 10 seconds
4. **LIVE URL INSTANTLY!** 🎉

---

### 🚀 Method 3: Vercel (1 minute)

```bash
# Install Vercel CLI (one-time)
npm install -g vercel

# Deploy
cd /workspace
vercel
```

Follow prompts → Get live URL! 🎉

---

## 🔑 Get Your xAI API Key

1. Go to: **https://console.x.ai/**
2. Sign up / Login
3. Click "Create API Key"
4. Copy the key (starts with `xai-...`)
5. Paste it when the app prompts you

**Cost:** xAI offers free trial credits!

---

## 🎮 Test These Questions

### English:
- "What products do you have for my cat?"
- "What's your address?"
- "How can I contact you on Zalo?"

### Vietnamese:
- "Có sản phẩm gì cho mèo?"
- "Địa chỉ ở đâu?"
- "Làm sao liên hệ qua Zalo?"

---

## 🆘 Issues?

**Can't start server?**
```bash
# Make sure you're in the right directory
cd /workspace

# Try with Python 3
python3 -m http.server 8000
```

**Chat icon not showing?**
- Clear browser cache (Ctrl+Shift+Delete)
- Try a different browser
- Check JavaScript is enabled

**API errors?**
- Verify your API key starts with `xai-`
- Check you have API credits at https://console.x.ai/
- Ensure internet connection

---

## 📖 Want More Details?

- Full deployment options: [DEPLOYMENT.md](./DEPLOYMENT.md)
- Complete docs: [README.md](./README.md)
- Requirements: [files/origins/pre-mvp--prd/prd--01.vc](./files/origins/pre-mvp--prd/prd--01.vc)

---

## 🎉 That's It!

You now have a **fully functional AI chatbot** powered by **xAI Grok-4-fast**!

**Choose your favorite method above and see it with your own eyes in under 60 seconds!** 👀
