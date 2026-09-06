import os
import unittest
from pathlib import Path
import numpy as np
import cv2

from face_encoder import FaceEncoder
from reverse_search import ReverseImageSearcher
from blockchain_recorder import BlockchainRecorder
from pipeline import run_pipeline

def generate_synthetic_face_image(output_path: str = "test_samples/sample_face.jpg"):
    """
    Generates a synthetic image with face features for automated testing.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # 400x400 background image
    img = np.ones((400, 400, 3), dtype=np.uint8) * 230
    
    # Draw head (ellipse)
    cv2.ellipse(img, (200, 200), (80, 110), 0, 0, 360, (180, 150, 120), -1)
    # Eyes
    cv2.circle(img, (170, 170), 12, (255, 255, 255), -1)
    cv2.circle(img, (230, 170), 12, (255, 255, 255), -1)
    cv2.circle(img, (170, 170), 5, (50, 50, 50), -1)
    cv2.circle(img, (230, 170), 5, (50, 50, 50), -1)
    # Mouth
    cv2.ellipse(img, (200, 240), (35, 15), 0, 0, 180, (50, 50, 200), 4)

    cv2.imwrite(output_path, img)
    return output_path

class TestFaceBlockchainPipeline(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.sample_path = generate_synthetic_face_image()

    def test_01_face_encoder(self):
        encoder = FaceEncoder()
        res = encoder.detect_and_encode(self.sample_path)
        self.assertIn("face_hash", res)
        self.assertEqual(len(res["face_hash"]), 64) # SHA256 length
        self.assertIn("bounding_box", res)
        self.assertTrue(os.path.exists(res["face_crop_path"]))

    def test_02_reverse_search(self):
        searcher = ReverseImageSearcher()
        res = searcher.search_by_image(self.sample_path)
        self.assertIn("matched_url", res)
        self.assertIn("platform", res)
        self.assertGreater(res["match_confidence"], 0)

    def test_03_blockchain_recorder(self):
        recorder = BlockchainRecorder()
        res = recorder.record_verification(
            face_hash_hex="0x" + "a"*64,
            source_image_hash_hex="0x" + "b"*64,
            social_url="https://x.com/test/status/1",
            platform="X (Twitter)"
        )
        self.assertIn("transaction_hash", res)
        self.assertIn("explorer_url", res)

    def test_04_full_pipeline(self):
        report = run_pipeline(self.sample_path, save_report=True)
        self.assertEqual(report["pipeline_version"], "1.0.0")
        self.assertIn("blockchain_record", report)
        self.assertTrue(os.path.exists("output/verification_report.json"))

if __name__ == "__main__":
    unittest.main()
