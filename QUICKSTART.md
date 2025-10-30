# 🚀 Quick Start Guide

## TL;DR

```bash
# 1. Setup
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env and add your XAI_API_KEY

# 3. Run
python main.py
# Or use: ./run.sh
```

Open http://localhost:8000 in your browser!

---

## Step-by-Step Setup

### 1. Prerequisites

- Python 3.9+
- [uv](https://github.com/astral-sh/uv) package manager
- xAI API Key (get from https://console.x.ai/)

### 2. Installation

```bash
# Clone and enter directory
cd lunpetshop

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # Mac/Linux
# or
.venv\Scripts\activate     # Windows

# Install dependencies
uv pip install -r requirements.txt
```

### 3. Configuration

```bash
# Create .env file
cp .env.example .env

# Edit .env and add your API key
# XAI_API_KEY=your_actual_api_key_here
```

### 4. Run the Application

**Option A: Using Python directly**
```bash
python main.py
```

**Option B: Using the run script (Mac/Linux)**
```bash
./run.sh
```

The server will start at http://localhost:8000

### 5. Test the Chatbot

**Run automated tests:**
```bash
python test_chatbot.py
```

**Use the web interface:**
1. Open http://localhost:8000
2. Click the chat button (🐱) in the bottom-right corner
3. Try asking:
   - "What products do you have for my cat?"
   - "What products do you have for my dog?"
   - "Tell me about the business"
   - "What's your address?"
   - "How can I reach you on Zalo?"

---

## 📁 Project Structure

```
lunpetshop/
├── src/
│   ├── chatbot.py        # LangGraph implementation
│   ├── knowledge_base.py # Product/business data
│   └── api.py            # FastAPI backend
├── static/
│   ├── index.html        # Frontend
│   ├── style.css         # Styling
│   └── chat.js           # Chat logic
├── main.py               # Entry point
├── test_chatbot.py       # Test suite
├── run.sh                # Quick start script
└── requirements.txt      # Dependencies
```

---

## 🔧 API Endpoints

- `GET /` - Web interface
- `GET /health` - Health check
- `POST /api/greeting` - Get greeting message
- `POST /api/chat` - Send message, get response
- `GET /docs` - API documentation (Swagger UI)

---

## 🐛 Troubleshooting

**Dependencies not installing?**
```bash
# Make sure you have uv installed
pip install uv
```

**Server won't start?**
```bash
# Check if port 8000 is already in use
lsof -i :8000
# Kill the process or change PORT in .env
```

**Chatbot not responding intelligently?**
- Make sure XAI_API_KEY is set in .env
- Without the API key, the bot uses rule-based responses (which still works for the core 5 questions!)

---

## 🎯 Success Criteria

Your MVP is ready when the chatbot can answer all 5 core questions:

✅ What products do you have for my cat?  
✅ What products do you have for my dog?  
✅ What can you tell me about the business?  
✅ What's your address?  
✅ How can I reach you on Zalo?

Run `python test_chatbot.py` to verify all questions work!

---

## 🚀 Next Steps

1. **Deploy**: Deploy to production (instructions in main README.md)
2. **Customize**: Modify `src/knowledge_base.py` to update product info
3. **Enhance**: Add new features from the roadmap
4. **Monitor**: Set up LangSmith for tracing (add LANGSMITH_API_KEY to .env)

---

## 📞 Support

For questions or issues, contact the development team.

Happy chatting! 🐾

