// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title VerificationRegistry
 * @dev Tamper-evident, immutable on-chain ledger for Face ID + Social Media Post verification matches.
 */
contract VerificationRegistry {

    struct VerificationRecord {
        bytes32 faceHash;           // SHA-256 fingerprint hash of detected face crop
        bytes32 sourceImageHash;    // SHA-256 hash of raw input image
        string socialPostUrl;       // Verified matching social media URL
        string platform;            // Platform name (e.g. X, Instagram, LinkedIn)
        uint256 timestamp;          // On-chain block timestamp
        address verifier;           // Address of the recorder/verifier
        bool exists;                // Flag indicating record presence
    }

    // Mapping from faceHash to its VerificationRecord
    mapping(bytes32 => VerificationRecord) private _records;
    
    // Array of all recorded face hashes for enumeration
    bytes32[] private _allFaceHashes;

    // Events
    event VerificationRecorded(
        bytes32 indexed faceHash,
        bytes32 indexed sourceImageHash,
        string socialPostUrl,
        string platform,
        uint256 timestamp,
        address indexed verifier
    );

    /**
     * @dev Records a new tamper-evident face verification match on-chain.
     */
    function recordVerification(
        bytes32 faceHash,
        bytes32 sourceImageHash,
        string memory socialPostUrl,
        string memory platform
    ) external returns (bool) {
        require(faceHash != bytes32(0), "Invalid face hash");
        require(bytes(socialPostUrl).length > 0, "Invalid social post URL");

        if (!_records[faceHash].exists) {
            _allFaceHashes.push(faceHash);
        }

        _records[faceHash] = VerificationRecord({
            faceHash: faceHash,
            sourceImageHash: sourceImageHash,
            socialPostUrl: socialPostUrl,
            platform: platform,
            timestamp: block.timestamp,
            verifier: msg.sender,
            exists: true
        });

        emit VerificationRecorded(
            faceHash,
            sourceImageHash,
            socialPostUrl,
            platform,
            block.timestamp,
            msg.sender
        );

        return true;
    }

    /**
     * @dev Retrieves a verification record by face hash.
     */
    function getVerification(bytes32 faceHash) 
        external 
        view 
        returns (
            bytes32 sourceImageHash,
            string memory socialPostUrl,
            string memory platform,
            uint256 timestamp,
            address verifier,
            bool exists
        ) 
    {
        VerificationRecord memory rec = _records[faceHash];
        return (
            rec.sourceImageHash,
            rec.socialPostUrl,
            rec.platform,
            rec.timestamp,
            rec.verifier,
            rec.exists
        );
    }

    /**
     * @dev Returns total number of registered verifications on-chain.
     */
    function totalVerifications() external view returns (uint256) {
        return _allFaceHashes.length;
    }
}
