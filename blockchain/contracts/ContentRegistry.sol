// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract ContentRegistry {
    
    struct ContentRecord {
        bytes32 contentHash;
        string source;
        uint256 timestamp;
        address submitter;
        bool exists;
    }

    // Mapping from data hash to its ContentRecord
    mapping(bytes32 => ContentRecord) private _records;

    // Event emitted when a new record is stored
    event ContentRegistered(
        bytes32 indexed contentHash,
        string source,
        uint256 timestamp,
        address indexed submitter
    );

    /**
     * @dev Stores a hash of the discovered data on the blockchain.
     * @param contentHash The canonical SHA-256 hash of the face/social media data.
     * @param source Metadata or source identifier for the hash.
     */
    function registerContent(bytes32 contentHash, string calldata source) external {
        // Option A: Reject duplicate hashes. This gives a cleaner provenance model
        // as it establishes a definitive "first seen" timestamp.
        require(!_records[contentHash].exists, "Content hash already registered");

        _records[contentHash] = ContentRecord({
            contentHash: contentHash,
            source: source,
            timestamp: block.timestamp,
            submitter: msg.sender,
            exists: true
        });

        emit ContentRegistered(contentHash, source, block.timestamp, msg.sender);
    }

    /**
     * @dev Verifies if a given hash exists on-chain and returns the record.
     * @param contentHash The hash to verify.
     */
    function getRecord(bytes32 contentHash) external view returns (
        bool exists,
        string memory source,
        uint256 timestamp,
        address submitter
    ) {
        ContentRecord memory record = _records[contentHash];
        return (record.exists, record.source, record.timestamp, record.submitter);
    }
}
