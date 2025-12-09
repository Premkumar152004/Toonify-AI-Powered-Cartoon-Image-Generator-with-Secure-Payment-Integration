import cv2
import numpy as np

def apply_cartoon_filter(image, k_colors=6, edge=30, blur=1):
    """
    Cleaner HD Cartoon Filter
    ------------------------
    - Smooth colors with multiple bilateral filters
    - Strong but soft cartoon outlines
    - Fewer color blocks for cleaner look
    """
    def odd_ksize(value):
        k = max(3, int(value))
        if k % 2 == 0:
            k += 1
        return k

    # 1. Smooth colors
    color = image.copy()
    for _ in range(blur):
        color = cv2.bilateralFilter(color, d=5, sigmaColor=50, sigmaSpace=blur*10)

    # 2. Color Quantization
    Z = color.reshape((-1, 3))
    Z = np.float32(Z)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
    _, labels, centers = cv2.kmeans(Z, k_colors, None, criteria, 10, cv2.KMEANS_PP_CENTERS)
    centers = np.uint8(centers)
    color = centers[labels.flatten()].reshape(image.shape)

    # 3. Edge Detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, odd_ksize(blur*2))
    edges = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, max(1, edge//50)
    )
    edges = cv2.medianBlur(edges, odd_ksize(blur))
    edges = cv2.dilate(edges, np.ones((1,1), np.uint8))  # softer edges

    # 4. Combine edges with colors
    edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    cartoon = cv2.bitwise_and(color, edges_colored)

    return cartoon