import hashlib
import json
from .models import Content

def generate_canonical_hash(data: Content) -> bytes:
    """
    Generates a deterministic SHA-256 hash of a JSON dictionary.
    Keys are sorted, and no extra whitespace is added.
    """
    # canonical JSON string
    canonical_string = json.dumps(data, sort_keys=True, separators=(',', ':'))
    # utf-8 bytes
    encoded_string = canonical_string.encode('utf-8')
    # sha256 hash
    hash_obj = hashlib.sha256(encoded_string)
    
    return hash_obj.digest()
