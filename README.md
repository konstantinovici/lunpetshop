# 🐾 LùnPetShop KittyCat AI Chatbot

A bilingual (Vietnamese/English) AI chatbot built with LangGraph for LùnPetShop - a pet store in Đà Nẵng, Vietnam.

## 🌟 Features

**Language:** Vietnamese & English (context switching)

**AI Model:** Grok 4 Fast (xAI) - Latest with 2M token context window

## 🎯 Core Capabilities

The chatbot can answer these key questions:

1. ✅ What products do you have for my cat?
2. ✅ What products do you have for my dog?
3. ✅ What can you tell me about the business?
4. ✅ What's your address?
5. ✅ How can I reach you on Zalo?

## 🏗️ Architecture

```
lunpetshop/
├── backend/                # Python FastAPI backend
│   ├── src/
│   │   ├── api.py          # FastAPI routes & endpoints
│   │   ├── chatbot.py      # LangGraph chatbot implementation
│   │   └── knowledge_base.py # Product & business data
│   ├── main.py             # Application entry point
│   ├── requirements.txt    # Python dependencies
│   └── test_chatbot.py    # Test suite
├── widget/                 # Widget UI (single source of truth)
│   ├── assets/
│   │   ├── css/chat-widget.css
│   │   └── js/chat-widget.js
│   └── index.html          # Demo page
├── wordpress-plugin/       # WordPress plugin
│   └── lunpetshop-chatbot/
└── bin/                    # Utility scripts
```

**📚 For detailed architecture and development guide, see [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)**

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- xAI API Key (for Grok model)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd lunpetshop
```

2. **Create a virtual environment with uv**
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
uv pip install -r backend/requirements.txt
```

4. **Set up environment variables**

Create a `.env` file in the root directory:
```bash
cp .env.example .env
```

Edit `.env` and add your xAI API key:
```
XAI_API_KEY=your_xai_api_key_here
```

Get your API key from: https://console.x.ai/

### Running the Application

**Start the server:**
```bash
cd backend
python main.py
# Or from root: ./run.sh
```

The application will be available at:
- 🌐 Web Interface: http://localhost:8000
- 📚 API Docs: http://localhost:8000/docs

### Testing

**Run the test suite:**
```bash
cd backend
python test_chatbot.py
```

This will test all 5 core questions in both Vietnamese and English.

## 🎨 UI Preview

The chatbot features:
- **Chat Widget**: Bottom-right expandable chat button
- **Modern Design**: Gold/Yellow (#FFC107) + Dark Blue/Black theme
- **Quick Actions**: Pre-defined buttons for common questions
- **Language Toggle**: Easy switching between Vietnamese and English
- **Responsive**: Works great on mobile and desktop

## 🔧 API Endpoints

### `POST /api/greeting`
Get initial greeting message
```json
{
  "language": "vi"
}
```

### `POST /api/chat`
Send a message and get response
```json
{
  "message": "What products do you have for my cat?",
  "thread_id": "optional-thread-id",
  "language": "en"
}
```

### `GET /health`
Health check endpoint

## 📦 Technology Stack

- **Backend**: FastAPI
- **AI Framework**: LangGraph
- **LLM**: xAI Grok (OpenAI-compatible API)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **State Management**: LangGraph MemorySaver

## 🌐 Business Information

**LùnPetShop (Lùn PetShop Phụ kiện thức ăn chó mèo)**

- 📍 Address: 46 Văn Cận, Khuê Trung, Cẩm Lệ, Đà Nẵng 550000, Vietnam
- 📞 Phone/Zalo: 0935005762
- 🌐 Website: https://lunpetshop.com/
- 📘 Facebook: https://www.facebook.com/lunpetshop
- 🕐 Hours: 8:00 AM – 9:30 PM

**Services**: Thức ăn, phụ kiện, spa, lưu trú (Food, accessories, spa, accommodation)

## 📝 Product Categories

### Cat Products (🐱)
- Thức ăn cho Mèo (Cat Food) - 31 products
- Pate mèo (Cat Pâté) - 29 products
- Ăn vặt Bánh Thưởng (Treats & Snacks) - 25 products
- Sữa tắm (Shampoo) - 26 products
- Cát vệ sinh (Litter) - 15 products
- Đồ chơi (Toys) - 34 products
- Quần áo (Clothing) - 35 products
- Nệm Lót (Beds) - 15 products

### Dog Products (🐕)
- Thức ăn cho Chó (Dog Food) - 8 products
- Pate chó (Dog Pâté) - 5 products
- Ăn vặt Bánh Thưởng (Treats & Snacks) - 25 products
- Sữa tắm (Shampoo) - 26 products
- Đồ chơi (Toys) - 34 products
- Quần áo (Clothing) - 35 products
- Nệm Lót (Beds) - 15 products
- Vòng Cổ Dây Dắt (Leashes & Collars) - 56 products

## 🔮 Future Enhancements (Post-MVP)

- [ ] Direct booking for services
- [ ] Image recognition for pet recommendations
- [ ] Appointment scheduling
- [ ] Order tracking
- [ ] Integration with e-commerce system
- [ ] Voice chat capability
- [ ] WhatsApp/Telegram integration

## 📄 License

This project is proprietary and confidential.

## 📚 Documentation

- **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)** - Complete developer documentation
- **[MIGRATION_NOTES.md](MIGRATION_NOTES.md)** - Migration from old structure
- **[README_NEW_STRUCTURE.md](README_NEW_STRUCTURE.md)** - Quick reference

## 🤝 Contributing

For questions or support, contact the development team.

**📖 Developers**: See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for detailed architecture, development workflow, and file reference.

---

**Built with ❤️ for LùnPetShop** 🐱🐕🐾