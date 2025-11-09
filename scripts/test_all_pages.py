"""Test all pages for common errors"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 60)
print("TESTING ALL APPLICATION COMPONENTS")
print("=" * 60)

# Test 1: Database connection
print("\n1. Testing Database Connection...")
try:
    from app.database import get_db
    from app.database.models import User, Child, Activity, Photo

    with get_db() as db:
        user_count = db.query(User).count()
        child_count = db.query(Child).count()
        print(f"   ✅ Database connected")
        print(f"   ✅ Users: {user_count}, Children: {child_count}")
except Exception as e:
    print(f"   ❌ Database error: {e}")

# Test 2: Authentication
print("\n2. Testing Authentication...")
try:
    from app.utils.auth import hash_password, verify_password, authenticate_user

    # Test password hashing
    hashed = hash_password("test123")
    assert verify_password("test123", hashed), "Password verification failed"
    print(f"   ✅ Password hashing works")

    # Test authentication
    user = authenticate_user("parent@demo.com", "parent123")
    if user:
        print(f"   ✅ Login works: {user.email}")
    else:
        print(f"   ❌ Login failed")
except Exception as e:
    print(f"   ❌ Auth error: {e}")

# Test 3: Activity Model
print("\n3. Testing Activity Model...")
try:
    from app.database.models import Activity
    from app.database import get_db

    # Check if Activity has required fields
    required_fields = ['child_id', 'staff_id', 'activity_type', 'activity_time',
                      'duration_minutes', 'notes', 'mood']

    for field in required_fields:
        assert hasattr(Activity, field), f"Activity missing field: {field}"

    print(f"   ✅ Activity model has all required fields")

    # Test querying activities
    with get_db() as db:
        activity_count = db.query(Activity).count()
        print(f"   ✅ Activities in DB: {activity_count}")

except Exception as e:
    print(f"   ❌ Activity model error: {e}")

# Test 4: LLM Service
print("\n4. Testing LLM Service...")
try:
    from app.services.llm import get_llm_service
    from app.config import Config

    llm = get_llm_service()
    print(f"   ✅ LLM Service loaded: {llm.provider}")
    print(f"   ℹ️  Provider: {Config.LLM_PROVIDER}")

    # Check if API keys are set
    if Config.LLM_PROVIDER == 'openai':
        if Config.OPENAI_API_KEY:
            print(f"   ✅ OpenAI API key is set")
        else:
            print(f"   ⚠️  OpenAI API key not set")
    elif Config.LLM_PROVIDER == 'gemini':
        if Config.GEMINI_API_KEY:
            print(f"   ✅ Gemini API key is set")
        else:
            print(f"   ⚠️  Gemini API key not set")

except Exception as e:
    print(f"   ⚠️  LLM Service error: {e}")
    print(f"   ℹ️  AI Chat will not work without API keys")

# Test 5: Check all page files exist
print("\n5. Testing Page Files...")
try:
    pages_dir = Path(__file__).parent.parent / "pages"
    pages = list(pages_dir.glob("*.py"))
    print(f"   ✅ Found {len(pages)} page files")
    for page in pages:
        print(f"      - {page.name}")
except Exception as e:
    print(f"   ❌ Pages error: {e}")

# Test 6: Test data extraction pattern
print("\n6. Testing Data Extraction Pattern...")
try:
    from app.database import get_db
    from app.database.models import Child

    with get_db() as db:
        # Query children
        children_db = db.query(Child).limit(1).all()

        # Extract data within session (correct pattern)
        children = [{
            'id': c.id,
            'first_name': c.first_name,
            'last_name': c.last_name
        } for c in children_db]

    # Access extracted data outside session (should work)
    if children:
        child_name = children[0]['first_name']
        print(f"   ✅ Data extraction pattern works: {child_name}")
    else:
        print(f"   ⚠️  No children in database")

except Exception as e:
    print(f"   ❌ Data extraction error: {e}")

print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print("✅ = Working correctly")
print("⚠️  = Warning (may need configuration)")
print("❌ = Error (needs fixing)")
print("=" * 60)
