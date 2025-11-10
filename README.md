# 👶 DaycareMoments

**AI-Powered Photo Sharing Platform for Daycares**

[![Live Demo](https://img.shields.io/badge/demo-live-success)](https://daycaremoments.streamlit.app)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org)
[![Streamlit](https://img.shields.io/badge/streamlit-1.31-red)](https://streamlit.io)

> Connecting daycares and parents through smart photo sharing, AI assistance, and seamless communication.

**🌐 Live Demo:** https://daycaremoments.streamlit.app

---

## ✨ Features

- 📸 **Smart Photo Sharing** - AI-powered face recognition and auto-tagging
- 💬 **AI Assistant** - Chat to find photos and get daily summaries
- 📞 **Voice Calling** - 24/7 AI agent via Twilio
- 🔐 **Secure** - Role-based access (Parents, Staff, Admin)
- 📱 **Mobile-Responsive** - Works perfectly on all devices

---

## 🚀 Quick Start

### Option 1: Run Locally (Fastest)

```bash
# 1. Clone repository
git clone https://github.com/gvkmdkra/daycaremoments.git
cd daycaremoments

# 2. Run the app
python run.py
```

The script will:
- Check Python version (3.11+ required)
- Install dependencies
- Start the app at http://localhost:8501

### Option 2: Manual Setup

```bash
# 1. Clone and setup
git clone https://github.com/gvkmdkra/daycaremoments.git
cd daycaremoments
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run app
streamlit run app.py
```

### Option 3: Test First

```bash
# Run system tests
python test_app.py
```

---

## 📁 Project Structure

```
daycaremoments/
├── app.py                  # Main entry point
├── run.py                  # Quick start script
├── test_app.py             # System tests
├── requirements.txt        # Python dependencies
├── .python-version         # Python 3.11
│
├── app/                    # Core application
│   ├── config.py           # Configuration
│   ├── database/           # Database & models
│   ├── services/           # LLM, storage, email
│   └── utils/              # Auth, UI theme
│
├── pages/                  # Streamlit pages
│   ├── 01_🔐_Login.py
│   ├── 02_👪_Parent_Portal.py
│   ├── 03_👨‍🏫_Staff_Dashboard.py
│   ├── 04_⚙️_Admin_Panel.py
│   ├── 05_💬_AI_Chat.py
│   ├── 06_📞_Voice_Call.py
│   └── 07_💰_Pricing.py
│
└── docs/                   # Documentation
    ├── ARCHITECTURE.md     # System design
    ├── DEPLOYMENT.md       # Deployment guide
    └── SUMMARY.md          # Project summary
```

---

## 🔧 Configuration

Create `.env` file (optional for local development):

```env
# AI/LLM
OPENAI_API_KEY=your_key
GEMINI_API_KEY=your_key
LLM_PROVIDER=openai

# Twilio
TWILIO_ENABLED=true
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890

# Database
TURSO_DB_URL=https://your-db.turso.io
TURSO_DB_AUTH_TOKEN=your_token
```

---

## 🚀 Deployment

### Deploy to Streamlit Cloud

1. Fork/clone this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repository
4. Add secrets in app settings
5. Deploy!

**Auto-deployment enabled:** Every push to `main` automatically deploys.

---

## 📚 Documentation

- **[Architecture](docs/ARCHITECTURE.md)** - System design and data flows
- **[Deployment](docs/DEPLOYMENT.md)** - Deployment guide and troubleshooting
- **[Summary](docs/SUMMARY.md)** - Project completion overview

---

## 🧪 Testing

```bash
# Run system tests
python test_app.py

# Test imports
python -c "import streamlit; import app.database; print('✅ OK')"

# Check Python version
python --version  # Should be 3.11+
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Framework** | Streamlit |
| **AI/LLM** | OpenAI GPT, Google Gemini |
| **Database** | Turso LibSQL + SQLAlchemy |
| **Auth** | Streamlit-Authenticator + BCrypt |
| **Communication** | Twilio (Voice + SMS) |
| **Deployment** | Streamlit Cloud |

---

## 📱 Mobile Support

Fully responsive design with:
- Adaptive layouts
- Touch-friendly buttons
- Responsive typography
- Mobile-optimized navigation

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file

---

## 🆘 Support

- **Issues:** [GitHub Issues](https://github.com/gvkmdkra/daycaremoments/issues)
- **Docs:** [Documentation](docs/)
- **Live Demo:** [daycaremoments.streamlit.app](https://daycaremoments.streamlit.app)

---

## 🎯 Quick Commands

```bash
# Start app
python run.py

# Run tests
python test_app.py

# Install dependencies
pip install -r requirements.txt

# Deploy (auto-deploys on push to main)
git push origin main
```

---

**Made with ❤️ for daycares and parents everywhere**

© 2025 DaycareMoments
