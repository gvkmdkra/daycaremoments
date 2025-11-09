"""
DaycareMoments Configuration
Centralized configuration management with swappable services
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""

    # Application
    APP_NAME = os.getenv("APP_NAME", "DaycareMoments")
    ENV = os.getenv("ENV", "development")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

    # LLM Provider (Swappable: openai, gemini, claude, ollama)
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

    # Database (Swappable: turso, postgres, sqlite) - Using SQLite for now, can swap to Turso later
    DB_TYPE = os.getenv("DB_TYPE", "sqlite")
    TURSO_DB_URL = os.getenv("TURSO_DB_URL")  # Ready for Turso when Rust is installed
    TURSO_DB_AUTH_TOKEN = os.getenv("TURSO_DB_AUTH_TOKEN")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///daycare.db")

    # Storage (Swappable: gdrive, s3, r2, local)
    STORAGE_TYPE = os.getenv("STORAGE_TYPE", "local")
    GOOGLE_DRIVE_CREDENTIALS = os.getenv("GOOGLE_DRIVE_CREDENTIALS")
    AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
    R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
    R2_ACCESS_KEY = os.getenv("R2_ACCESS_KEY")
    R2_SECRET_KEY = os.getenv("R2_SECRET_KEY")
    R2_BUCKET = os.getenv("R2_BUCKET")
    LOCAL_STORAGE_PATH = os.getenv("LOCAL_STORAGE_PATH", "./uploads")

    # Communication
    # Twilio
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

    # Email
    EMAIL_SERVICE = os.getenv("EMAIL_SERVICE", "smtp")
    RESEND_API_KEY = os.getenv("RESEND_API_KEY")
    EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", "465"))
    EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
    EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "DaycareMoments")
    EMAIL_FROM_ADDRESS = os.getenv("EMAIL_FROM_ADDRESS", "noreply@daycaremoments.com")

    # Payments
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

    # Features
    ENABLE_FACE_RECOGNITION = os.getenv("ENABLE_FACE_RECOGNITION", "True").lower() == "true"
    ENABLE_AI_CHAT = os.getenv("ENABLE_AI_CHAT", "True").lower() == "true"
    ENABLE_VOICE_CALLING = os.getenv("ENABLE_VOICE_CALLING", "True").lower() == "true"
    ENABLE_SMS_NOTIFICATIONS = os.getenv("ENABLE_SMS_NOTIFICATIONS", "False").lower() == "true"

    # Limits
    PHOTO_RETENTION_DAYS = int(os.getenv("PHOTO_RETENTION_DAYS", "90"))
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    MAX_FILES_PER_UPLOAD = int(os.getenv("MAX_FILES_PER_UPLOAD", "10"))

    # Pricing Tiers
    PRICING_TIERS = {
        "free": {
            "price": 0,
            "children": 50,
            "photos_per_month": 100,
            "ai_queries_per_day": 20,
            "voice_minutes_per_month": 0,
            "features": ["email", "basic_analytics"]
        },
        "starter": {
            "price": 29,
            "children": 100,
            "photos_per_month": 500,
            "ai_queries_per_day": 100,
            "voice_minutes_per_month": 10,
            "features": ["email", "sms", "voice", "advanced_analytics"]
        },
        "professional": {
            "price": 99,
            "children": -1,  # Unlimited
            "photos_per_month": -1,  # Unlimited
            "ai_queries_per_day": -1,  # Unlimited
            "voice_minutes_per_month": 60,
            "features": ["all", "priority_support", "custom_branding"]
        }
    }

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        errors = []

        # Check LLM provider key
        if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        elif cls.LLM_PROVIDER == "gemini" and not cls.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY is required when LLM_PROVIDER=gemini")

        # Check database URL
        if not cls.DATABASE_URL:
            errors.append("DATABASE_URL or TURSO_DB_URL is required")

        return errors

    @classmethod
    def get_llm_config(cls):
        """Get LLM configuration based on provider"""
        if cls.LLM_PROVIDER == "openai":
            return {"api_key": cls.OPENAI_API_KEY, "provider": "openai"}
        elif cls.LLM_PROVIDER == "gemini":
            return {"api_key": cls.GEMINI_API_KEY, "provider": "gemini"}
        elif cls.LLM_PROVIDER == "claude":
            return {"api_key": cls.CLAUDE_API_KEY, "provider": "claude"}
        else:
            return {"url": cls.OLLAMA_URL, "provider": "ollama"}


# Validate configuration on import
config_errors = Config.validate()
if config_errors and Config.ENV == "production":
    raise ValueError(f"Configuration errors: {', '.join(config_errors)}")
