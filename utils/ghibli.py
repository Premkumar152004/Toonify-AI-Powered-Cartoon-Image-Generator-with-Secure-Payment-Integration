import cv2
import numpy as np
import onnxruntime as ort

MODEL_PATH = "anime_models\Ghibli.onnx"

session = ort.InferenceSession(
    MODEL_PATH,
    providers=["CPUExecutionProvider"]
)

# Optional: Face Detection (if you want face-only editing)
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)


def detect_face(img):
    """Detect face and return bounding box."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
    )

    if len(faces) == 0:
        return None

    x, y, w, h = faces[0]
    pad = int(0.3 * h)
    x1 = max(x - pad, 0)
    y1 = max(y - pad, 0)
    x2 = min(x + w + pad, img.shape[1])
    y2 = min(y + h + pad, img.shape[0])

    return x1, y1, x2, y2


def preprocess(image, size=512):
    image = cv2.resize(image, (size, size))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = image.astype(np.float32) / 255.0
    image = np.expand_dims(image, 0)  # (1, H, W, 3)
    return image

def postprocess(output, original_size):
    output = output[0]  # (H, W, 3)
    output = np.clip(output * 255, 0, 255).astype(np.uint8)
    output = cv2.cvtColor(output, cv2.COLOR_RGB2BGR)
    output = cv2.resize(output, original_size)
    return output



def apply_ghibli_style(img, face_only=False):
    """
    Apply Ghibli Anime Style.
    face_only=True  → Modify only face
    face_only=False → Convert full image
    """

    if not face_only:
        # Full image conversion (recommended)
        original_size = (img.shape[1], img.shape[0])
        inp = preprocess(img)
        out = session.run(None, {session.get_inputs()[0].name: inp})[0]
        output = postprocess(out, original_size)
        return output

    # Face-only mode
    face_box = detect_face(img)
    if face_box is None:
        return img

    x1, y1, x2, y2 = face_box
    face = img[y1:y2, x1:x2]
    original_size = (face.shape[1], face.shape[0])

    inp = preprocess(face)
    out = session.run(None, {session.get_inputs()[0].name: inp})[0]
    anime_face = postprocess(out, original_size)

    result = img.copy()
    result[y1:y2, x1:x2] = anime_face
    return result