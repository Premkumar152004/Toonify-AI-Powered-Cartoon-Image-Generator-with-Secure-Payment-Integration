"""
Authentication utilities for session management
"""
import streamlit as st

def init_session_state():
    """Initialize session state variables"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'

def login_user(user_data):
    """Login user and store data in session"""
    st.session_state.logged_in = True
    st.session_state.user_data = user_data

def logout_user():
    """Logout user and clear session"""
    st.session_state.logged_in = False
    st.session_state.user_data = None
    # Clear any cached data
    if 'processed_image' in st.session_state:
        del st.session_state.processed_image
    if 'processed_path' in st.session_state:
        del st.session_state.processed_path
    if 'effect_applied' in st.session_state:
        del st.session_state.effect_applied

def is_logged_in():
    """Check if user is logged in"""
    return st.session_state.get('logged_in', False)

def get_current_user():
    """Get current user data"""
    return st.session_state.get('user_data', None)