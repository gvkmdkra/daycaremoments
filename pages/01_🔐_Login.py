"""Login & Registration Page"""

import streamlit as st
from app.utils.auth import authenticate_user, register_user, logout
from app.database import get_db
from app.database.models import Organization

st.set_page_config(page_title="Login - DaycareMoments", page_icon="🔐", layout="centered")

st.title("🔐 Login & Registration")

# Check if already logged in
if 'user_id' in st.session_state:
    st.success(f"Already logged in as: {st.session_state.get('email')}")
    if st.button("Logout"):
        logout()
    st.stop()

# Tabs for login and registration
tab1, tab2 = st.tabs(["Login", "Register"])

# Login Tab
with tab1:
    st.subheader("Login to Your Account")

    with st.form("login_form"):
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login", use_container_width=True)

        if submit:
            if not email or not password:
                st.error("Please enter both email and password")
            else:
                user = authenticate_user(email, password)
                if user:
                    # Store in session
                    st.session_state.user_id = user['id']
                    st.session_state.email = user['email']
                    st.session_state.role = user['role']
                    st.session_state.organization_id = user['organization_id']

                    st.success(f"✅ Logged in successfully as {user['role']}!")
                    st.balloons()

                    # Redirect based on role
                    if user['role'] == "parent":
                        st.info("Redirecting to Parent Portal...")
                        st.switch_page("pages/02_👪_Parent_Portal.py")
                    elif user['role'] == "staff":
                        st.info("Redirecting to Staff Dashboard...")
                        st.switch_page("pages/03_👨‍🏫_Staff_Dashboard.py")
                else:
                    st.error("❌ Invalid email or password")

# Registration Tab
with tab2:
    st.subheader("Create New Account")

    st.info("ℹ️ Public registration is for **Parents only**. Staff and Admin accounts must be created by administrators.")

    with st.form("register_form"):
        reg_email = st.text_input("Email", key="reg_email", placeholder="you@example.com")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        reg_password_confirm = st.text_input("Confirm Password", type="password")
        reg_role = "parent"  # Fixed to parent for public registration
        st.text_input("Role", value="Parent", disabled=True, help="Only parents can self-register")

        # Organization selection
        with get_db() as db:
            orgs = db.query(Organization).all()
            if orgs:
                org_names = {org.name: org.id for org in orgs}
                selected_org = st.selectbox("Organization", list(org_names.keys()))
                organization_id = org_names[selected_org]
            else:
                st.warning("No organizations found. Please create one first or use demo setup.")
                organization_id = None

        submit_reg = st.form_submit_button("Register", use_container_width=True)

        if submit_reg:
            if not organization_id:
                st.error("No organization available. Please contact admin.")
            elif not reg_email or not reg_password:
                st.error("Please fill in all fields")
            elif reg_password != reg_password_confirm:
                st.error("Passwords do not match")
            elif len(reg_password) < 6:
                st.error("Password must be at least 6 characters")
            else:
                user, error = register_user(reg_email, reg_password, reg_role, organization_id)
                if user:
                    st.success("✅ Registration successful! Please login.")
                    st.balloons()
                else:
                    st.error(f"❌ Registration failed: {error}")

st.divider()

# Demo credentials
with st.expander("🔍 Demo Credentials"):
    st.markdown("""
    **For Testing:**

    **Staff Account:**
    - Email: `staff@demo.com`
    - Password: `password123`

    **Parent Account:**
    - Email: `parent@demo.com`
    - Password: `password123`

    *Note: These accounts will be created automatically on first run via database seeding*
    """)
