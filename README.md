# 👶 DaycareMoments

**AI-Powered Photo Sharing Platform for Daycares**

A modern, professional daycare management system with AI-powered features, beautiful UI, and seamless parent-staff communication.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://daycaremoments-app.streamlit.app)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ Features

### 🎨 Professional UI
- **Purple gradient theme** throughout the application
- Modern card designs with animations
- Responsive layout for desktop and mobile
- Professional typography and spacing

### 📸 Smart Photo Sharing
- Automatic face recognition using AI
- Instant child tagging on upload
- Photo approval workflow for staff
- Gallery view with filters and search

### 💬 AI Chat Assistant
- Natural language queries about child activities
- **Interactive charts and graphs** for activity statistics
- **Photo display** in chat responses
- Daily summaries and insights

### 📞 Voice Calling
- 24/7 AI agent via Twilio integration
- Request photos via phone call
- Hear about child's daily activities
- Automated voice responses

### 👥 Multi-Role System
- **Parents**: View photos, chat with AI, receive notifications
- **Staff**: Upload photos, manage activities, approve content
- **Admin**: System management, user control, analytics

### 🔔 Smart Notifications
- Email notifications via Gmail SMTP
- SMS alerts via Twilio
- Real-time activity updates
- Customizable notification preferences

---

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/gvkmdkra/daycaremoments.git
cd daycaremoments
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Create environment file**
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. **Run the application**
```bash
streamlit run app.py
```

5. **Access the app**
- Open browser to: http://localhost:8501

### Demo Accounts

**Parent Account**
- Email: `parent@demo.com`
- Password: `password123`

**Staff Account**
- Email: `staff@demo.com`
- Password: `password123`

**Admin Account**
- Email: `admin@demo.com`
- Password: `password123`

---

## 🌐 Deployment

### Streamlit Community Cloud (Recommended)

1. Fork this repository to your GitHub account
2. Visit https://share.streamlit.io
3. Click "New app" and select your forked repository
4. Configure secrets (see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md))
5. Click "Deploy"

**Detailed deployment instructions**: See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

## 🔧 Configuration

### Required API Keys

**LLM Provider** (Choose one):
- OpenAI API Key - https://platform.openai.com/api-keys
- Google Gemini API Key - https://makersuite.google.com/app/apikey

**Email Notifications**:
- Gmail account with App Password
- Guide: https://support.google.com/accounts/answer/185833

**Voice Calling** (Optional):
- Twilio Account SID
- Twilio Auth Token
- Twilio Phone Number
- Sign up: https://www.twilio.com/try-twilio

### Environment Variables

Create a `.env` file or configure Streamlit Secrets:

```env
# LLM Configuration
OPENAI_API_KEY=your-openai-key
GEMINI_API_KEY=your-gemini-key
LLM_PROVIDER=openai

# Email
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Twilio (Optional)
TWILIO_ENABLED=true
TWILIO_ACCOUNT_SID=your-sid
TWILIO_AUTH_TOKEN=your-token
TWILIO_PHONE_NUMBER=your-number

# Database (Optional - uses SQLite by default)
TURSO_DB_URL=your-turso-url
TURSO_DB_AUTH_TOKEN=your-turso-token
```

---

## 📁 Project Structure

```
daycaremoments/
├── app.py                      # Main application entry point
├── requirements.txt            # Python dependencies
├── .streamlit/
│   ├── config.toml            # Streamlit configuration
│   └── secrets.toml.example   # Secrets template
├── app/
│   ├── database/
│   │   ├── models.py          # SQLAlchemy models
│   │   └── __init__.py        # Database initialization
│   ├── services/
│   │   ├── llm/               # LLM adapters (OpenAI, Gemini)
│   │   ├── notifications/     # Email & SMS services
│   │   └── voice/             # Twilio voice integration
│   └── utils/
│       ├── auth.py            # Authentication utilities
│       └── ui_theme.py        # Professional UI theme
├── pages/
│   ├── 01_🔐_Login.py         # Login & registration
│   ├── 02_👪_Parent_Portal.py # Parent dashboard
│   ├── 03_👨‍🏫_Staff_Dashboard.py # Staff dashboard
│   ├── 04_⚙️_Admin_Panel.py   # Admin panel
│   ├── 05_💬_AI_Chat.py       # AI chat assistant
│   ├── 06_📞_Voice_Call.py    # Voice calling interface
│   └── 07_💰_Pricing.py       # Pricing plans
└── tests/                     # Test files
```

---

## 🎯 Key Technologies

- **Frontend**: Streamlit
- **Backend**: Python 3.11+
- **Database**: SQLAlchemy (SQLite/Turso)
- **AI/LLM**: OpenAI GPT / Google Gemini
- **Charts**: Plotly
- **Authentication**: bcrypt
- **Email**: smtplib (Gmail)
- **SMS/Voice**: Twilio
- **Face Recognition**: OpenCV (planned)

---

## 📸 Screenshots

### Home Page
Beautiful landing page with feature highlights and statistics.

### Parent Portal
View your child's photos, activities, and daily summaries.

### AI Chat Assistant
Ask questions and get interactive charts and photo displays.

### Staff Dashboard
Upload photos, manage activities, and communicate with parents.

---

## 🛣️ Roadmap

- [x] Professional UI theme with purple gradients
- [x] AI chat with charts and photo display
- [x] Multi-role authentication system
- [x] Email and SMS notifications
- [x] Voice calling integration
- [ ] Face recognition for auto-tagging
- [ ] Mobile app (React Native)
- [ ] Real-time notifications (WebSocket)
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Payment integration (Stripe)
- [ ] Calendar view for activities
- [ ] Video upload support
- [ ] Parent-staff messaging

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Sivaneshwaran**
- GitHub: [@gvkmdkra](https://github.com/gvkmdkra)
- Email: sivaneshwaran16@gmail.com

---

## 🙏 Acknowledgments

- Streamlit team for the amazing framework
- OpenAI for GPT models
- Google for Gemini AI
- Twilio for voice/SMS services
- All contributors and testers

---

## 📞 Support

If you encounter any issues or have questions:
- Open an issue on GitHub
- Check the [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- Email: sivaneshwaran16@gmail.com

---

## ⭐ Show Your Support

If you find this project helpful, please give it a ⭐️ on GitHub!

---

**Made with ❤️ for daycares and parents everywhere**

© 2025 DaycareMoments | Professional Daycare Management Platform
