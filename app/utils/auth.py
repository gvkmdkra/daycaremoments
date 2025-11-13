"""Authentication utilities"""
import bcrypt
import streamlit as st
from app.database import get_db
from app.database.models import User


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def authenticate_user(email: str, password: str):
    """Authenticate user with email and password - returns dict to avoid session issues"""
    with get_db() as db:
        user = db.query(User).filter(User.email == email).first()
        if user and verify_password(password, user.password_hash):
            # Return dict to avoid detached instance errors
            return {
                'id': user.id,
                'email': user.email,
                'role': user.role,
                'organization_id': user.organization_id
            }
    return None


def register_user(email: str, password: str, role: str, organization_id: str):
    """Register new user - returns dict to avoid session issues"""
    with get_db() as db:
        # Check if user exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            return None, "Email already registered"

        # Create user
        user = User(
            email=email,
            password_hash=hash_password(password),
            role=role,
            organization_id=organization_id
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        # Return dict to avoid detached instance errors
        user_dict = {
            'id': user.id,
            'email': user.email,
            'role': user.role,
            'organization_id': user.organization_id
        }

        return user_dict, None


def get_current_user():
    """Get current logged-in user from session"""
    if 'user_id' in st.session_state:
        return {
            'id': st.session_state.get('user_id'),
            'email': st.session_state.get('email'),
            'role': st.session_state.get('role'),
            'organization_id': st.session_state.get('organization_id')
        }
    return None


def require_auth(allowed_roles=None):
    """Require authentication"""
    if 'user_id' not in st.session_state:
        st.error("⛔ Please login to access this page")
        st.stop()

    if allowed_roles and st.session_state.get('role') not in allowed_roles:
        st.error(f"⛔ This page requires {', '.join(allowed_roles)} role")
        st.stop()

    return get_current_user()


def logout():
    """Logout current user"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
