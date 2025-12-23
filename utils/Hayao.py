import cv2
import numpy as np

def apply_hayao_style(image_data):
    """Hayao Miyazaki style - soft, dreamy colors"""
    nparr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Soften the image
    img = cv2.bilateralFilter(img, 9, 75, 75)
    
    # Adjust colors for dreamy effect
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hsv[:, :, 1] = hsv[:, :, 1] * 0.8  # Reduce saturation
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 1.2, 0, 255)  # Increase brightness
    img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    _, buffer = cv2.imencode('.png', img)
    return buffer.tobytes()