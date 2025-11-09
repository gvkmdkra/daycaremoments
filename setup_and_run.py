"""Complete setup and run script"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and print results"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")

    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    if result.stdout:
        print(result.stdout)
    if result.stderr and result.returncode != 0:
        print(f"⚠️ Error: {result.stderr}")

    return result.returncode == 0


def main():
    """Main setup and run function"""
    print("\n" + "="*60)
    print("🎯 DaycareMoments - Complete Setup & Run")
    print("="*60)

    base_dir = Path(__file__).parent

    # Step 1: Check Python version
    print(f"\n✅ Python version: {sys.version}")

    # Step 2: Install dependencies
    print("\n📦 Installing dependencies...")
    success = run_command(
        "pip install streamlit streamlit-authenticator sqlalchemy libsql-client openai google-generativeai face-recognition opencv-python twilio stripe pytest bcrypt python-dotenv",
        "Installing Python packages"
    )

    if not success:
        print("⚠️ Some packages failed to install, continuing anyway...")

    # Step 3: Seed demo data
    print("\n🌱 Seeding demo data...")
    seed_script = base_dir / "scripts" / "seed_demo_data.py"
    run_command(f"python {seed_script}", "Creating demo database and users")

    # Step 4: Run tests
    print("\n🧪 Running tests...")
    test_auth = base_dir / "tests" / "test_auth.py"
    test_db = base_dir / "tests" / "test_database.py"

    print("\n  Testing authentication...")
    run_command(f"python {test_auth}", "Authentication tests")

    print("\n  Testing database...")
    run_command(f"python {test_db}", "Database tests")

    # Step 5: Display summary
    print("\n" + "="*60)
    print("✅ SETUP COMPLETE!")
    print("="*60)

    print("\n📋 Demo Accounts Created:")
    print("-" * 60)
    print("👑 ADMIN:    admin@demo.com  / admin123")
    print("👨‍🏫 STAFF:    staff@demo.com  / staff123")
    print("👪 PARENT:   parent@demo.com / parent123")
    print("-" * 60)

    print("\n🎯 Next Steps:")
    print("1. Configure your .env file with API keys (optional)")
    print("2. Run: streamlit run app.py")
    print("3. Open browser to: http://localhost:8501")
    print("4. Login with demo credentials")

    print("\n💡 Quick Start:")
    print("   streamlit run app.py")

    print("\n" + "="*60)
    print("🚀 Ready to launch DaycareMoments!")
    print("="*60 + "\n")

    # Ask if user wants to start the app
    response = input("\n🎬 Start the application now? (y/n): ")

    if response.lower() == 'y':
        print("\n🚀 Starting Streamlit application...")
        os.system("streamlit run app.py")


if __name__ == "__main__":
    main()
