<<<<<<< HEAD
# Face Verification Pipeline

This repository contains the microservices for the HH Goa 2026 Shortlisting Task 3: Face Identification & Blockchain Verification.

## Project Structure

The project is divided into distinct modules, allowing different teams to work independently.

### `blockchain/`
Handles the content provenance and verification. It receives discovered social media data, generates a canonical hash, and uploads it to the Ethereum testnet via a smart contract. See `blockchain/README.md` for specific setup instructions for the junior developer.

### `ml_pipeline/`
Handles the face detection and recognition logic. Takes an input image and extracts face encodings.

### `search_engine/`
Takes the face encodings and searches the web/social media to find genuine matching posts. Returns the discovered post metadata to the blockchain module.

### `shared/`
Contains shared utilities, constants, and data models used across multiple modules to ensure smooth integration.
=======
# Face ID + Blockchain Verification Pipeline

A production-grade Python backend pipeline that detects and encodes faces from input photographs, performs genuine reverse-image searches to find matching social media posts, and anchors tamper-evident verification records permanently onto an EVM blockchain (Polygon Amoy / Ethereum Sepolia Testnet).

---

## Architecture Flow

```
+----------------+      +-----------------------+      +--------------------------+
|  Input Image   | ---> |  Face ID Encoder      | ---> | Reverse Image Search     |
| (Photos/Crops) |      |  - Bbox Detection     |      | - SerpApi / Google Lens  |
+----------------+      |  - 512d Feature Vector|      | - Social Post Extraction |
                        |  - SHA-256 Fingerprint|      +--------------------------+
                        +-----------------------+                    |
                                                                     v
+----------------+      +-----------------------+      +--------------------------+
| Block Explorer | <--- |  Polygon Amoy Testnet | <--- | Blockchain Recorder      |
|  Verification  |      |  VerificationRegistry |      | - Web3.py Sign & Send    |
+----------------+      +-----------------------+      +--------------------------+
```

---

## Features

- **Face Detection & Encoding (`face_encoder.py`)**:
  - Detects bounding box coordinates of faces using OpenCV Haar Cascades / DNN models.
  - Crops & standardizes face region (`224x224`).
  - Generates deterministic 512-dimensional normalized feature embeddings.
  - Produces a canonical cryptographic SHA-256 fingerprint hash (`face_hash`) for on-chain anchoring.

- **Genuine Reverse Image Search (`reverse_search.py`)**:
  - Queries SerpApi Google Lens engine (`engine="google_lens"`) to locate real web/social matches.
  - Filters results against social media domains (X/Twitter, Instagram, LinkedIn, Facebook, Reddit, TikTok, Pinterest).
  - Extracts matching post URLs, titles, and match confidence scores.
  - Includes a fallback generator for offline testing or dry-run demonstrations.

- **Blockchain Tamper-Evident Ledger (`contracts/VerificationRegistry.sol` & `blockchain_recorder.py`)**:
  - Connects via `web3.py` to EVM testnets (Polygon Amoy Chain ID `80002` or Ethereum Sepolia).
  - Deploys/Interacts with `VerificationRegistry.sol` contract.
  - Records `(faceHash, sourceImageHash, socialPostUrl, platform, timestamp, verifierAddress)` immutably on-chain.
  - Generates block explorer receipts (Polygonscan/Etherscan) for immediate third-party verification.

---

## Prerequisites & Installation

### 1. Clone & Environment Setup
```bash
cd e:\HHGOA\face_blockchain_pipeline
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables Configuration
Copy `.env.example` to `.env` and fill in your keys (optional for mock/dry-run mode):
```bash
cp .env.example .env
```
Key parameters in `.env`:
- `SERPAPI_KEY`: Your SerpApi API key for live Google Lens reverse image search.
- `RPC_URL`: `https://rpc-amoy.polygon.technology` (Polygon Amoy Testnet RPC).
- `PRIVATE_KEY`: Funded testnet wallet private key.
- `CONTRACT_ADDRESS`: Deployed `VerificationRegistry.sol` contract address.

---

## How to Run the Pipeline

### Quick Start Execution
To run the full end-to-end pipeline on any photo:
```bash
python pipeline.py --image test_samples/sample_face.jpg
```

### Output Artifacts Generated:
1. **Cropped Face Asset**: `output/face_crop.jpg`
2. **JSON Verification Report**: `output/verification_report.json`
3. **Blockchain Receipt**: On-chain transaction hash printed with block explorer link.

### Run Automated Unit & Integration Tests
```bash
python test_pipeline.py
```

---

## Smart Contract Details (`VerificationRegistry.sol`)

- **Network**: Polygon Amoy Testnet (Chain ID: `80002`) / Ethereum Sepolia
- **Compiler Version**: Solidity `^0.8.19`
- **Data Structure**:
  ```solidity
  struct VerificationRecord {
      bytes32 faceHash;           // SHA-256 fingerprint hash of face crop
      bytes32 sourceImageHash;    // SHA-256 hash of raw input photo
      string socialPostUrl;       // Verified matching social media URL
      string platform;            // Platform name (X, Instagram, etc.)
      uint256 timestamp;          // On-chain block timestamp
      address verifier;           // Verifier wallet address
  }
  ```

---

## Known Limitations

1. **Social Media API Rate Limits**: Public reverse image search APIs (SerpApi) rate-limit high-frequency automated requests; batch jobs should introduce delay throttling.
2. **Face Resolution**: Photos with faces below 30x30 pixels may use center ROI fallback cropping.
3. **Testnet Faucets**: Testnet MATIC/ETH requires periodic refilling from public faucets (e.g. `faucet.polygon.technology`).

---

## Submission Guidance (Screen Recording)

For the hackathon submission video:
1. Open a terminal and run `python pipeline.py --image test_samples/sample_face.jpg`.
2. Highlight the 3 steps as they complete:
   - **Step 1**: Face crop & SHA-256 fingerprint hash output.
   - **Step 2**: Extracted social media post match URL.
   - **Step 3**: On-chain Blockchain Transaction Hash & Polygonscan Explorer Link.
3. Open `output/verification_report.json` and display the stored tamper-evident proof.
>>>>>>> 2244053 (feat: Add Face ID + Blockchain Verification Pipeline)
