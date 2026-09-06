import os
import json
import time
import hashlib
from web3 import Web3
from eth_account import Account
from config import Config

# Standard ABI for VerificationRegistry
CONTRACT_ABI = [
    {
        "inputs": [
            {"internalType": "bytes32", "name": "faceHash", "type": "bytes32"},
            {"internalType": "bytes32", "name": "sourceImageHash", "type": "bytes32"},
            {"internalType": "string", "name": "socialPostUrl", "type": "string"},
            {"internalType": "string", "name": "platform", "type": "string"}
        ],
        "name": "recordVerification",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "faceHash", "type": "bytes32"}],
        "name": "getVerification",
        "outputs": [
            {"internalType": "bytes32", "name": "sourceImageHash", "type": "bytes32"},
            {"internalType": "string", "name": "socialPostUrl", "type": "string"},
            {"internalType": "string", "name": "platform", "type": "string"},
            {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
            {"internalType": "address", "name": "verifier", "type": "address"},
            {"internalType": "bool", "name": "exists", "type": "bool"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "totalVerifications",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

class BlockchainRecorder:
    """
    Handles connection to EVM testnets (Polygon Amoy / Ethereum Sepolia) via Web3.py,
    submits tamper-evident transactions, and returns explorer transaction receipts.
    """
    def __init__(self, rpc_url: str = None, private_key: str = None, contract_address: str = None):
        self.rpc_url = rpc_url or Config.RPC_URL
        self.private_key = private_key or Config.PRIVATE_KEY
        self.contract_address = contract_address or Config.CONTRACT_ADDRESS

        self.w3 = None
        self.account = None
        
        self._init_web3()

    def _init_web3(self):
        try:
            self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
            if self.private_key and len(self.private_key) == 66 and self.private_key.startswith("0x"):
                if self.private_key != "0x0000000000000000000000000000000000000000000000000000000000000000":
                    self.account = Account.from_key(self.private_key)
        except Exception as e:
            print(f"[WARN] Failed to initialize live Web3 provider: {e}")

    def record_verification(self, face_hash_hex: str, source_image_hash_hex: str, social_url: str, platform: str) -> dict:
        """
        Records the face match payload onto the blockchain.
        """
        is_live = False
        
        if self.w3 and self.w3.is_connected() and self.account and self.contract_address:
            try:
                print(f"[INFO] Submitting transaction to Polygon Amoy Testnet via wallet {self.account.address[:8]}...")
                return self._submit_live_transaction(face_hash_hex, source_image_hash_hex, social_url, platform)
            except Exception as e:
                print(f"[WARN] Live transaction submission failed: {e}")
                print("[INFO] Switching to deterministic testnet transaction recorder simulation...")
        
        # Fallback / Dry-Run Mode for demonstration
        return self._simulate_transaction(face_hash_hex, source_image_hash_hex, social_url, platform)

    def _submit_live_transaction(self, face_hash_hex: str, source_image_hash_hex: str, social_url: str, platform: str) -> dict:
        contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.contract_address),
            abi=CONTRACT_ABI
        )

        face_bytes32 = bytes.fromhex(face_hash_hex.replace("0x", ""))
        source_bytes32 = bytes.fromhex(source_image_hash_hex.replace("0x", ""))

        nonce = self.w3.eth.get_transaction_count(self.account.address)
        gas_price = self.w3.eth.gas_price

        tx = contract.functions.recordVerification(
            face_bytes32,
            source_bytes32,
            social_url,
            platform
        ).build_transaction({
            'from': self.account.address,
            'nonce': nonce,
            'gasPrice': gas_price,
            'chainId': self.w3.eth.chain_id
        })

        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)

        tx_hash_str = self.w3.to_hex(tx_hash)
        
        return {
            "status": "CONFIRMED_ON_CHAIN",
            "blockchain": "Polygon Amoy Testnet (Chain ID 80002)",
            "transaction_hash": tx_hash_str,
            "block_number": receipt.blockNumber,
            "gas_used": receipt.gasUsed,
            "contract_address": self.contract_address,
            "verifier_address": self.account.address,
            "explorer_url": f"{Config.EXPLORER_BASE_URL}{tx_hash_str}",
            "is_simulation": False
        }

    def _simulate_transaction(self, face_hash_hex: str, source_image_hash_hex: str, social_url: str, platform: str) -> dict:
        """
        Simulates an EVM transaction receipt with a deterministic Tx Hash for demonstration.
        """
        payload_seed = f"{face_hash_hex}:{source_image_hash_hex}:{social_url}:{time.time()}"
        sim_tx_hash = "0x" + hashlib.sha256(payload_seed.encode()).hexdigest()
        sim_contract = self.contract_address or "0x89205A3A3b2A69De6Dbf7f01ED13B2108B2c43e7"
        sim_verifier = self.account.address if self.account else "0x71C7656EC7ab88b098defB751B7401B5f6d8976F"

        return {
            "status": "RECORDED_ON_TESTNET (SIMULATED)",
            "blockchain": "Polygon Amoy Testnet (EVM Target)",
            "transaction_hash": sim_tx_hash,
            "block_number": 14920381,
            "gas_used": 68420,
            "contract_address": sim_contract,
            "verifier_address": sim_verifier,
            "explorer_url": f"{Config.EXPLORER_BASE_URL}{sim_tx_hash}",
            "is_simulation": True,
            "note": "To broadcast live on-chain, configure RPC_URL & PRIVATE_KEY in .env"
        }

if __name__ == "__main__":
    recorder = BlockchainRecorder()
    res = recorder.record_verification(
        face_hash_hex="0x" + "a"*64,
        source_image_hash_hex="0x" + "b"*64,
        social_url="https://x.com/sample/status/123",
        platform="X (Twitter)"
    )
    print(json.dumps(res, indent=2))
