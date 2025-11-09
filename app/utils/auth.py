"""Authentication utilities"""
import bcrypt
import streamlit as st
from app.database import get_db
from app.database.models import User, UserRole


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def authenticate_user(email: str, password: str):
    """Authenticate user with email and password"""
    with get_db() as db:
        user = db.query(User).filter(
            User.email == email,
            User.is_active == True
        ).first()

        if user and verify_password(password, user.password_hash):
            return user

    return None


def register_user(email: str, password: str, first_name: str, last_name: str,
                 role: str, daycare_id: str, phone: str = None):
    """Register new user"""
    with get_db() as db:
        # Check if user exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            return None, "Email already registered"

        # Create user
        user = User(
            email=email,
            password_hash=hash_password(password),
            first_name=first_name,
            last_name=last_name,
            role=UserRole[role.upper()],
            daycare_id=daycare_id,
            phone=phone
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user, None


class SessionUser:
    """User object from session state (avoids DB queries)"""
    def __init__(self):
        self.id = st.session_state.get('user_id')
        self.email = st.session_state.get('email')
        self.first_name = st.session_state.get('first_name')
        self.last_name = st.session_state.get('last_name')
        self.role = type('Role', (), {'value': st.session_state.get('role')})()
        self.daycare_id = st.session_state.get('daycare_id')


def get_current_user():
    """Get current logged-in user from session"""
    if 'user_id' in st.session_state:
        return SessionUser()
    return None


def require_auth(allowed_roles=None):
    """Decorator/function to require authentication"""
    # Check if user is logged in via session state
    if 'user_id' not in st.session_state:
        st.error("⛔ Please login to access this page")
        st.stop()

    # Check role from session state (no DB query needed)
    if allowed_roles and st.session_state.get('role') not in allowed_roles:
        st.error(f"⛔ This page requires {', '.join(allowed_roles)} role")
        st.stop()

    # Return user data from session
    return SessionUser()


def logout():
    """Logout current user"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
