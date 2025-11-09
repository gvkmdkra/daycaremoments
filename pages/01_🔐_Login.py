"""Login and Registration Page"""

import streamlit as st
from app.utils.auth import authenticate_user, register_user, hash_password, verify_password
from app.database import get_db
from app.database.models import Daycare, User
from datetime import datetime
from app.utils.ui_theme import apply_professional_theme

st.set_page_config(page_title="Login - DaycareMoments", page_icon="🔐", layout="centered")

# Apply professional theme
apply_professional_theme()

st.title("🔐 Login / Register")

# Tabs for login and registration
tab1, tab2 = st.tabs(["🔓 Login", "📝 Register"])

# ===== LOGIN TAB =====
with tab1:
    st.subheader("Login to Your Account")

    with st.form("login_form"):
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("🚀 Login", use_container_width=True)

        if submit:
            if not email or not password:
                st.error("Please enter both email and password")
            else:
                # Authenticate and extract user data in one session
                with get_db() as db:
                    user = db.query(User).filter(
                        User.email == email,
                        User.is_active == True
                    ).first()

                    if user and verify_password(password, user.password_hash):
                        # Extract all data while in session
                        user_data = {
                            'id': user.id,
                            'email': user.email,
                            'first_name': user.first_name,
                            'last_name': user.last_name,
                            'role': user.role.value,
                            'daycare_id': user.daycare_id
                        }

                        # Update last login
                        user.last_login = datetime.utcnow()
                        db.commit()

                        # Store in session
                        st.session_state.user_id = user_data['id']
                        st.session_state.email = user_data['email']
                        st.session_state.first_name = user_data['first_name']
                        st.session_state.last_name = user_data['last_name']
                        st.session_state.role = user_data['role']
                        st.session_state.daycare_id = user_data['daycare_id']

                        st.success(f"✅ Welcome back, {user_data['first_name']}!")
                        st.balloons()

                        # Redirect based on role
                        if user_data['role'] == "parent":
                            st.info("Redirecting to Parent Portal...")
                            st.switch_page("pages/02_👪_Parent_Portal.py")
                        elif user_data['role'] == "staff":
                            st.info("Redirecting to Staff Dashboard...")
                            st.switch_page("pages/03_👨‍🏫_Staff_Dashboard.py")
                        elif user_data['role'] == "admin":
                            st.info("Redirecting to Admin Panel...")
                            st.switch_page("pages/04_⚙️_Admin_Panel.py")
                    else:
                        st.error("❌ Invalid email or password")

# ===== REGISTRATION TAB =====
with tab2:
    st.subheader("Create New Account")

    with st.form("register_form"):
        col1, col2 = st.columns(2)

        with col1:
            reg_first_name = st.text_input("First Name")
            reg_email = st.text_input("Email")
            reg_password = st.text_input("Password", type="password")

        with col2:
            reg_last_name = st.text_input("Last Name")
            reg_phone = st.text_input("Phone (optional)")
            reg_password_confirm = st.text_input("Confirm Password", type="password")

        reg_role = st.selectbox("I am a...", ["Parent", "Staff", "Admin"])

        # Daycare selection (simplified - in production, this would be invitation-based)
        with get_db() as db:
            daycares_db = db.query(Daycare).filter(Daycare.is_active == True).all()
            # Extract data while in session
            daycare_options = {d.name: d.id for d in daycares_db} if daycares_db else {}

        if daycare_options:
            selected_daycare = st.selectbox("Select Daycare", options=list(daycare_options.keys()))
            daycare_id = daycare_options[selected_daycare]
        else:
            st.warning("No daycares available. Creating demo daycare...")
            # Create demo daycare
            with get_db() as db:
                demo_daycare = Daycare(
                    name="Demo Daycare",
                    email="demo@daycare.com",
                    license_number="DEMO-001"
                )
                db.add(demo_daycare)
                db.commit()
                daycare_id = demo_daycare.id
                st.success("Demo daycare created!")

        agree_terms = st.checkbox("I agree to the Terms of Service and Privacy Policy")

        submit_register = st.form_submit_button("📝 Create Account", use_container_width=True)

        if submit_register:
            # Validation
            if not all([reg_first_name, reg_last_name, reg_email, reg_password]):
                st.error("Please fill in all required fields")
            elif reg_password != reg_password_confirm:
                st.error("Passwords do not match")
            elif len(reg_password) < 6:
                st.error("Password must be at least 6 characters")
            elif not agree_terms:
                st.error("Please agree to the Terms of Service")
            else:
                user, error = register_user(
                    email=reg_email,
                    password=reg_password,
                    first_name=reg_first_name,
                    last_name=reg_last_name,
                    role=reg_role.lower(),
                    daycare_id=daycare_id,
                    phone=reg_phone
                )

                if user:
                    st.success("✅ Account created successfully!")
                    st.info("Please login using the Login tab")
                    st.balloons()
                else:
                    st.error(f"❌ Registration failed: {error}")

st.divider()

# Demo credentials
with st.expander("🔍 Demo Credentials"):
    st.markdown("""
    **For Testing:**

    **Parent Account:**
    - Email: parent@demo.com
    - Password: parent123

    **Staff Account:**
    - Email: staff@demo.com
    - Password: staff123

    **Admin Account:**
    - Email: admin@demo.com
    - Password: admin123

    *Note: These accounts will be created automatically on first run*
    """)
