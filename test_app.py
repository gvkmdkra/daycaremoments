#!/usr/bin/env python3
"""
DaycareMoments - Simple Test Script
Tests basic imports and configuration
"""

import sys

def test_imports():
    """Test all critical imports"""
    print("Testing imports...")

    tests = [
        ("streamlit", "Streamlit framework"),
        ("app.database", "Database module"),
        ("app.config", "Configuration"),
        ("app.utils.auth", "Authentication"),
        ("app.utils.ui_theme", "UI Theme"),
    ]

    passed = 0
    failed = 0

    for module, description in tests:
        try:
            __import__(module)
            print(f"  [PASS] {description}")
            passed += 1
        except ImportError as e:
            print(f"  [FAIL] {description}: {e}")
            failed += 1

    return passed, failed

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    try:
        from app.config import Config
        print("  [PASS] Configuration loaded")

        # Check for key configuration
        if Config.LLM_PROVIDER:
            print(f"  [PASS] LLM Provider: {Config.LLM_PROVIDER}")
        else:
            print("  [WARN] LLM Provider not set (optional)")

        return True
    except Exception as e:
        print(f"  [FAIL] Configuration error: {e}")
        return False

def test_database():
    """Test database connection"""
    print("\nTesting database...")
    try:
        from app.database import init_db
        init_db()
        print("  [PASS] Database initialized")
        return True
    except Exception as e:
        print(f"  [FAIL] Database error: {e}")
        return False

def main():
    print("=" * 50)
    print("  DaycareMoments - System Test")
    print("=" * 50 + "\n")

    passed, failed = test_imports()
    config_ok = test_config()
    db_ok = test_database()

    print("\n" + "=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50 + "\n")

    if failed == 0 and config_ok and db_ok:
        print("[SUCCESS] All tests passed! Ready to run.")
        print("Run: python run.py")
        return 0
    else:
        print("[FAILED] Some tests failed. Check errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
