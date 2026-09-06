import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Load .env file if present
load_dotenv(BASE_DIR / ".env")

class Config:
    SERPAPI_KEY: str = os.getenv("SERPAPI_KEY", "")
    RPC_URL: str = os.getenv("RPC_URL", "https://rpc-amoy.polygon.technology")
    PRIVATE_KEY: str = os.getenv("PRIVATE_KEY", "")
    CONTRACT_ADDRESS: str = os.getenv("CONTRACT_ADDRESS", "")
    ALLOW_MOCK_FALLBACK: bool = os.getenv("ALLOW_MOCK_FALLBACK", "true").lower() == "true"
    
    # Polygon Amoy Explorer URL
    EXPLORER_BASE_URL: str = "https://amoy.polygonscan.com/tx/"

    @classmethod
    def validate(cls, check_blockchain: bool = False, check_serpapi: bool = False):
        warnings = []
        if check_serpapi and not cls.SERPAPI_KEY:
            warnings.append("[WARN] SERPAPI_KEY is missing. Genuine reverse image search will use fallback mock search if ALLOW_MOCK_FALLBACK is True.")
        if check_blockchain:
            if not cls.PRIVATE_KEY or cls.PRIVATE_KEY == "0x0000000000000000000000000000000000000000000000000000000000000000":
                warnings.append("[WARN] PRIVATE_KEY is missing or invalid. Blockchain writes will operate in dry-run mode.")
        return warnings
