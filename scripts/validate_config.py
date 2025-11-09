"""Validate configuration and API keys"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 60)
print("DAYCAREMOMENTS - CONFIGURATION VALIDATION")
print("=" * 60)

# Test 1: Database
print("\n[1] Database Connection")
try:
    from app.database import get_db
    from app.database.models import User, Child

    with get_db() as db:
        user_count = db.query(User).count()
        child_count = db.query(Child).count()
        print(f"    PASS - Database connected")
        print(f"    Users: {user_count}, Children: {child_count}")
except Exception as e:
    print(f"    FAIL - {e}")

# Test 2: LLM Configuration
print("\n[2] LLM Service Configuration")
try:
    from app.config import Config

    print(f"    Provider: {Config.LLM_PROVIDER}")

    if Config.LLM_PROVIDER == 'gemini':
        if Config.GEMINI_API_KEY:
            print(f"    PASS - Gemini API key configured ({len(Config.GEMINI_API_KEY)} chars)")
        else:
            print(f"    FAIL - Gemini API key not set")

    if Config.LLM_PROVIDER == 'openai':
        if Config.OPENAI_API_KEY:
            print(f"    PASS - OpenAI API key configured ({len(Config.OPENAI_API_KEY)} chars)")
        else:
            print(f"    FAIL - OpenAI API key not set")

    # Test loading LLM service
    from app.services.llm import get_llm_service
    llm = get_llm_service()
    print(f"    PASS - LLM service initialized: {llm.provider}")

except Exception as e:
    print(f"    FAIL - {e}")

# Test 3: Authentication
print("\n[3] Authentication System")
try:
    from app.utils.auth import authenticate_user, hash_password, verify_password

    # Test password hashing
    test_hash = hash_password("test123")
    assert verify_password("test123", test_hash)
    print(f"    PASS - Password hashing works")

    # Test login
    user = authenticate_user("parent@demo.com", "parent123")
    if user:
        print(f"    PASS - Demo login works: {user.email}")
    else:
        print(f"    FAIL - Demo login failed")

except Exception as e:
    print(f"    FAIL - {e}")

# Test 4: Activity Model
print("\n[4] Activity Model Schema")
try:
    from app.database.models import Activity

    required_fields = ['child_id', 'staff_id', 'activity_type',
                      'activity_time', 'duration_minutes', 'notes', 'mood']

    missing = [f for f in required_fields if not hasattr(Activity, f)]

    if missing:
        print(f"    FAIL - Missing fields: {missing}")
    else:
        print(f"    PASS - All required fields present")

except Exception as e:
    print(f"    FAIL - {e}")

# Test 5: Email Configuration
print("\n[5] Email Configuration")
try:
    from app.config import Config

    if Config.EMAIL_HOST_USER:
        print(f"    PASS - Email user: {Config.EMAIL_HOST_USER}")
    else:
        print(f"    WARN - Email not configured")

except Exception as e:
    print(f"    WARN - {e}")

# Test 6: Application Pages
print("\n[6] Application Pages")
try:
    pages_dir = Path(__file__).parent.parent / "pages"
    pages = list(pages_dir.glob("*.py"))
    print(f"    PASS - Found {len(pages)} pages")
    for page in sorted(pages):
        print(f"      - {page.name}")
except Exception as e:
    print(f"    FAIL - {e}")

print("\n" + "=" * 60)
print("CONFIGURATION SUMMARY")
print("=" * 60)

try:
    from app.config import Config

    config_status = {
        "Database": "SQLite (daycare.db)",
        "LLM Provider": Config.LLM_PROVIDER,
        "Gemini API": "SET" if Config.GEMINI_API_KEY else "NOT SET",
        "OpenAI API": "SET" if Config.OPENAI_API_KEY else "NOT SET",
        "Email": Config.EMAIL_HOST_USER if Config.EMAIL_HOST_USER else "NOT SET"
    }

    for key, value in config_status.items():
        print(f"{key:20s}: {value}")

except Exception as e:
    print(f"Error reading config: {e}")

print("=" * 60)
print("\nApplication URL: http://localhost:8501")
print("=" * 60)
