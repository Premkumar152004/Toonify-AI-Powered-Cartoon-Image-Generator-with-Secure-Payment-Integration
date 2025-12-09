"""
AnimeGAN2 Processor - ONNX + PyTorch Support (CPU Only)
Supports both .onnx and .pt model files for offline CPU inference
"""
import numpy as np
import cv2
import os
from PIL import Image
import onnxruntime as ort

# Try importing ONNX Runtime
try:
    
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False
    print("⚠️ ONNX Runtime not available. Install: pip install onnxruntime")

# Try importing PyTorch
try:
    import torch
    import torchvision.transforms as transforms
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("⚠️ PyTorch not available. Install: pip install torch torchvision")


class ONNXAnimeGAN:
    """AnimeGAN2 using ONNX Runtime (CPU)"""
    
    def __init__(self, model_path):
        if not ONNX_AVAILABLE:
            raise RuntimeError("ONNX Runtime not installed")
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        # Create ONNX session (CPU only)
        self.session = ort.InferenceSession(
            model_path,
            providers=['CPUExecutionProvider']
        )
        
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        
        print(f"✅ ONNX Model loaded: {os.path.basename(model_path)}")
    
    def preprocess(self, image):
        """Preprocess image for ONNX model"""
        if isinstance(image, np.ndarray):
            # Convert BGR to RGB
            if len(image.shape) == 3 and image.shape[2] == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy and normalize
        img_array = np.array(image).astype(np.float32)
        img_array = img_array / 127.5 - 1.0  # Normalize to [-1, 1]
        
        # Transpose to [1, 3, H, W]
        img_array = np.transpose(img_array, (2, 0, 1))
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    
    def postprocess(self, output):
        """Postprocess ONNX output to image"""
        # Remove batch dimension
        output = output.squeeze(0)
        
        # Denormalize from [-1, 1] to [0, 255]
        output = (output + 1.0) * 127.5
        output = np.clip(output, 0, 255).astype(np.uint8)
        
        # Transpose from [3, H, W] to [H, W, 3]
        output = np.transpose(output, (1, 2, 0))
        
        # Convert RGB to BGR for OpenCV
        output = cv2.cvtColor(output, cv2.COLOR_RGB2BGR)
        
        return output
    
    def convert(self, image):
        """Convert image to anime style"""
        try:
            input_tensor = self.preprocess(image)
            output = self.session.run([self.output_name], {self.input_name: input_tensor})[0]
            result = self.postprocess(output)
            return result
        except Exception as e:
            print(f"❌ ONNX conversion error: {e}")
            if isinstance(image, np.ndarray):
                return image
            else:
                return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


class PyTorchAnimeGAN:
    """AnimeGAN2 using PyTorch (CPU)"""
    
    def __init__(self, model_path):
        if not TORCH_AVAILABLE:
            raise RuntimeError("PyTorch not installed")
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        self.device = torch.device('cpu')
        
        try:
            # Try loading as TorchScript
            self.model = torch.jit.load(model_path, map_location=self.device)
            print(f"✅ Loaded as TorchScript model")
        except Exception as e1:
            # Try loading as state dict
            try:
                checkpoint = torch.load(model_path, map_location=self.device)
                # Handle different checkpoint formats
                if isinstance(checkpoint, dict):
                    if 'model_state_dict' in checkpoint:
                        self.model = checkpoint['model_state_dict']
                    elif 'state_dict' in checkpoint:
                        self.model = checkpoint['state_dict']
                    else:
                        self.model = checkpoint
                else:
                    self.model = checkpoint
                print(f"✅ Loaded as state dict")
            except Exception as e2:
                raise RuntimeError(f"Failed to load model: TorchScript error: {e1}, StateDict error: {e2}")
        
        if hasattr(self.model, 'eval'):
            self.model.eval()
        
        print(f"✅ PyTorch Model loaded: {os.path.basename(model_path)}")
    
    def preprocess(self, image):
        """Preprocess image for PyTorch model"""
        if isinstance(image, np.ndarray):
            if len(image.shape) == 3 and image.shape[2] == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to tensor and normalize to [-1, 1]
        img_array = np.array(image).astype(np.float32)
        img_array = img_array / 127.5 - 1.0
        
        # Transpose to [1, 3, H, W]
        img_tensor = torch.from_numpy(img_array).permute(2, 0, 1).unsqueeze(0).to(self.device)
        
        return img_tensor
    
    def postprocess(self, output):
        """Postprocess PyTorch output to image"""
        output = output.squeeze(0).cpu()
        
        # Denormalize from [-1, 1] to [0, 255]
        output = (output + 1.0) * 127.5
        output = output.clamp(0, 255).byte().numpy()
        
        # Transpose from [3, H, W] to [H, W, 3]
        output = np.transpose(output, (1, 2, 0))
        
        # Convert RGB to BGR for OpenCV
        output = cv2.cvtColor(output, cv2.COLOR_RGB2BGR)
        
        return output
    
    def convert(self, image):
        """Convert image to anime style"""
        try:
            input_tensor = self.preprocess(image)
            
            with torch.no_grad():
                output = self.model(input_tensor)
            
            if isinstance(output, tuple):
                output = output[0]
            
            result = self.postprocess(output)
            return result
        except Exception as e:
            print(f"❌ PyTorch conversion error: {e}")
            import traceback
            traceback.print_exc()
            if isinstance(image, np.ndarray):
                return image
            else:
                return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


class AnimeGANManager:
    """Manager for multiple AnimeGAN2 models (ONNX + PyTorch)"""
    
    def __init__(self, models_dir="anime_models"):
        self.models_dir = models_dir
        self.models = {}
        
        # Define available models (ONNX and PyTorch)
        self.model_files = {
            "Hayao": "Hayao.onnx",
            "Shinkai": "Shinkai.onnx",
            "Paprika": "paprika.pt",
            "FacePaint V1": "face_paint_v1.pt",
            "FacePaint V2": "face_paint_v2.pt",
            "Celeba Distill": "celeba_distill.pt",
        }
        
        # Check which models are available
        self.available_styles = []
        for style, filename in self.model_files.items():
            model_path = os.path.join(self.models_dir, filename)
            if os.path.exists(model_path):
                self.available_styles.append(style)
                print(f"✅ Found model: {style} ({filename})")
            else:
                print(f"⚠️ Model not found: {style} ({filename})")
        
        if not self.available_styles:
            print(f"❌ No models found in {models_dir}/")
            print(f"Expected models: {list(self.model_files.values())}")
        else:
            print(f"✅ Initialized with {len(self.available_styles)} anime styles: {', '.join(self.available_styles)}")
    
    def get_model(self, style):
        """Load model for specific style"""
        if style not in self.available_styles:
            raise ValueError(f"Style '{style}' not available. Available: {self.available_styles}")
        
        # Load model if not cached
        if style not in self.models:
            model_path = os.path.join(self.models_dir, self.model_files[style])
            
            # Determine model type by extension
            if model_path.endswith('.onnx'):
                if not ONNX_AVAILABLE:
                    raise RuntimeError(f"{style} requires ONNX Runtime. Install: pip install onnxruntime")
                self.models[style] = ONNXAnimeGAN(model_path)
            elif model_path.endswith('.pt'):
                if not TORCH_AVAILABLE:
                    raise RuntimeError(f"{style} requires PyTorch. Install: pip install torch torchvision")
                self.models[style] = PyTorchAnimeGAN(model_path)
            else:
                raise ValueError(f"Unsupported model format: {model_path}")
        
        return self.models[style]
    
    def convert(self, image, style):
        """Convert image using specified style"""
        model = self.get_model(style)
        return model.convert(image)
    
    def clear_cache(self):
        """Clear loaded models from memory"""
        self.models.clear()
        print("🗑️ Model cache cleared")