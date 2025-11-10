# 🏗️ DaycareMoments Architecture Documentation

## System Overview

DaycareMoments is a modular, cloud-native application built with Streamlit, featuring a clean separation of concerns and swappable service adapters.

## Directory Structure

```
daycaremoments/
├── app.py                      # Entry point - Landing page
├── .python-version             # Python 3.11 specification
├── requirements.txt            # Minimal dependencies
├── packages.txt                # System packages (empty)
│
├── .github/workflows/
│   └── deploy.yml              # Automated CI/CD pipeline
│
├── app/
│   ├── config.py               # Centralized configuration
│   ├── database/
│   │   ├── connection.py       # Turso LibSQL client
│   │   └── models.py           # SQLAlchemy ORM models
│   ├── services/
│   │   ├── llm/                # AI adapter pattern
│   │   │   ├── openai_adapter.py
│   │   │   ├── gemini_adapter.py
│   │   │   ├── claude_adapter.py
│   │   │   └── ollama_adapter.py
│   │   ├── storage/            # Storage adapter pattern
│   │   │   ├── local_adapter.py
│   │   │   ├── s3_adapter.py
│   │   │   ├── r2_adapter.py
│   │   │   └── google_drive_adapter.py
│   │   ├── email_service.py
│   │   └── face_recognition_service.py
│   └── utils/
│       ├── auth.py             # Authentication logic
│       └── ui_theme.py         # CSS theme + components
│
└── pages/                      # Streamlit multipage structure
    ├── 01_🔐_Login.py
    ├── 02_👪_Parent_Portal.py
    ├── 03_👨‍🏫_Staff_Dashboard.py
    ├── 04_⚙️_Admin_Panel.py
    ├── 05_💬_AI_Chat.py
    ├── 06_📞_Voice_Call.py
    └── 07_💰_Pricing.py
```

## Core Components

### 1. Entry Point (app.py)
- Initializes database
- Applies UI theme
- Renders hero section with animations
- Shows login prompt or welcome message
- Displays feature cards and pricing

### 2. Database Layer (app/database/)
- **connection.py**: Manages Turso LibSQL connection
- **models.py**: SQLAlchemy models for users, children, photos, activities

### 3. Service Layer (app/services/)
#### LLM Adapters (Swappable AI Providers)
- Abstract interface for AI operations
- Implementations: OpenAI, Gemini, Claude, Ollama
- Configured via `LLM_PROVIDER` environment variable

#### Storage Adapters (Swappable Storage)
- Abstract interface for file operations
- Implementations: Local, S3, R2, Google Drive
- Configured via `STORAGE_PROVIDER` environment variable

### 4. UI Layer (app/utils/ui_theme.py)
- **apply_professional_theme()**: Injects CSS for gradient backgrounds, buttons, cards
- **create_feature_card()**: Generates feature cards with icons
- **create_metric_card()**: Generates metric cards with gradients
- Mobile-responsive media queries

### 5. Pages (pages/)
Each page is a separate Streamlit script:
- **01_Login.py**: Authentication (register/login)
- **02_Parent_Portal.py**: View child photos, activities, chat
- **03_Staff_Dashboard.py**: Upload photos, manage activities
- **04_Admin_Panel.py**: Manage users, daycares, settings
- **05_AI_Chat.py**: Conversational AI interface
- **06_Voice_Call.py**: Twilio voice integration
- **07_Pricing.py**: Subscription plans

## Data Flow

### Authentication Flow
```
User → Login Page → auth.py → Database
      ↓
  Session State (st.session_state)
      ↓
  Redirect to Dashboard
```

### Photo Upload Flow
```
Staff → Upload UI → Local Storage
           ↓
     Face Recognition Service
           ↓
     Tag Children Automatically
           ↓
     Save Metadata to Database
           ↓
     Notify Parents (Email/SMS)
```

### AI Chat Flow
```
User → AI Chat Page → LLM Adapter (OpenAI/Gemini)
           ↓
     Retrieve Context (Photos, Activities)
           ↓
     Generate Response
           ↓
     Display in Chat UI
           ↓
     Save to ai_chat_history
```

## Configuration Management

### Environment Variables (.env or Streamlit Secrets)
```env
# AI/LLM
GEMINI_API_KEY=xxx
OPENAI_API_KEY=xxx
LLM_PROVIDER=openai

# Communication
TWILIO_ENABLED=true
TWILIO_ACCOUNT_SID=xxx
TWILIO_AUTH_TOKEN=xxx

# Database
TURSO_DB_URL=https://xxx.turso.io
TURSO_DB_AUTH_TOKEN=xxx
```

### Accessing Config
```python
from app.config import get_config
config = get_config()
api_key = config.get('OPENAI_API_KEY')
```

## Deployment Pipeline

### GitHub Actions Workflow
1. **Trigger**: Push to `main` branch
2. **Checkout**: Pull latest code
3. **Setup**: Install Python 3.11
4. **Install**: Run `pip install -r requirements.txt`
5. **Notify**: Log deployment info
6. **Streamlit Cloud**: Auto-detects changes and deploys

### Streamlit Cloud Settings
- **Python Version**: 3.11 (via `.python-version`)
- **Main File**: `app.py`
- **Requirements**: `requirements.txt`
- **Secrets**: Configure in Streamlit Cloud dashboard

## Design Patterns

### 1. Adapter Pattern
Used for LLM and Storage services to allow easy swapping:
```python
class LLMAdapter(ABC):
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass

class OpenAIAdapter(LLMAdapter):
    def generate_response(self, prompt: str) -> str:
        # OpenAI implementation
```

### 2. Session State Management
Streamlit session state stores user authentication and app state:
```python
st.session_state['user_id'] = user.id
st.session_state['role'] = user.role
```

### 3. Page-based Architecture
Streamlit multipage app with `pages/` directory:
- Each file is a separate page
- Numbered prefix controls order
- Emoji prefix for visual navigation

## Security Considerations

1. **Password Hashing**: BCrypt for secure password storage
2. **Role-based Access**: Check `st.session_state['role']` before operations
3. **Environment Variables**: Never commit API keys to Git
4. **GitHub Secret Scanning**: Enabled to prevent accidental key commits
5. **Database Security**: Turso LibSQL with authentication tokens

## Performance Optimizations

1. **Minimal Dependencies**: Only 14 packages for fast deployment
2. **Python 3.11**: Faster runtime performance
3. **Lazy Loading**: Import heavy modules only when needed
4. **Caching**: Use `@st.cache_data` for expensive operations
5. **Async Operations**: Background tasks for notifications

## Mobile Responsiveness

### CSS Media Queries
```css
@media (max-width: 768px) {
    .main { padding: 0.5rem !important; }
    h1 { font-size: 2rem !important; }
    .stButton > button { padding: 0.5rem 1rem !important; }
}
```

### Responsive Columns
```python
# Desktop: 3 columns, Mobile: 1 column
col1, col2, col3 = st.columns([1, 1, 1])
```

## Testing Strategy

1. **Local Testing**: `streamlit run app.py`
2. **Import Validation**: `python -m py_compile app.py`
3. **Dependency Check**: `pip install -r requirements.txt`
4. **Manual Testing**: Test on desktop and mobile browsers
5. **Production Testing**: Verify on Streamlit Cloud after deployment

## Troubleshooting

### Common Issues
- **Import errors**: Check `requirements.txt`
- **Database connection**: Verify Turso credentials
- **AI not responding**: Check API keys and quotas
- **Mobile layout issues**: Test with browser dev tools

## Future Enhancements

- [ ] Unit tests with pytest
- [ ] Integration tests for API endpoints
- [ ] Performance monitoring with Sentry
- [ ] Advanced analytics dashboard
- [ ] Multi-language support (i18n)
- [ ] Progressive Web App (PWA) features
- [ ] Push notifications
- [ ] Offline mode support

---

Last Updated: 2025-01-09
