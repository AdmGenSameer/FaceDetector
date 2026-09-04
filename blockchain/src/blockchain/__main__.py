import argparse
import json
import sys
import os
from .client import BlockchainClient
from .hasher import generate_canonical_hash
from .verifier import verify_content

def main():
    parser = argparse.ArgumentParser(description="Blockchain Content Provenance CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Register command
    register_parser = subparsers.add_parser("register", help="Register content on the blockchain")
    register_parser.add_argument("file_path", help="Path to the JSON file to register")

    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify content against the blockchain")
    verify_parser.add_argument("file_path", help="Path to the JSON file to verify")

    args = parser.parse_args()

    # Load JSON file
    if not os.path.exists(args.file_path):
        print(f"Error: File not found: {args.file_path}")
        sys.exit(1)

    with open(args.file_path, "r") as f:
        try:
            content_data = json.load(f)
        except json.JSONDecodeError:
            print(f"Error: File {args.file_path} is not valid JSON.")
            sys.exit(1)

    # Initialize client
    client = BlockchainClient()
    
    # Ensure contract is deployed (mostly for local testing if env is not set)
    if not client.contract_address:
        print("No CONTRACT_ADDRESS in env. Deploying a new local contract...")
        address = client.deploy_contract()
        print(f"Deployed local ContentRegistry at {address}")

    if args.command == "register":
        canonical_hash = generate_canonical_hash(content_data)
        print(f"Canonical Hash: 0x{canonical_hash.hex()}")
        
        # We'll use a generic source string here or extract if available
        source = content_data.get("source_url", "unknown_source")
        
        print("Registering on blockchain...")
        tx_hash = client.register_content(canonical_hash, source)
        print(f"Success! Transaction Hash: {tx_hash}")

    elif args.command == "verify":
        print(f"Verifying {args.file_path}...")
        result = verify_content(client, content_data)
        
        print("\n--- Verification Result ---")
        if result["verified"]:
            print("Status: \033[92mVERIFIED\033[0m")
        else:
            print("Status: \033[91mTAMPERED\033[0m")
            
        print(f"Reason: {result['reason']}")
        print(f"Local Hash: 0x{result['local_hash']}")
        if result["blockchain_hash"]:
            print(f"Blockchain Hash: 0x{result['blockchain_hash']}")
            record = result.get("record", {})
            print(f"Registered Source: {record.get('source')}")
            print(f"Registered By: {record.get('submitter')}")

if __name__ == "__main__":
    main()
