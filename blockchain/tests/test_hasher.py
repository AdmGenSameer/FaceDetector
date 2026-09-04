import pytest
from src.blockchain.hasher import generate_canonical_hash

def test_canonical_hash_ignores_key_order():
    # Two dicts with identical content but different key orders
    data1 = {
        "user": "alice",
        "post_id": 12345,
        "metadata": {
            "platform": "instagram",
            "date": "2026-10-01"
        }
    }
    
    data2 = {
        "metadata": {
            "date": "2026-10-01",
            "platform": "instagram"
        },
        "post_id": 12345,
        "user": "alice"
    }

    hash1 = generate_canonical_hash(data1)
    hash2 = generate_canonical_hash(data2)
    
    assert hash1 == hash2

def test_canonical_hash_is_deterministic():
    data = {"a": 1, "b": 2}
    hash1 = generate_canonical_hash(data)
    hash2 = generate_canonical_hash(data)
    
    assert hash1 == hash2

def test_different_content_produces_different_hashes():
    data1 = {"a": 1, "b": 2}
    data2 = {"a": 1, "b": 3}
    
    hash1 = generate_canonical_hash(data1)
    hash2 = generate_canonical_hash(data2)
    
    assert hash1 != hash2
