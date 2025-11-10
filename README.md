# 👶 DaycareMoments - AI-Powered Daycare Photo Sharing Platform

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://daycaremoments.streamlit.app)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 Overview

DaycareMoments is a revolutionary platform that connects daycares and parents through smart photo sharing, real-time AI assistance, and seamless communication. Built with Streamlit and powered by cutting-edge AI technologies.

**Live Demo:** https://daycaremoments.streamlit.app

## ✨ Key Features

- **📸 Smart Photo Sharing** - Upload photos with automatic face recognition and instant child tagging
- **💬 AI Assistant** - Chat with AI to find photos, get daily summaries, and answers about your child's day
- **📞 Voice Calling** - Call 24/7 AI agent via phone to hear about activities and request photos
- **🔐 Secure Authentication** - Role-based access control for parents, staff, and administrators
- **📊 Real-time Analytics** - Track engagement, photo views, and platform usage
- **📱 Mobile Responsive** - Fully optimized for mobile devices and tablets

## 🚀 Quick Start

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/gvkmdkra/daycaremoments.git
   cd daycaremoments
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   streamlit run app.py
   ```

## 🔄 Automated Deployment

Every push to `main` branch automatically deploys to Streamlit Cloud:

```bash
git add .
git commit -m "Your changes"
git push origin main
```

Streamlit Cloud will automatically deploy in 2-3 minutes!

## 📦 Tech Stack

- **Framework:** Streamlit
- **AI/LLM:** OpenAI GPT, Google Gemini
- **Database:** Turso LibSQL
- **Authentication:** Streamlit-Authenticator + BCrypt
- **Communication:** Twilio (Voice + SMS)
- **Deployment:** Streamlit Cloud + GitHub Actions

## 📧 Support

GitHub Issues: https://github.com/gvkmdkra/daycaremoments/issues

---

Made with ❤️ for daycares and parents everywhere
