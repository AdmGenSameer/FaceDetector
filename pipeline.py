#!/usr/bin/env python3
"""
===================================================================
Face ID + Blockchain Verification Pipeline
End-to-End CLI Orchestrator
===================================================================
Pipeline Execution Flow:
 1. Face Detection & Feature Fingerprint Encoding
 2. Genuine Reverse Image Search for Social Media Post Matching
 3. Blockchain On-Chain Recordation (Polygon Amoy / Ethereum Testnet)
 4. Tamper-Evident Verification Report Generation
===================================================================
"""

import sys
import os
import json
import argparse
import time
from pathlib import Path

from config import Config
from face_encoder import FaceEncoder
from reverse_search import ReverseImageSearcher
from blockchain_recorder import BlockchainRecorder

BANNER = """
===================================================================
    FACIAL RECOGNITION + BLOCKCHAIN VERIFICATION PIPELINE v1.0
===================================================================
  [Task #3] Detect Face -> Reverse Search -> Anchor to Blockchain
===================================================================
"""

def run_pipeline(image_path: str, save_report: bool = True) -> dict:
    print(BANNER)
    start_time = time.time()

    # Validate image path
    if not os.path.exists(image_path):
        print(f"[ERROR] Image file does not exist: {image_path}")
        sys.exit(1)

    # -------------------------------------------------------------------
    # STEP 1: FACE DETECTION & ENCODING
    # -------------------------------------------------------------------
    print(f"\n[STEP 1/3] Detecting & Encoding Face from Image...")
    print(f" -> Input Image: {image_path}")
    
    encoder = FaceEncoder()
    encoding_result = encoder.detect_and_encode(image_path)
    
    print(f" [+] Face Detected Bounding Box : {encoding_result['bounding_box']}")
    print(f" [+] Face Crop Exported         : {encoding_result['face_crop_path']}")
    print(f" [+] Face Fingerprint Hash (256): {encoding_result['face_hash_hex']}")
    print(f" [+] Source Image Hash (SHA256) : {encoding_result['source_image_hash']}")

    # -------------------------------------------------------------------
    # STEP 2: REVERSE IMAGE SEARCH FOR SOCIAL MEDIA MATCH
    # -------------------------------------------------------------------
    print(f"\n[STEP 2/3] Performing Reverse Image Search for Social Media Matches...")
    
    searcher = ReverseImageSearcher()
    match_result = searcher.search_by_image(image_path)
    
    print(f" [+] Search Engine Used   : {match_result.get('search_engine', 'Reverse Search Engine')}")
    print(f" [+] Social Media Match   : {match_result['matched_url']}")
    print(f" [+] Platform Detected    : {match_result['platform']}")
    print(f" [+] Post / Media Title   : {match_result['title']}")
    print(f" [+] Match Confidence     : {match_result['match_confidence'] * 100:.1f}%")

    # -------------------------------------------------------------------
    # STEP 3: BLOCKCHAIN RECORDATION
    # -------------------------------------------------------------------
    print(f"\n[STEP 3/3] Writing Tamper-Evident Verification Record to Blockchain...")
    
    recorder = BlockchainRecorder()
    tx_result = recorder.record_verification(
        face_hash_hex=encoding_result['face_hash_hex'],
        source_image_hash_hex=encoding_result['source_image_hash'],
        social_url=match_result['matched_url'],
        platform=match_result['platform']
    )
    
    print(f" [+] Target Blockchain    : {tx_result['blockchain']}")
    print(f" [+] Status               : {tx_result['status']}")
    print(f" [+] Transaction Hash     : {tx_result['transaction_hash']}")
    print(f" [+] Block Number         : {tx_result['block_number']}")
    print(f" [+] Gas Consumed         : {tx_result['gas_used']} gas units")
    print(f" [+] Contract Address     : {tx_result['contract_address']}")
    print(f" [+] Explorer Receipt URL : {tx_result['explorer_url']}")

    elapsed = time.time() - start_time

    # -------------------------------------------------------------------
    # COMPILING VERIFICATION REPORT
    # -------------------------------------------------------------------
    report = {
        "pipeline_version": "1.0.0",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "execution_time_seconds": round(elapsed, 3),
        "input_image": encoding_result,
        "social_media_match": match_result,
        "blockchain_record": tx_result
    }

    if save_report:
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        report_path = output_dir / "verification_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\n[SUMMARY] Complete verification report exported to: {report_path}")

    print("\n===================================================================")
    print("  VERIFICATION PIPELINE EXECUTED SUCCESSFULLY (End-to-End Validated)")
    print("===================================================================\n")

    return report

def main():
    parser = argparse.ArgumentParser(
        description="Face ID + Blockchain Verification Pipeline CLI"
    )
    parser.add_argument(
        "--image", 
        type=str, 
        required=True, 
        help="Path to input photo containing a face"
    )
    parser.add_argument(
        "--json", 
        action="store_true", 
        help="Output raw JSON verification report to stdout"
    )

    args = parser.parse_args()
    report = run_pipeline(args.image, save_report=True)
    
    if args.json:
        print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
