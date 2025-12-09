"""
Utils Package - Toonify Image Processing
Initialization file for the utils module
"""

# Import authentication utilities
from .auth import (
    init_session_state,
    is_logged_in,
    login_user,
    logout_user
)

# Import database utilities
from .database import Database

# Import validators
from .validators import (
    validate_name,
    validate_email,
    validate_age,
    validate_mobile,
    validate_city,
    validate_password
)

# Import image processing
from .image_processor import ImageProcessor

# Import individual style processors
from .Hayao import apply_hayao_style
from .Shinkai import apply_shinkai_style
from .Paprika import apply_paprika_style
from .ghibli import apply_ghibli_style
from .cartoon import apply_cartoon_filter

# Optional: Import animegan_processor if you're using it
try:
    from .animegan_processor import AnimeGANManager, ONNXAnimeGAN, PyTorchAnimeGAN
    ANIMEGAN_AVAILABLE = True
except ImportError:
    ANIMEGAN_AVAILABLE = False
    print("⚠️ AnimeGAN processor not available")

__all__ = [
    # Auth
    'init_session_state',
    'is_logged_in',
    'login_user',
    'logout_user',
    
    # Database
    'Database',
    
    # Validators
    'validate_name',
    'validate_email',
    'validate_age',
    'validate_mobile',
    'validate_city',
    'validate_password',
    
    # Image Processing
    'ImageProcessor',
    'apply_hayao_style',
    'apply_shinkai_style',
    'apply_paprika_style',
    'apply_ghibli_style',
    'apply_cartoon_filter',
]

# Add AnimeGAN to exports if available
if ANIMEGAN_AVAILABLE:
    __all__.extend(['AnimeGANManager', 'ONNXAnimeGAN', 'PyTorchAnimeGAN'])

__version__ = '1.0.0'
__author__ = 'Prem Kumar'