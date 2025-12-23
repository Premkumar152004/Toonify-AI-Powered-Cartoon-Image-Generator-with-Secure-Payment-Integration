"""
Toonify: The Art of Cartooning Images
"""
import streamlit as st
import time
from utils.auth import init_session_state, is_logged_in, logout_user
from utils.database import Database
from utils.validators import *
from utils.image_processor import ImageProcessor
from payment_system.payment_gateway import render_payment_gateway
from admin_dashboard import render_admin_dashboard

import os
from PIL import Image
import cv2
import numpy as np
from datetime import datetime
import base64

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="Toonify - Cartoon Image Generator",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
    /* ===== STREAMLIT ALERTS ONLY ===== */

    /* Error */
    div[data-testid="stAlert"][data-alert-type="error"] {
        background: rgba(220, 53, 69, 0.85) !important;
        color: white !important;
    }

    /* Warning */
    div[data-testid="stAlert"][data-alert-type="warning"] {
        background: rgba(255, 193, 7, 0.85) !important;
        color: white !important;
    }

    /* Success */
    div[data-testid="stAlert"][data-alert-type="success"] {
        background: rgba(25, 135, 84, 0.85) !important;
        color: white !important;
    }

    /* Info */
    div[data-testid="stAlert"][data-alert-type="info"] {
        background: rgba(13, 110, 253, 0.85) !important;
        color: white !important;
    }

    /* Alert text */
    div[data-testid="stAlert"] p {
        color: white !important;
        font-weight: 600;
        font-size: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =============================================================================
# HELPER FUNCTION FOR IMAGE ENCODING
# =============================================================================
def image_to_base64(img_path):
    """Convert image to base64 for HTML display"""
    try:
        with open(img_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

# =============================================================================
# DYNAMIC BACKGROUND FUNCTION - WITH BRIGHTNESS/CONTRAST CONTROL
# =============================================================================
def set_page_background(page_name):
    """Set unique background for each page with brightness and contrast control"""
    
    # Define background images for each page
    backgrounds = {
        "landing": None,  # Landing uses basic colors (no image)
        "login": "assets/backgrounds/login_bg.png",
        "register": "assets/backgrounds/register_bg.png",
        "admin_login": "assets/backgrounds/admin_bg.png",
        "dashboard": "assets/backgrounds/dashboard_bg.jpg",
        "admin_dashboard": "assets/backgrounds/admin_dashboard_bg.jpg",
        "payment": "assets/backgrounds/payment_bg.png",
    }
    
    # ADJUST THESE VALUES TO CONTROL BRIGHTNESS AND CONTRAST
    page_settings = {
        "login": {
            "brightness": 0.7,
            "contrast": 1.2,
            "blur": 0,
            "overlay": 0.3
        },
        "register": {
            "brightness": 0.75,
            "contrast": 1.1,
            "blur": 0,
            "overlay": 0.2
        },
        "admin_login": {
            "brightness": 0.6,
            "contrast": 1.3,
            "blur": 0,
            "overlay": 0.4
        },
        "dashboard": {
            "brightness": 0.8,
            "contrast": 1.0,
            "blur": 2,
            "overlay": 0.2
        },
        "admin_dashboard": {
            "brightness": 0.65,
            "contrast": 1.25,
            "blur": 0,
            "overlay": 0.35
        },
        "payment": {
            "brightness": 0.7,
            "contrast": 1.2,
            "blur": 0,
            "overlay": 0.3
        }
    }
    
    # Get background for current page
    bg_image_path = backgrounds.get(page_name)
    settings = page_settings.get(page_name, {
        "brightness": 1.0,
        "contrast": 1.0,
        "blur": 0,
        "overlay": 0
    })
    
    if page_name == "landing" or bg_image_path is None:
        # Landing page uses basic gradient colors
        st.markdown("""
            <style>
            .stApp {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            </style>
        """, unsafe_allow_html=True)
    else:
        # Other pages use their specific background image with effects
        bg_base64 = image_to_base64(bg_image_path)
        if bg_base64:
            st.markdown(f"""
                <style>
                /* Background image layer */
                .stApp::before {{
                    content: "";
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background-image: url("data:image/jpeg;base64,{bg_base64}");
                    background-size: cover;
                    background-position: center;
                    background-repeat: no-repeat;
                    background-attachment: fixed;
                    filter: brightness({settings['brightness']}) 
                            contrast({settings['contrast']}) 
                            blur({settings['blur']}px);
                    z-index: -2;
                }}
                
                /* Dark overlay layer */
                .stApp::after {{
                    content: "";
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0, 0, 0, {settings['overlay']});
                    z-index: -1;
                }}
                
                /* Ensure .stApp itself is transparent */
                .stApp {{
                    background: transparent !important;
                }}
                </style>
            """, unsafe_allow_html=True)
        else:
            # Fallback if image not found
            st.markdown("""
                <style>
                .stApp {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }
                </style>
            """, unsafe_allow_html=True)

# =============================================================================
# GLOBAL CSS STYLES
# =============================================================================
st.markdown("""
    <style>
    .main-header {
        font-size: 3.5rem;
        font-weight: bold;
        background: linear-gradient(120deg, #FF6B6B, #FFE66D, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
        animation: fadeIn 0.8s ease-out;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #FFE66D;
        text-align: center;
        padding-bottom: 2rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    
    .stForm {
        background: rgba(255, 255, 255, 0.95) !important;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
    }
    
    .stTextInput>div>div>input, 
    .stNumberInput>div>div>input, 
    .stSelectbox>div>div>select {
        border-radius: 10px;
        border: 2px solid #E0E0E0 !important;
        transition: all 0.3s ease;
        background-color: white !important;
        color: #000000 !important;
    }
    
    .stTextInput>div>div>input:focus, 
    .stNumberInput>div>div>input:focus, 
    .stSelectbox>div>div>select:focus {
        border-color: #667eea !important;
        background-color: white !important;
        color: #000000 !important;
        box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
    }
    
    .stSelectbox>div>div>select option {
        background-color: white !important;
        color: #000000 !important;
    }
    
    .stTextInput>label, 
    .stNumberInput>label, 
    .stSelectbox>label {
        color: #333333 !important;
        font-weight: 500;
    }
    
    .stForm label {
        color: #333333 !important;
    }
    
    input[type="password"] {
        background-color: white !important;
        color: #000000 !important;
    }
    
    .info-box {
        padding: 2rem;
        border-radius: 20px;
        background: rgba(255, 255, 255, 0.95) !important;
        color: #333333 !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
    }
    
    .info-box h3 {
        color: #333333 !important;
        margin: 0.8rem 0;
        padding: 0.5rem;
        border-bottom: 2px solid #E0E0E0;
    }
    
    .info-box h3 strong {
        color: #667eea !important;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    [data-testid="stSidebar"] .stMarkdown {
        color: white;
    }
    [data-testid="stSidebar"] .stButton>button {
        background: rgba(255, 255, 255, 0.2);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    [data-testid="stSidebar"] .stButton>button:hover {
        background: rgba(255, 255, 255, 0.3);
    }
    
    .stDownloadButton>button {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        border-radius: 25px;
        font-weight: bold;
    }
    
    .hero-sub {
        font-size: 22px;
        text-align: center;
        color: #f8f8f8;
        margin-top: -10px;
        animation: fadeIn 1.5s ease-in-out;
    }
    .feature-card {
        background: rgba(255,255,255,0.15);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        color: white;
        backdrop-filter: blur(8px);
        transition: 0.3s;
        animation: fadeInUp 1s ease-in-out;
    }
    .feature-card:hover {
        transform: translateY(-8px);
        background: rgba(255,255,255,0.25);
    }
    .section-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: white;
        margin-bottom: 1rem;
    }
    .section-text {
        font-size: 1.2rem;
        color: #f0f0f0;
        line-height: 1.6;
    }
    .footer {
        width: 100%;
        padding: 25px 0;
        background: rgba(0,0,0,0.45);
        text-align: center;
        color: white;
        font-size: 18px;
        font-weight: 500;
        backdrop-filter: blur(8px);
        margin-top: 50px;
        border-top: 1px solid rgba(255,255,255,0.2);
    }
    .footer b {
        color: #ffd700;
        font-size: 19px;
    }
    
    .stMarkdown p {
        color: inherit;
    }
    
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.1);
        color: #333333;
    }
    
    .stAlert {
        background-color: rgba(255, 255, 255, 0.95);
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Card number formatting */
    .card-number-input {
        letter-spacing: 3px;
        font-family: monospace;
    }
    </style>
""", unsafe_allow_html=True)

# =============================================================================
# INITIALIZE SESSION STATE & DATABASE
# =============================================================================
init_session_state()
db = Database()

# Initialize page routing
if "page" not in st.session_state:
    if is_logged_in():
        st.session_state.page = "dashboard"
    else:
        st.session_state.page = "landing"

# Initialize payment state
if "show_payment" not in st.session_state:
    st.session_state.show_payment = False

if "payment_image_path" not in st.session_state:
    st.session_state.payment_image_path = None

# Auto-redirect logged-in users to dashboard
if is_logged_in() and st.session_state.page in ["landing", "login", "register"]:
    st.session_state.page = "dashboard"
    st.rerun()

# =============================================================================
# SET BACKGROUND BASED ON CURRENT PAGE
# =============================================================================
set_page_background(st.session_state.page)

# =============================================================================
# 🏠 LANDING PAGE
# =============================================================================
if st.session_state.page == "landing":
    
    st.markdown("<div class='main-header'>Toonify - AI Cartoon Generator</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Turn your photos into stunning cartoon-style artwork!</div>", unsafe_allow_html=True)
    
    col_left, col_center, col_right = st.columns([4, 4, 1])
    with col_right:
        if st.button("Login →", key="landing_login"):
            st.session_state.page = "login"
            st.rerun()

    st.markdown("<h2 class='hero-sub'>Transform real images into beautiful cartoon art instantly!</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
            <div class='feature-card'>
                🎨<br><b>AI Cartoon Effect</b><br>
                Turn your images into cartoon masterpieces instantly.
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class='feature-card'>
                ⚡<br><b>Fast Processing</b><br>
                Experience quick and efficient transformation.
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div class='feature-card'>
                🛡️<br><b>Secure</b><br>
                Your photos stay private and safe.
            </div>
        """, unsafe_allow_html=True)
    
    st.divider()

    col1, col2 = st.columns([1, 1.5])
    with col1:
        try:
            st.image(Image.open("assets/landing/prem.png"), use_column_width=True)
        except:
            st.info("📷 Image: assets/landing/prem.png")
    with col2:
        st.markdown("""
            <div>
                <h1 class="section-title">Cartoonify an Image in One Go</h1>
                <h2 class="section-text">
                    Apply cartoon photo effects in seconds using AI! 
                    Convert your photos into amazing cartoon art instantly.
                </h2>
            </div>
        """, unsafe_allow_html=True)
    
    st.divider()

    col3, col4 = st.columns([1.5, 1])
    with col3:
        st.markdown("""
            <div>
                <h1 class="section-title">Cartoon Yourself for Charming Portraits</h1>
                <h2 class="section-text">
                    Make your portrait pictures look beautiful with multiple cartoon styles. 
                    Choose anime, 3D, sketch, or creative filters!
                </h2>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        try:
            st.image(Image.open("assets/landing/portrait.png"), use_column_width=True)
        except:
            st.info("📷 Image: assets/landing/portrait.png")
    
    st.divider()

    col5, col6 = st.columns([1, 1.5])
    with col5:
        try:
            st.image(Image.open("assets/landing/cartoon.png"), use_column_width=True)
        except:
            st.info("📷 Image: assets/landing/cartoon.png")
    with col6:
        st.markdown("""
            <div>
                <h1 class="section-title">Cartoonize Photos for Your Pets</h1>
                <h2 class="section-text">
                    Turn your cute pets into adorable cartoon characters. 
                    Perfect for pet lovers who want fun and unique artwork.
                </h2>
            </div>
        """, unsafe_allow_html=True)
    
    st.divider()

    col7, col8 = st.columns([1.5, 1])
    with col7:
        st.markdown("""
            <div>
                <h1 class="section-title">Elevate Your Landscape with Cartoon Maker</h1>
                <h2 class="section-text">
                    Convert landscape photos into vibrant cartoon artworks using AI filters. 
                    Create professional-style artwork with ease.
                </h2>
            </div>
        """, unsafe_allow_html=True)
    with col8:
        try:
            st.image(Image.open("assets/landing/difstyle.png"), use_column_width=True)
        except:
            st.info("📷 Image: assets/landing/difstyle.png")
    
    st.divider()

    st.markdown("# ⭐ Why Choose Our AI Cartoon Generator?")
    
    img_base64 = image_to_base64("assets/picc.jpg")
    if img_base64:
        st.markdown(f"""
            <div style="text-align:center; margin:30px 0;">
                <img src="data:image/jpeg;base64,{img_base64}" 
                     style="width:100%; height:550px; object-fit:cover; border-radius:15px; box-shadow: 0 8px 25px rgba(0,0,0,0.3);"/>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("📷 Feature Image: assets/picc.jpg")
    
    st.divider()
    
    col_left, col_center, col_right = st.columns([3, 2, 3])
    with col_center:
        if st.button("🚀 Get Started Now", use_container_width=True, key="get_started_btn"):
            st.session_state.page = "login"
            st.rerun()

    st.markdown("""
        <div class="footer">
            Created by <b>Prem Kumar</b> &nbsp; | &nbsp;
            Email: <b>raviprem.2004@gmail.com</b> &nbsp; | &nbsp;
            Phone: <b>+91 8248070047</b> &nbsp; | &nbsp;
            © 2025 Toonify - All Rights Reserved
        </div>
    """, unsafe_allow_html=True)
    
    st.stop()

# =============================================================================
# 🔐 LOGIN PAGE
# =============================================================================
elif st.session_state.page == 'login' and not is_logged_in():
    
    st.markdown('<h1 class="main-header">🎨 Toonify</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">Transform Your Images into Cartoons</h2>', unsafe_allow_html=True)
    
    if st.button("← Back to Home", key="back_to_landing"):
        st.session_state.page = "landing"
        st.rerun()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("## 🔐 Login to Your Account")
        
        with st.form("login_form"):
            email = st.text_input("📧 Email", placeholder="example@gmail.com")
            password = st.text_input("🔒 Password", type="password")
            
            col_login, col_register = st.columns(2)
            
            with col_login:
                submit = st.form_submit_button("Login", use_container_width=True)
            
            with col_register:
                register = st.form_submit_button("Create Account", use_container_width=True)
            
            if submit:
                if not email or not password:
                    st.error("❌ Please fill in all fields")
                else:
                    success, result = db.authenticate_user(email, password)
                    if success:
                        from utils.auth import login_user
                        login_user(result)
                        st.success("✅ Login successful!")
                        st.session_state.page = "dashboard"
                        st.rerun()
                    else:
                        st.error(f"❌ {result}")
            
            if register:
                st.session_state.page = 'register'
                st.rerun()
    
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if st.button("👨‍💼 Admin Login", use_container_width=True, type="secondary"):
            st.session_state.page = "admin_login"
            st.rerun()
    
    st.stop()

# =============================================================================
# 👨‍💼 ADMIN LOGIN PAGE
# =============================================================================
elif st.session_state.page == 'admin_login':

    st.markdown('<h1 class="main-header">👨‍💼 Admin Login</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">Toonify Administration Portal</h2>', unsafe_allow_html=True)

    if st.button("← Back to User Login"):
        st.session_state.page = "login"
        st.rerun()

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("## 🔐 Admin Access")

        with st.form("admin_login_form"):
            email = st.text_input("📧 Admin Email", placeholder="admin@toonify.com")
            password = st.text_input("🔒 Admin Password", type="password")

            submit = st.form_submit_button(
                "Login as Admin",
                use_container_width=True,
                type="primary"
            )

            if submit:
                if not email or not password:
                    st.error("❌ Please fill in all fields")
                else:
                    success, result = db.authenticate_admin(email, password)
                    if success:
                        from utils.auth import login_user
                        login_user(result)
                        st.success("✅ Admin login successful!")
                        st.session_state.page = "admin_dashboard"
                        st.rerun()
                    else:
                        st.error(f"❌ {result}")

        st.info("ℹ️ Default: admin@toonify.com / Admin@123")

    st.stop()

# =============================================================================
# 📊 ADMIN DASHBOARD PAGE
# =============================================================================
elif st.session_state.page == 'admin_dashboard' and is_logged_in():

    if st.session_state.user_data.get("is_admin"):
        render_admin_dashboard()
    else:
        st.error("❌ Unauthorized access")
        st.session_state.page = "dashboard"
        st.rerun()

    st.stop()

# =============================================================================
# 📝 REGISTRATION PAGE
# =============================================================================
elif st.session_state.page == 'register':
    
    st.markdown('<h1 class="main-header">🎨 Toonify</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">Create Your Account</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 📝 Registration Form")
        
        with st.form("registration_form"):
            name = st.text_input("👤 Full Name", placeholder="John Doe")
            email = st.text_input("📧 Email", placeholder="example@gmail.com")
            
            col_gender, col_age = st.columns(2)
            with col_gender:
                gender = st.selectbox("⚥ Gender", ["Select", "Male", "Female", "Other", "Prefer not to say"])
            with col_age:
                age = st.number_input("🎂 Age", min_value=13, max_value=120, value=18)
            
            mobile = st.text_input("📱 Mobile Number", placeholder="1234567890")
            city = st.text_input("🏙️ City", placeholder="Your City")
            
            password = st.text_input("🔒 Password", type="password", 
                                    help="Must contain: 8+ characters, uppercase, lowercase, number, special character")
            confirm_password = st.text_input("🔒 Confirm Password", type="password")
            
            with st.expander("📋 Password Requirements"):
                st.markdown("""
                - ✓ Minimum 8 characters
                - ✓ At least one uppercase letter (A-Z)
                - ✓ At least one lowercase letter (a-z)
                - ✓ At least one number (0-9)
                - ✓ At least one special character (!@#$%^&*(),.?":{}|<>)
                """)
            
            col_reg, col_back = st.columns(2)
            
            with col_reg:
                submit = st.form_submit_button("Register", use_container_width=True)
            
            with col_back:
                back = st.form_submit_button("Back to Login", use_container_width=True)
            
            if submit:
                errors = []
                
                valid, msg = validate_name(name)
                if not valid: errors.append(msg)
                
                valid, msg = validate_email(email)
                if not valid: errors.append(msg)
                
                if gender == "Select":
                    errors.append("Please select your gender")
                
                valid, msg = validate_age(age)
                if not valid: errors.append(msg)
                
                valid, msg = validate_mobile(mobile)
                if not valid: errors.append(msg)
                
                valid, msg = validate_city(city)
                if not valid: errors.append(msg)
                
                valid, msg = validate_password(password)
                if not valid: errors.append(msg)
                
                if password != confirm_password:
                    errors.append("Passwords do not match")
                
                if errors:
                    for error in errors:
                        st.error(f"❌ {error}")
                else:
                    success, message = db.create_user(name, email, password, gender, age, mobile, city)
                    if success:
                        st.success(f"✅ {message}")
                        st.info("🔄 Redirecting to login page...")
                        st.session_state.page = 'login'
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
            
            if back:
                st.session_state.page = 'login'
                st.rerun()
    
    st.stop()

# =============================================================================
# 💳 PAYMENT GATEWAY PAGE
# =============================================================================
elif st.session_state.get('show_payment', False) and is_logged_in():
    user = st.session_state.user_data
    image_path = st.session_state.payment_image_path

    # SAFETY CHECK: ensure effect is selected
    if "selected_effect" not in st.session_state:
        st.error("❌ No style selected. Please apply an effect first.")
        st.session_state.show_payment = False
        st.stop()

    effect_name = st.session_state.selected_effect
    
    # Render payment gateway
    payment_success = render_payment_gateway(
        image_path,
        user["email"],
        effect_name
    )

    if payment_success:
        st.session_state.show_payment = False
        st.session_state.payment_image_path = None
        st.session_state.selected_effect = None
        # JavaScript in payment_gateway.py handles auto-redirect after 5 seconds
        # No need for time.sleep() or rerun here

    st.stop()

# =============================================================================
# 🎨 DASHBOARD PAGE (with Gallery in Profile)
# =============================================================================
elif is_logged_in():
    
    user = st.session_state.user_data
    
    # Sidebar User Menu
    with st.sidebar:
        st.markdown("## 👤 User Profile")
        st.write(f"**Name:** {user['name']}")
        st.write(f"**Email:** {user['email']}")
        st.markdown("---")
        
        if st.button("📊 View Full Profile", use_container_width=True):
            st.session_state.show_profile = True
        
        # NEW: Gallery Button
        if st.button("🖼️ My Gallery", use_container_width=True):
            st.session_state.show_gallery = True
        
        if st.button("🔐 Change Password", use_container_width=True):
            st.session_state.show_change_password = True
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
            st.session_state.page = "login"
            st.rerun()
    
    # Show Profile Modal
    if st.session_state.get('show_profile', False):
        col1, col2, col3 = st.columns([1, 4, 1])
        with col2:
            st.markdown("## 👤 User Profile")
            st.markdown(f"""
            <div class="info-box">
                <h3><strong>Name:</strong> {user['name']}</h3>
                <h3><strong>Email:</strong> {user['email']}</h3>
                <h3><strong>Gender:</strong> {user['gender']}</h3>
                <h3><strong>Age:</strong> {user['age']}</h3>
                <h3><strong>Mobile:</strong> {user['mobile']}</h3>
                <h3><strong>City:</strong> {user['city']}</h3>
                <h3><strong>Member Since:</strong> {user.get('created_at', 'N/A')}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("← Back to Dashboard", use_container_width=True):
                st.session_state.show_profile = False
                st.rerun()
        st.stop()
    
    # NEW: Show Gallery Modal
    if st.session_state.get('show_gallery', False):
        st.markdown('<h1 class="main-header">🖼️ My Gallery</h1>', unsafe_allow_html=True)
        st.markdown('<h2 class="sub-header">Your Edited Images</h2>', unsafe_allow_html=True)
        
        if st.button("← Back to Dashboard", use_container_width=False):
            st.session_state.show_gallery = False
            st.rerun()
        
        st.markdown("---")
        
        # Get user's image history
        user_images = db.get_user_image_history(user['email'])
        
        if user_images:
            st.markdown(f"### 🎨 Total Images: {len(user_images)}")
            
            # Display images in grid
            cols_per_row = 3
            for idx in range(0, len(user_images), cols_per_row):
                cols = st.columns(cols_per_row)
                
                for col_idx, img_data in enumerate(user_images[idx:idx+cols_per_row]):
                    effect_name, image_path, amount, transaction_id, created_at = img_data
                    
                    with cols[col_idx]:
                        try:
                            if os.path.exists(image_path):
                                img = Image.open(image_path)
                                st.image(img, use_column_width=True)
                                
                                st.markdown(f"""
                                <div style="background: white; padding: 1rem; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 1rem;">
                                    <p style="color: #667eea; font-weight: bold; font-size: 1.1rem; margin: 0; text-align: center;">
                                        {effect_name}
                                    </p>
                                    <p style="color: #28a745; font-size: 1.2rem; font-weight: bold; margin: 0.3rem 0; text-align: center;">
                                        💰 ₹{amount}
                                    </p>
                                    <p style="color: #666; font-size: 0.85rem; margin: 0; text-align: center;">
                                        📅 {created_at}
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Download button for each image
                                with open(image_path, 'rb') as file:
                                    file_data = file.read()
                                    st.download_button(
                                        label="📥 Download",
                                        data=file_data,
                                        file_name=f"{effect_name}_{transaction_id[-8:]}.png",
                                        mime="image/png",
                                        key=f"download_{transaction_id}",
                                        use_container_width=True
                                    )
                            else:
                                st.warning(f"Image not found: {effect_name}")
                        except Exception as e:
                            st.error(f"Error loading image: {e}")
            
            # Total spent summary
            total_spent = sum([img[2] for img in user_images])
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
                        padding: 2rem; border-radius: 15px; text-align: center; margin-top: 2rem;">
                <p style="color: white; font-size: 2rem; font-weight: bold; margin: 0;">
                    💰 Total Spent: ₹{total_spent}
                </p>
                <p style="color: white; font-size: 1.1rem; margin-top: 0.5rem;">
                    {len(user_images)} Images Processed
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("📷 You haven't edited any images yet. Start creating your first cartoon masterpiece!")
            
            if st.button("🎨 Start Editing", use_container_width=True):
                st.session_state.show_gallery = False
                st.rerun()
        
        st.stop()
    
    # Main Dashboard - Image Editor
    st.markdown('<h1 class="main-header">🎨 Image Editor</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">Upload and transform your images</h2>', unsafe_allow_html=True)
    
    # Image upload and effect selection in two columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📤 Upload Image")
        uploaded_file = st.file_uploader("Choose an image...", type=['jpg', 'jpeg', 'png'])
        
        if uploaded_file is not None:
            # Save uploaded image
            import tempfile
            import os
            
            # Create temp directory if not exists
            temp_dir = "temp"
            os.makedirs(temp_dir, exist_ok=True)
            
            # Save uploaded file
            uploaded_path = os.path.join(temp_dir, uploaded_file.name)
            with open(uploaded_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Display uploaded image
            st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
            
            # Store in session
            st.session_state.uploaded_image_path = uploaded_path
    
    with col2:
        st.markdown("### 🎨 Select Style")
        
        # Initialize ImageProcessor
        processor = ImageProcessor()
        available_effects = processor.get_available_effects()
        
        # Display style cards with prices
        selected_effect = None
        cols = st.columns(2)
        
        for idx, effect in enumerate(available_effects):
            with cols[idx % 2]:
                # Get price for this effect
                from payment_system.payment_handler import PaymentHandler
                payment_handler = PaymentHandler()
                price = payment_handler.style_prices.get(effect, 99.00)
                
                if st.button(f"""
                **{effect}**  
                💰 ₹{price}
                """, use_container_width=True, key=f"effect_{effect}"):
                    selected_effect = effect
                    st.session_state.selected_effect = effect
        
        if selected_effect:
            st.success(f"✅ Selected: {selected_effect}")
            
            if st.session_state.get('uploaded_image_path'):
                # Process image
                with st.spinner(f"🔄 Applying {selected_effect} style..."):
                    try:
                        # Load and process image
                        import cv2
                        from PIL import Image
                        
                        # Read image
                        img = cv2.imread(st.session_state.uploaded_image_path)
                        
                        # Process with selected effect
                        result = processor.process_image(img, selected_effect)
                        
                        # Save processed image
                        import time
                        timestamp = int(time.time())
                        output_path = f"temp/processed_{timestamp}.png"
                        cv2.imwrite(output_path, result)
                        
                        # Store in session
                        st.session_state.processed_image = result
                        st.session_state.processed_path = output_path
                        st.session_state.effect_applied = selected_effect
                        
                        st.success("✅ Style applied successfully!")
                        
                    except Exception as e:
                        st.error(f"❌ Error processing image: {e}")
    
    # Display processed image if available
    if st.session_state.get('processed_image') is not None:
        st.markdown("---")
        st.markdown("### 🖼️ Result")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.get('uploaded_image_path'):
                st.image(st.session_state.uploaded_image_path, caption="Original", use_column_width=True)
        
        with col2:
            st.image(st.session_state.processed_path, caption=f"{st.session_state.effect_applied} Style", use_column_width=True)
        
        # Payment button
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            # Get price for the applied effect
            from payment_system.payment_handler import PaymentHandler
            payment_handler = PaymentHandler()
            price = payment_handler.style_prices.get(st.session_state.effect_applied, 99.00)
            
            st.markdown(f"""
            <div style="background: #e8f5e8; padding: 1.5rem; border-radius: 15px; text-align: center; margin-bottom: 1.5rem; border: 2px solid #28a745;">
                <p style="color: #000000; font-size: 1.5rem; font-weight: bold; margin: 0;">
                    Amount: ₹{price}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("💳 Proceed to Payment", use_container_width=True, type="primary"):
                st.session_state.payment_image_path = st.session_state.processed_path
                st.session_state.show_payment = True
                st.rerun()
    
    # Change Password Modal
    if st.session_state.get('show_change_password', False):
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col2:
            st.markdown("## 🔐 Change Password")
            
            with st.form("change_password_form"):
                current_password = st.text_input("Current Password", type="password")
                new_password = st.text_input("New Password", type="password")
                confirm_password = st.text_input("Confirm New Password", type="password")
                
                col_submit, col_cancel = st.columns(2)
                
                with col_submit:
                    submit = st.form_submit_button("Update Password", use_container_width=True)
                
                with col_cancel:
                    cancel = st.form_submit_button("Cancel", use_container_width=True)
                
                if submit:
                    if new_password != confirm_password:
                        st.error("❌ New passwords don't match")
                    else:
                        success, message = db.update_password(user['email'], current_password, new_password)
                        if success:
                            st.success(f"✅ {message}")
                            st.session_state.show_change_password = False
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                
                if cancel:
                    st.session_state.show_change_password = False
                    st.rerun()
        
        st.stop()