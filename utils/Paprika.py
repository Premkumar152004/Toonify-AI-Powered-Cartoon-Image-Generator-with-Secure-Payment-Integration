"""
Paprika Style Processor using ONNX
Surreal, dreamlike anime art effect
"""
import cv2
import numpy as np
import onnxruntime as ort
import os

MODEL_PATH = "anime_models/Paprika.onnx"

# Initialize session globally to avoid reloading
session = None

def load_model():
    """Load ONNX model once"""
    global session
    if session is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model not found: {MODEL_PATH}")
        
        session = ort.InferenceSession(
            MODEL_PATH,
            providers=["CPUExecutionProvider"]
        )
        print(f"✅ Paprika model loaded from {MODEL_PATH}")
    return session

def preprocess(image):
    """
    Preprocess image for AnimeGAN2 ONNX model
    Input: BGR image (H, W, 3)
    Output: Float tensor (1, H, W, 3) normalized to [0, 1] - NHWC format
    """
    # Save original size
    h, w = image.shape[:2]
    original_size = (w, h)
    
    # Convert BGR to RGB
    img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Convert to float32 and normalize to [0, 1]
    img_float = img_rgb.astype(np.float32) / 255.0
    
    # Add batch dimension (N, H, W, C) - NHWC format
    img_batch = np.expand_dims(img_float, axis=0)
    
    return img_batch, original_size

def postprocess(output, original_size):
    """
    Postprocess model output to BGR image
    Input: Float tensor (1, H, W, 3) in range [0, 1]
    Output: BGR image (H, W, 3) uint8
    """
    # Remove batch dimension
    output = output.squeeze(0)
    
    # Scale to [0, 255]
    output = output * 255.0
    output = np.clip(output, 0, 255).astype(np.uint8)
    
    # Convert RGB to BGR
    output = cv2.cvtColor(output, cv2.COLOR_RGB2BGR)
    
    # Resize to original size if needed
    if output.shape[:2] != (original_size[1], original_size[0]):
        output = cv2.resize(output, original_size)
    
    return output

def apply_paprika_style(image):
    """
    Apply Paprika anime style to image
    
    Args:
        image: BGR image (numpy array) from OpenCV
        
    Returns:
        Styled BGR image
    """
    try:
        # Load model
        model = load_model()
        
        # Preprocess
        input_tensor, original_size = preprocess(image)
        
        # Run inference
        input_name = model.get_inputs()[0].name
        output_name = model.get_outputs()[0].name
        
        print(f"🔄 Paprika: Processing {original_size[0]}x{original_size[1]} image...")
        output = model.run([output_name], {input_name: input_tensor})[0]
        
        # Postprocess
        result = postprocess(output, original_size)
        
        print(f"✅ Paprika: Style applied successfully")
        return result
        
    except Exception as e:
        print(f"❌ Error applying Paprika style: {e}")
        import traceback
        traceback.print_exc()
        return image