import pytest
from src.blockchain.client import BlockchainClient
from src.blockchain.verifier import verify_content
from src.blockchain.hasher import generate_canonical_hash

@pytest.fixture
def client():
    client = BlockchainClient()
    client.deploy_contract()
    return client

def test_verify_authentic_content(client):
    content = {
        "author": "john_doe",
        "image_url": "https://example.com/image.png",
        "post_id": "999"
    }
    
    # Register first
    canonical_hash = generate_canonical_hash(content)
    client.register_content(canonical_hash, "https://example.com/post/999")
    
    # Verify
    result = verify_content(client, content)
    
    assert result["verified"] is True
    assert result["reason"] == "VERIFIED"
    assert result["local_hash"] == canonical_hash.hex()

def test_verify_tampered_content(client):
    original_content = {
        "author": "john_doe",
        "image_url": "https://example.com/image.png",
        "post_id": "999"
    }
    
    # Register original
    canonical_hash = generate_canonical_hash(original_content)
    client.register_content(canonical_hash, "https://example.com/post/999")
    
    # Tamper with the content
    tampered_content = original_content.copy()
    tampered_content["author"] = "hacker"
    
    # Verify tampered
    result = verify_content(client, tampered_content)
    
    assert result["verified"] is False
    assert "TAMPERED" in result["reason"]
