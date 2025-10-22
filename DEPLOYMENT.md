# 🚀 Deployment Guide - LùnPetShop AI Chatbot

## Prerequisites

1. **Get your xAI API Key**
   - Go to: https://console.x.ai/
   - Sign up/login
   - Create an API key
   - Copy the key (starts with `xai-...`)

---

## 🎯 Option 1: Test Locally (INSTANT - Recommended for testing)

### Using Python (Pre-installed on most systems)

```bash
# Navigate to the project folder
cd /workspace

# Start the server
python3 -m http.server 8000

# Or if you have npm
npm start
```

Then open: **http://localhost:8000**

✅ **That's it!** Enter your xAI API key in the interface and start chatting!

---

## ☁️ Option 2: Deploy to Vercel (1-Click Deploy)

### Method A: Via Vercel CLI (Fast)

```bash
# Install Vercel CLI globally (one-time)
npm install -g vercel

# Deploy from the project directory
cd /workspace
vercel

# Follow the prompts:
# - "Set up and deploy?" → Yes
# - "Which scope?" → Your account
# - "Link to existing project?" → No
# - "What's your project's name?" → lunpetshop-chatbot
# - "In which directory is your code located?" → ./
```

**Done!** Vercel will give you a live URL instantly.

### Method B: Via Vercel Website

1. Go to: https://vercel.com/
2. Click "Add New" → "Project"
3. Import your Git repository OR drag-and-drop the `/workspace` folder
4. Click "Deploy"
5. Get your live URL!

---

## 🌐 Option 3: Deploy to Netlify (1-Click Deploy)

### Method A: Drag & Drop (Easiest)

1. Go to: https://app.netlify.com/drop
2. Drag the entire `/workspace` folder onto the page
3. **Instant deployment!** Get your live URL

### Method B: Via Netlify CLI

```bash
# Install Netlify CLI (one-time)
npm install -g netlify-cli

# Deploy
cd /workspace
netlify deploy --prod

# Follow prompts and get your live URL
```

---

## 📦 Option 4: Deploy to GitHub Pages

```bash
# 1. Create a new GitHub repo
# 2. Push your code
git init
git add .
git commit -m "Initial commit: LùnPetShop chatbot"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/lunpetshop-chatbot.git
git push -u origin main

# 3. Go to GitHub → Settings → Pages
# 4. Source: Deploy from branch "main" folder "/"
# 5. Save and wait 1-2 minutes
```

Your site will be live at: `https://YOUR_USERNAME.github.io/lunpetshop-chatbot/`

---

## 🔧 Option 5: Deploy to Any Static Host

The chatbot is a single HTML file with no backend dependencies!

**Compatible with:**
- AWS S3 + CloudFront
- Google Cloud Storage
- Azure Static Web Apps
- Cloudflare Pages
- Render
- Railway
- Surge.sh

**Simple deployment:**
1. Upload `index.html` to any static file host
2. Configure as the index/root page
3. Done!

---

## ⚡ Quick Test URLs

After deploying, test with these questions:

**English:**
- "What products do you have for my cat?"
- "What's your address?"
- "How can I contact you on Zalo?"

**Vietnamese:**
- "Có sản phẩm gì cho mèo?"
- "Địa chỉ ở đâu?"
- "Làm sao liên hệ qua Zalo?"

---

## 🔒 API Key Security

**Important:** The API key is stored in browser `localStorage` only. It never leaves the user's browser.

For production, consider:
1. **Backend Proxy:** Create a simple serverless function to proxy API requests
2. **Rate Limiting:** Implement usage limits
3. **User Authentication:** Add login to track usage

**Example backend (optional - for production):**
```javascript
// vercel/functions/api/chat.js
export default async function handler(req, res) {
  const response = await fetch('https://api.x.ai/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.XAI_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(req.body)
  });
  const data = await response.json();
  res.json(data);
}
```

---

## 📊 Monitoring & Analytics

Add to your HTML `<head>` for tracking:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=YOUR-GA-ID"></script>

<!-- Or Simple Analytics -->
<script async defer src="https://scripts.simpleanalyticscdn.com/latest.js"></script>
```

---

## 🎨 Customization

All settings are in `index.html`:

- **Colors:** Search for `#FFC107` and `#1a1a2e`
- **Business Info:** Update the `systemPrompt` object
- **Language:** Modify `translations` object
- **Style:** Edit the `<style>` section

---

## 🆘 Troubleshooting

**Chat icon doesn't appear:**
- Check browser console for errors
- Ensure JavaScript is enabled

**API errors:**
- Verify API key is correct
- Check xAI API status: https://status.x.ai/
- Ensure you have API credits

**CORS errors:**
- Only happens in local file:// protocol
- Use any of the deployment methods above

---

## 📞 Support

- **xAI API Docs:** https://docs.x.ai/
- **xAI Console:** https://console.x.ai/
- **Questions?** Check your xAI dashboard for usage and limits

---

## 🎉 You're Ready!

Choose any option above and your chatbot will be live in minutes!

**Recommended flow:**
1. ✅ Test locally first (Option 1)
2. ✅ Then deploy to Vercel/Netlify (Option 2/3)
3. ✅ Share the live URL!
