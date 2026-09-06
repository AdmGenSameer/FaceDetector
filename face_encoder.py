import os
import hashlib
import json
from pathlib import Path
import cv2
import numpy as np

class FaceEncoder:
    """
    Detects faces in an input image, crops the primary face region, 
    computes face encodings/fingerprints, and generates tamper-evident SHA-256 hashes.
    """
    def __init__(self, cascade_path: str = None):
        self.face_cascade = None
        if cascade_path is None and hasattr(cv2, 'data') and hasattr(cv2.data, 'haarcascades'):
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        
        if cascade_path and os.path.exists(cascade_path):
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
        else:
            print("[INFO] OpenCV Haar Cascade XML file not found at path; using ROI face detection fallback.")

    def detect_and_encode(self, image_path: str, output_dir: str = "output") -> dict:
        """
        Detects faces in the image at `image_path`, extracts features, 
        saves the cropped face, and returns metadata & hashes.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Input image not found: {image_path}")

        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image file: {image_path}")

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        faces = []
        if self.face_cascade is not None:
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=5, 
                minSize=(30, 30)
            )

        height, width, _ = image.shape
        
        if len(faces) == 0:
            # Fallback: if no face bounding box detected, crop center 60% of image as primary region
            print("[INFO] No strict face bounding box detected. Using central ROI crop fallback.")
            margin_x, margin_y = int(width * 0.2), int(height * 0.2)
            face_roi = image[margin_y:height-margin_y, margin_x:width-margin_x]
            bbox = [margin_x, margin_y, width - 2 * margin_x, height - 2 * margin_y]
        else:
            # Select largest face detected
            largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
            x, y, w, h = largest_face
            bbox = [int(x), int(y), int(w), int(h)]
            # Add slight padding (10%)
            pad_x, pad_y = int(w * 0.1), int(h * 0.1)
            x1 = max(0, x - pad_x)
            y1 = max(0, y - pad_y)
            x2 = min(width, x + w + pad_x)
            y2 = min(height, y + h + pad_y)
            face_roi = image[y1:y2, x1:x2]

        # Standardize face crop size to 224x224
        face_resized = cv2.resize(face_roi, (224, 224))
        
        # Ensure output directory exists
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        crop_path = os.path.join(output_dir, "face_crop.jpg")
        cv2.imwrite(crop_path, face_resized)

        # Compute face crop image hash (SHA-256)
        _, crop_encoded = cv2.imencode('.jpg', face_resized)
        crop_bytes = crop_encoded.tobytes()
        face_hash = hashlib.sha256(crop_bytes).hexdigest()

        # Generate mock 512-dim normalized feature embedding vector from ROI features
        # (Allows deterministic vector representation for downstream indexing)
        gray_roi = cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY)
        flattened = gray_roi.flatten().astype(np.float32)
        norm_vector = (flattened - np.mean(flattened)) / (np.std(flattened) + 1e-6)
        # Resample to 512 floats
        embedding_512 = np.interp(
            np.linspace(0, len(norm_vector), 512), 
            np.arange(len(norm_vector)), 
            norm_vector
        ).tolist()

        # Full full-image SHA-256 for integrity reference
        with open(image_path, "rb") as f:
            source_image_hash = hashlib.sha256(f.read()).hexdigest()

        result = {
            "source_image_path": str(image_path),
            "source_image_hash": source_image_hash,
            "face_crop_path": str(crop_path),
            "bounding_box": bbox,
            "face_hash": face_hash,  # Tamper-evident face fingerprint hash (bytes32 format ready)
            "face_hash_hex": "0x" + face_hash,
            "embedding_dim": len(embedding_512),
            "embedding_sample": embedding_512[:5]  # Display first 5 components
        }

        return result

if __name__ == "__main__":
    import sys
    encoder = FaceEncoder()
    test_img = sys.argv[1] if len(sys.argv) > 1 else None
    if test_img:
        res = encoder.detect_and_encode(test_img)
        print(json.dumps(res, indent=2))
    else:
        print("Usage: python face_encoder.py <path_to_image>")
