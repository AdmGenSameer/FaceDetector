import pytest
from src.blockchain.client import BlockchainClient
from web3.exceptions import ContractLogicError

@pytest.fixture
def client():
    # Will use eth-tester automatically if RPC_URL is not set
    # Note: we assume deploy.py has been run and ContentRegistry.json exists
    client = BlockchainClient()
    client.deploy_contract()
    return client

def test_register_and_retrieve(client):
    mock_hash = b'\x01' * 32
    source = "https://instagram.com/p/mock123"
    
    # Register
    tx_hash = client.register_content(mock_hash, source)
    assert tx_hash is not None
    
    # Retrieve
    record = client.get_record(mock_hash)
    
    assert record["exists"] is True
    assert record["source"] == source
    assert record["submitter"] == client.account
    assert record["timestamp"] > 0

def test_duplicate_registration_fails(client):
    mock_hash = b'\x02' * 32
    source = "https://instagram.com/p/mock456"
    
    # First registration should succeed
    client.register_content(mock_hash, source)
    
    # Second registration of the same hash should fail
    with pytest.raises(Exception, match="Content hash already registered"):
        client.register_content(mock_hash, source)
