import os
import json
from web3 import Web3
from eth_tester import EthereumTester
from dotenv import load_dotenv

load_dotenv()

class BlockchainClient:
    def __init__(self):
        self.rpc_url = os.getenv("RPC_URL")
        self.private_key = os.getenv("PRIVATE_KEY")
        self.contract_address = os.getenv("CONTRACT_ADDRESS")
        
        # Connect to network
        if self.rpc_url:
            self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
            if self.private_key:
                self.account = self.w3.eth.account.from_key(self.private_key)
            else:
                self.account = None
        else:
            # Fallback to eth-tester for local testing if no RPC is provided
            print("No RPC_URL found, falling back to eth-tester (local mock).")
            tester = EthereumTester()
            self.w3 = Web3(Web3.EthereumTesterProvider(tester))
            self.account = self.w3.eth.accounts[0] # Use first test account
            
        # Load ABI
        contract_json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "contracts", "ContentRegistry.json")
        try:
            with open(contract_json_path, "r") as f:
                contract_data = json.load(f)
                self.abi = contract_data["abi"]
                self.bytecode = contract_data["bytecode"]
        except FileNotFoundError:
            raise Exception(f"Contract JSON not found at {contract_json_path}. Did you run scripts/deploy.py?")
            
        if self.contract_address:
            self.contract = self.w3.eth.contract(address=self.contract_address, abi=self.abi)
        else:
            self.contract = None

    def deploy_contract(self) -> str:
        """Deploys the contract and sets it for the client."""
        Contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        
        if isinstance(self.account, str):
            # eth-tester account
            tx_hash = Contract.constructor().transact({'from': self.account})
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            self.contract_address = tx_receipt.contractAddress
            self.contract = self.w3.eth.contract(address=self.contract_address, abi=self.abi)
            return self.contract_address
        else:
            # real account with private key
            construct_txn = Contract.constructor().build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 3000000,
                'gasPrice': self.w3.eth.gas_price,
            })
            signed = self.account.sign_transaction(construct_txn)
            tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction) # Changed from rawTransaction to raw_transaction
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            self.contract_address = tx_receipt.contractAddress
            self.contract = self.w3.eth.contract(address=self.contract_address, abi=self.abi)
            return self.contract_address

    def register_content(self, content_hash: bytes, source: str) -> str:
        """Registers a canonical hash on the blockchain."""
        if not self.contract:
            raise Exception("Contract not deployed or address not set.")
            
        if isinstance(self.account, str):
            # eth-tester
            tx_hash = self.contract.functions.registerContent(content_hash, source).transact({'from': self.account})
            self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return tx_hash.hex()
        else:
            # real account
            tx = self.contract.functions.registerContent(content_hash, source).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 2000000,
                'gasPrice': self.w3.eth.gas_price,
            })
            signed = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction) # Changed from rawTransaction to raw_transaction
            self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return tx_hash.hex()

    def get_record(self, content_hash: bytes) -> dict:
        """Retrieves a record from the blockchain."""
        if not self.contract:
            raise Exception("Contract not deployed or address not set.")
            
        exists, source, timestamp, submitter = self.contract.functions.getRecord(content_hash).call()
        return {
            "exists": exists,
            "source": source,
            "timestamp": timestamp,
            "submitter": submitter
        }
