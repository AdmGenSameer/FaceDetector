from typing import Dict, Any
from .hasher import generate_canonical_hash
from .models import Content

def verify_content(client, data: Content) -> Dict[str, Any]:
    """
    Verifies if the canonical hash of the data exists on the blockchain.
    """
    # 1. Generate canonical hash
    canonical_hash = generate_canonical_hash(data)
    
    # 2. Check blockchain
    try:
        record = client.get_record(canonical_hash)
    except Exception as e:
        return {
            "verified": False,
            "local_hash": canonical_hash.hex(),
            "blockchain_hash": None,
            "reason": f"Error fetching from blockchain: {str(e)}"
        }
        
    if not record["exists"]:
        return {
            "verified": False,
            "local_hash": canonical_hash.hex(),
            "blockchain_hash": None,
            "reason": "Hash not found on blockchain (TAMPERED or NEVER REGISTERED)"
        }
        
    return {
        "verified": True,
        "local_hash": canonical_hash.hex(),
        "blockchain_hash": canonical_hash.hex(),
        "reason": "VERIFIED",
        "record": {
            "source": record["source"],
            "timestamp": record["timestamp"],
            "submitter": record["submitter"]
        }
    }
