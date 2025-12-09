"""
Toonify: The Art of Cartooning Images
Main Streamlit Application - FIXED FOR STREAMLIT 1.31.0

FLOW: Landing Page → Login Page → Dashboard → Logout → Login Page
"""


import streamlit as st
from utils.auth import init_session_state, is_logged_in, logout_user
from utils.database import Database
from utils.validators import *
from utils.image_processor import ImageProcessor
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

# =============================================================================
# GLOBAL CSS STYLES (FIXED - Profile & Change Password Box Colors)
# =============================================================================
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
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
    
    /* FIXED: Form styling matching login page */
    .stForm {
        background: rgba(255, 255, 255, 0.95) !important;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
    }
    
    /* FIXED: Input fields - dark text on white background */
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
    
    /* FIXED: Labels - dark text */
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
    
    /* FIXED: Info box for profile (white background like login) */
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
    
    /* Buttons */
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
    
    /* Sidebar styling */
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
    
    /* Download button */
    .stDownloadButton>button {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        border-radius: 25px;
        font-weight: bold;
    }
    
    /* Hero and feature sections */
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
    
    /* Fix for markdown text in forms */
    .stMarkdown p {
        color: inherit;
    }
    
    /* Fix for expander */
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.1);
        color: #333333;
    }
    
    /* Fix for error/success/info messages */
    .stAlert {
        background-color: rgba(255, 255, 255, 0.95);
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
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

# Auto-redirect logged-in users to dashboard
if is_logged_in() and st.session_state.page in ["landing", "login", "register"]:
    st.session_state.page = "dashboard"
    st.rerun()

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
# 🏠 LANDING PAGE
# =============================================================================
if st.session_state.page == "landing":
    
    st.markdown("<div class='main-header'>Toonify - AI Cartoon Generator</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Turn your photos into stunning cartoon-style artwork!</div>", unsafe_allow_html=True)
    
    # FIXED: Removed gap parameter (not available in 1.31.0)
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
            Phone: <b>+91 1234567890</b> &nbsp; | &nbsp;
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
# 🎨 DASHBOARD PAGE
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
        
        if st.button("🔐 Change Password", use_container_width=True):
            st.session_state.show_change_password = True
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
            st.session_state.page = "login"
            st.rerun()
    
    # Show Profile Modal (FIXED STYLING)
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
    
    # Show Change Password Modal (FIXED STYLING)
    if st.session_state.get('show_change_password', False):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("## 🔐 Change Password")
            
            with st.form("change_password_form"):
                current_password = st.text_input("Current Password", type="password")
                new_password = st.text_input("New Password", type="password")
                confirm_password = st.text_input("Confirm New Password", type="password")
                
                with st.expander("📋 Password Requirements"):
                    st.markdown("""
                    - Minimum 8 characters
                    - At least one uppercase, lowercase, number, special character
                    """)
                
                col_submit, col_cancel = st.columns(2)
                
                with col_submit:
                    submit = st.form_submit_button("Update Password", use_container_width=True)
                
                with col_cancel:
                    cancel = st.form_submit_button("Cancel", use_container_width=True)
                
                if submit:
                    if not all([current_password, new_password, confirm_password]):
                        st.error("❌ Please fill in all fields")
                    elif new_password != confirm_password:
                        st.error("❌ New passwords do not match")
                    else:
                        valid, msg = validate_password(new_password)
                        if not valid:
                            st.error(f"❌ {msg}")
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
    
    # Main Dashboard Content
    st.markdown('<h1 class="main-header">🎨 Toonify Dashboard</h1>', unsafe_allow_html=True)
    st.markdown(f"## Welcome back, {user['name']}! 👋")
    
    st.markdown("---")
    
    # Initialize Image Processor
    if 'processor' not in st.session_state:
        with st.spinner("🔄 Loading AI models..."):
            try:
                st.session_state.processor = ImageProcessor()
                available_effects = st.session_state.processor.get_available_effects()
                st.success(f"✅ Loaded {len(available_effects)} effects!")
            except Exception as e:
                st.error(f"❌ Error loading models: {e}")
                st.info("⚠️ Some AI models may not be available. OpenCV effects will still work.")
    
    processor = st.session_state.processor
    available_effects = processor.get_available_effects()
    
    # Create user directories
    user_dir = f"data/user_images/{user['email'].replace('@', '_').replace('.', '_')}"
    original_dir = f"{user_dir}/original"
    cartoonized_dir = f"{user_dir}/cartoonized"
    
    os.makedirs(original_dir, exist_ok=True)
    os.makedirs(cartoonized_dir, exist_ok=True)
    
    # ═══════════════════════════════════════════════════════════════
    # UPLOAD & PROCESS SECTION
    # ═══════════════════════════════════════════════════════════════
    
    st.markdown("## 🖼️ Upload and Transform Your Image")
    
    uploaded_file = st.file_uploader(
        "Choose an image...", 
        type=['jpg', 'jpeg', 'png', 'bmp'],
        help="Upload an image to apply Anime/Cartoon Effects"
    )
    
    if uploaded_file is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📷 Original Image")
            image = Image.open(uploaded_file)
            st.image(image, use_column_width=True)
        
        with col2:
            st.markdown("### 🎨 Select Effect")
            
            effect = st.selectbox(
                "Choose Effect",
                available_effects,
                help="Select an effect to apply to your image"
            )
            
            # Effect descriptions
            effect_descriptions = {
                "Hayao": "🌿 Soft, watercolor Ghibli-style animation (Miyazaki)",
                "Shinkai": "✨ Vibrant, cinematic lighting (Your Name style)",
                "Paprika": "🎨 Surreal, dreamlike anime art (Satoshi Kon)",
                "Ghibli Style": "🏯 Studio Ghibli anime transformation",
                "Classic Cartoon": "🎪 Traditional cartoon effect with bold outlines",
                "Sketch": "✏️ Black and white pencil sketch",
                "Pencil Color": "🖍️ Colored pencil drawing effect",
                "Oil Painting": "🖌️ Oil painting texture and style"
            }
            
            st.info(f"ℹ️ {effect_descriptions.get(effect, 'Transform your image')}")
            
            if st.button("✨ Apply Effect", use_container_width=True, type="primary"):
                with st.spinner(f"🔄 Applying {effect} effect..."):
                    try:
                        # Convert PIL to OpenCV
                        img_array = np.array(image)
                        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                        
                        # Process image
                        result = processor.process_image(img_bgr, effect)
                        
                        # Convert back to RGB
                        result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
                        result_pil = Image.fromarray(result_rgb)
                        
                        # Save images with timestamp
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        original_path = f"{original_dir}/original_{timestamp}.png"
                        cartoonized_path = f"{cartoonized_dir}/cartoon_{effect.replace(' ', '_')}_{timestamp}.png"
                        
                        image.save(original_path)
                        cv2.imwrite(cartoonized_path, result)
                        
                        # Store in session
                        st.session_state.processed_image = result_pil
                        st.session_state.processed_path = cartoonized_path
                        st.session_state.effect_applied = effect
                        
                        st.success(f"✅ {effect} effect applied successfully!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error processing image: {str(e)}")
                        st.info("💡 Tip: If using anime styles, make sure models are downloaded")
        # Display processed image if available
        if 'processed_image' in st.session_state:
            st.markdown("---")
            st.markdown("## 🎉 Result")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📷 Original")
                st.image(image, use_column_width=True)
            
            with col2:
                st.markdown(f"### 🎨 {st.session_state.effect_applied}")
                st.image(st.session_state.processed_image, use_column_width=True)
                
                # Download button
                try:
                    with open(st.session_state.processed_path, 'rb') as file:
                        st.download_button(
                            label="💾 Download Result",
                            data=file,
                            file_name=f"toonify_{st.session_state.effect_applied.lower().replace(' ', '_')}.png",
                            mime="image/png",
                            use_container_width=True,
                            type="primary"
                        )
                except Exception as e:
                    st.error(f"Error loading download file: {e}")
            
            # Clear result button
            if st.button("🗑️ Clear Result & Upload New Image"):
                del st.session_state.processed_image
                del st.session_state.processed_path
                del st.session_state.effect_applied
                st.rerun()
    
    # ═══════════════════════════════════════════════════════════════
    # PREVIOUS EDITS GALLERY
    # ═══════════════════════════════════════════════════════════════
    
    st.markdown("---")
    st.markdown("### 📚 Your Previous Edits")
    
    if os.path.exists(cartoonized_dir):
        cartoon_files = sorted(
            [f for f in os.listdir(cartoonized_dir) if f.endswith(('.png', '.jpg', '.jpeg'))],
            reverse=True
        )
        
        if cartoon_files:
            # Show last 6 images
            cols = st.columns(3)
            for idx, file in enumerate(cartoon_files[:6]):
                with cols[idx % 3]:
                    img_path = f"{cartoonized_dir}/{file}"
                    try:
                        img = Image.open(img_path)
                        st.image(img, caption=file, use_column_width=True)
                        
                        # Download button for each
                        with open(img_path, 'rb') as f:
                            st.download_button(
                                label="⬇️ Download",
                                data=f,
                                file_name=file,
                                mime="image/png",
                                key=f"download_{file}",
                                use_container_width=True
                            )
                    except Exception as e:
                        st.error(f"Error loading {file}")
        else:
            st.info("📭 No previous edits found. Start by uploading and processing an image!")
    else:
        st.info("📭 No previous edits found. Start by uploading and processing an image!")

# =============================================================================
# DEFAULT FALLBACK (Should not reach here)
# =============================================================================
else:
    if is_logged_in():
        st.session_state.page = "dashboard"
    else:
        st.session_state.page = "landing"
    st.rerun()