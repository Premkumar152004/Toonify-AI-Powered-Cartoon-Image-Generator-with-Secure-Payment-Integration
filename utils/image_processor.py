"""
Image processing functions for cartoonization
Includes OpenCV effects + AnimeGAN2 styles (ONNX models)
"""
import cv2
import numpy as np
from PIL import Image
import os

# Import individual style processors
from utils.Hayao import apply_hayao_style
from utils.Shinkai import apply_shinkai_style
from utils.Paprika import apply_paprika_style
from utils.cartoon import apply_cartoon_filter
from utils.ghibli import apply_ghibli_style

class ImageProcessor:

    def __init__(self):
        """Initialize image processor with available effects"""
        print("🔄 Initializing Image Processor...")
        
        # Check which ONNX models are available
        self.onnx_styles = {
            "Hayao": "anime_models/Hayao.onnx",
            "Shinkai": "anime_models/Shinkai.onnx",
            "Paprika": "anime_models/Paprika.onnx"
        }
        
        self.available_onnx = []
        for style, path in self.onnx_styles.items():
            if os.path.exists(path):
                self.available_onnx.append(style)
                print(f"  ✅ Found {style} model")
            else:
                print(f"  ⚠️ Missing {style} model at {path}")
        
        # Check Ghibli model
        ghibli_path = "anime_models/Ghibli.onnx"
        self.ghibli_available = os.path.exists(ghibli_path)
        if self.ghibli_available:
            print(f"  ✅ Found Ghibli model")
        else:
            print(f"  ⚠️ Missing Ghibli model at {ghibli_path}")
        
        print(f"✅ Image Processor initialized with {len(self.available_onnx) + (1 if self.ghibli_available else 0)} AI models")
    
    @staticmethod
    def sketch_effect(image):
        """Pencil sketch effect"""
        try:
            img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            img_invert = cv2.bitwise_not(img_gray)
            img_blur = cv2.GaussianBlur(img_invert, (25, 25), 0)
            img_blend = cv2.bitwise_not(img_blur)
            sketch = cv2.divide(img_gray, img_blend, scale=256.0)
            return cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
        except Exception as e:
            print(f"Error in sketch_effect: {e}")
            return image
    
    @staticmethod
    def pencil_color_effect(image):
        """Colored pencil sketch effect"""
        try:
            _, img_color = cv2.pencilSketch(
                image, sigma_s=90, sigma_r=0.17, shade_factor=0.15
            )
            return img_color
        except Exception as e:
            print(f"Error in pencil_color_effect: {e}")
            return image
    
    @staticmethod
    def oil_painting_effect(image):
        """Oil painting effect"""
        try:
            smooth = cv2.bilateralFilter(image, 19, 86, 88)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 110, 210)
            edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
            return cv2.addWeighted(smooth, 1.9, edges, 0.9, 0.5)
        except Exception as e:
            print(f"Error in oil_painting_effect: {e}")
            return image
    
    def process_image(self, image, effect_type):
        """Process image with specified effect"""
        try:
            # Convert PIL Image to OpenCV format if needed
            if isinstance(image, Image.Image):
                image = np.array(image)
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # ONNX Anime Styles
            if effect_type == "Hayao" and "Hayao" in self.available_onnx:
                return apply_hayao_style(image)
            
            elif effect_type == "Shinkai" and "Shinkai" in self.available_onnx:
                return apply_shinkai_style(image)
            
            elif effect_type == "Paprika" and "Paprika" in self.available_onnx:
                return apply_paprika_style(image)
            
            elif effect_type == "Ghibli Style" and self.ghibli_available:
                return apply_ghibli_style(image)
            
            # OpenCV Effects
            elif effect_type == "Classic Cartoon":
                return apply_cartoon_filter(image)
            
            elif effect_type == "Sketch":
                return self.sketch_effect(image)
            
            elif effect_type == "Pencil Color":
                return self.pencil_color_effect(image)
            
            elif effect_type == "Oil Painting":
                return self.oil_painting_effect(image)
            
            else:
                print(f"⚠️ Effect '{effect_type}' not available or models missing")
                return image
                
        except Exception as e:
            print(f"❌ Error processing image with {effect_type}: {e}")
            import traceback
            traceback.print_exc()
            return image
    
    @staticmethod
    def save_image(image, path):
        """Save image to disk"""
        try:
            # Create directory if it doesn't exist
            dir_path = os.path.dirname(path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
            
            # Save image
            success = cv2.imwrite(path, image)
            if success:
                print(f"✅ Image saved: {path}")
            else:
                print(f"❌ Failed to save image: {path}")
            return success
        except Exception as e:
            print(f"Error saving image: {e}")
            return False
    
    def get_available_effects(self):
        """Get list of all available effects"""
        effects = []
        
        # Add ONNX anime styles that are available
        effects.extend(self.available_onnx)
        
        # Add Ghibli if available
        if self.ghibli_available:
            effects.append("Ghibli Style")
        
        # Add OpenCV effects (always available)
        opencv_effects = [
            "Classic Cartoon",
            "Sketch",
            "Pencil Color",
            "Oil Painting"
        ]
        effects.extend(opencv_effects)
        
        return effects