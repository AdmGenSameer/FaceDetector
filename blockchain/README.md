# Face Verification Pipeline: Blockchain Module

This repository contains the standalone blockchain module for the Face/Web Content Verification Pipeline. It is responsible for taking discovered web content (JSON data representing social media posts/images) and creating an immutable, verifiable provenance record on an Ethereum-compatible blockchain.

## 1. Architecture

The system acts as a decentralized notary. It does **not** store the raw images or text on the blockchain (which would be prohibitively expensive and a privacy violation). Instead, it stores a **canonical SHA-256 hash** of the data. 

**Workflow:**
1. **Input**: The module receives a JSON file containing the discovered web content metadata.
2. **Canonicalization**: The JSON is canonicalized (keys sorted, whitespace stripped) to ensure deterministic hashing.
3. **Hashing**: A SHA-256 hash is generated.
4. **Registration**: The hash is submitted to the `ContentRegistry` smart contract.
5. **Verification**: When requested, the system recalculates the hash of the provided content and checks if it exists in the registry. If it exists, the content is `VERIFIED`. If the hash is missing (or if the content was altered, producing a different hash), it is flagged as `TAMPERED`.

## 2. Technology Stack

- **Smart Contracts**: Solidity (^0.8.19)
- **Language**: Python 3
- **Blockchain Interaction**: `web3.py`
- **Local Testing Environment**: `eth-tester` (allows running the full pipeline locally without needing a real RPC node or testnet ETH)
- **Testing**: `pytest`

## 3. Setup Instructions

1. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Copy the example config and edit if deploying to a real testnet (e.g., Sepolia).
   ```bash
   cp .env.example .env
   ```
   *Note: By default, if `RPC_URL` is empty, the client will fall back to using an ephemeral local `eth-tester` node.*

## 4. Contract Deployment

Before interacting with the blockchain, you must compile the smart contract to generate the ABI and bytecode.

```bash
python scripts/deploy.py
```

This script will compile `contracts/ContentRegistry.sol` and save the output to `contracts/ContentRegistry.json`.

If you are using a real testnet (via `.env`), you can write a deployment script using the compiled artifacts, or the client will automatically deploy a temporary contract if running locally.

## 5. CLI Usage

The module exposes a command-line interface via `src/blockchain`.

**Register Content**:
```bash
PYTHONPATH=. python -m src.blockchain register examples/content.json
```

**Verify Content**:
```bash
PYTHONPATH=. python -m src.blockchain verify examples/content.json
```

## 6. Tampering Demonstration

To demonstrate the immutable properties of the system, follow these steps:

1. **Register the authentic data**:
   ```bash
   PYTHONPATH=. python -m src.blockchain register examples/content.json
   ```
   *(Note the Canonical Hash printed in the terminal).*

2. **Verify the authentic data**:
   ```bash
   PYTHONPATH=. python -m src.blockchain verify examples/content.json
   ```
   *(The output will show **Status: VERIFIED**).*

3. **Tamper with the data**:
   Open `examples/content.json` in a text editor and change any value (e.g., change the `location` or `timestamp`). Save the file.

4. **Verify the tampered data**:
   ```bash
   PYTHONPATH=. python -m src.blockchain verify examples/content.json
   ```
   *(The output will show **Status: TAMPERED** and highlight that the newly calculated hash was not found on the blockchain).*

## 7. Security Considerations

- **Privacy Preserving**: By storing only a SHA-256 hash, no Personally Identifiable Information (PII) or raw biometric data is ever exposed on the public ledger.
- **Immutability**: Once a hash is registered, its timestamp and existence cannot be altered, providing a cryptographic anchor of trust.
- **Deterministic Hashing**: The canonicalization step ensures that functionally identical JSON files (e.g., keys in a different order) produce the same hash, preventing false "tampered" flags due to formatting.

## 8. Limitations

- **Garbage In, Garbage Out**: The blockchain only proves that a specific piece of data existed at a specific time. It does *not* prove that the data itself is true. If a deepfake is registered before being detected, the blockchain will faithfully record the deepfake.
- **Cost**: Deploying to Ethereum mainnet incurs gas fees. For production, a Layer 2 solution (e.g., Arbitrum, Optimism) or Polygon is recommended.
