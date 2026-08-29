// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title ForensicAuditLedger
 * @notice Anvex — Tamper-evident on-chain notarization of AI-detected cyber threats.
 * @dev Each alert is stored by its alertId. The alertHash is the SHA-256 digest of the
 *      complete JSON payload, providing cryptographic proof that the payload has not
 *      been altered after notarization.
 */
contract ForensicAuditLedger {
    // -------------------------------------------------------------------------
    // Data Structures
    // -------------------------------------------------------------------------

    struct AlertRecord {
        bytes32 alertHash;    // SHA-256 of the complete alert JSON payload
        string  alertId;      // Unique alert identifier (e.g., "FL-<uuid>")
        string  threatClass;  // e.g., "DDOS", "PORT_SCAN", "C2_BEACON"
        uint16  confidence;   // Scaled by 100: 9650 == 96.50%
        uint256 timestamp;    // block.timestamp at time of notarization
        bool    exists;       // Sentinel to distinguish zero-value from missing
    }

    // -------------------------------------------------------------------------
    // State
    // -------------------------------------------------------------------------

    /// @dev Maps alertId -> AlertRecord
    mapping(string => AlertRecord) private _alerts;

    /// @dev Owner of the contract (deployer)
    address public immutable owner;

    // -------------------------------------------------------------------------
    // Events
    // -------------------------------------------------------------------------

    /**
     * @notice Emitted when a new threat alert is successfully notarized.
     * @param alertId    The unique alert identifier.
     * @param alertHash  SHA-256 digest of the alert payload.
     * @param threatClass Threat category string.
     * @param timestamp  Block timestamp of notarization.
     */
    event AlertNotarized(
        string indexed alertId,
        bytes32        alertHash,
        string         threatClass,
        uint256        timestamp
    );

    // -------------------------------------------------------------------------
    // Errors
    // -------------------------------------------------------------------------

    error AlertAlreadyExists(string alertId);
    error AlertNotFound(string alertId);

    // -------------------------------------------------------------------------
    // Constructor
    // -------------------------------------------------------------------------

    constructor() {
        owner = msg.sender;
    }

    // -------------------------------------------------------------------------
    // Write Functions
    // -------------------------------------------------------------------------

    /**
     * @notice Notarize a new threat alert on-chain.
     * @dev Any caller may notarize; in production, restrict to a trusted relayer.
     * @param _alertId     Unique alert identifier.
     * @param _alertHash   SHA-256 hash of the complete JSON payload (as bytes32).
     * @param _threatClass Human-readable threat category.
     * @param _confidence  Detection confidence scaled by 100 (e.g., 9650 = 96.50%).
     * @return The stored alertHash for client-side confirmation.
     */
    function notarizeAlert(
        string  memory _alertId,
        bytes32        _alertHash,
        string  memory _threatClass,
        uint16         _confidence
    ) external returns (bytes32) {
        if (_alerts[_alertId].exists) {
            revert AlertAlreadyExists(_alertId);
        }

        _alerts[_alertId] = AlertRecord({
            alertHash:   _alertHash,
            alertId:     _alertId,
            threatClass: _threatClass,
            confidence:  _confidence,
            timestamp:   block.timestamp,
            exists:      true
        });

        emit AlertNotarized(_alertId, _alertHash, _threatClass, block.timestamp);

        return _alertHash;
    }

    // -------------------------------------------------------------------------
    // View Functions
    // -------------------------------------------------------------------------

    /**
     * @notice Retrieve an alert record for forensic verification.
     * @param _alertId The alert identifier to look up.
     * @return alertHash   The stored SHA-256 payload hash.
     * @return threatClass The threat category.
     * @return confidence  Detection confidence (scaled × 100).
     * @return timestamp   Block timestamp when the alert was notarized.
     */
    function verifyAlert(string memory _alertId)
        external
        view
        returns (
            bytes32 alertHash,
            string  memory threatClass,
            uint16  confidence,
            uint256 timestamp
        )
    {
        if (!_alerts[_alertId].exists) {
            revert AlertNotFound(_alertId);
        }

        AlertRecord storage record = _alerts[_alertId];
        return (
            record.alertHash,
            record.threatClass,
            record.confidence,
            record.timestamp
        );
    }

    /**
     * @notice Check whether an alertId has been notarized.
     * @param _alertId The alert identifier to check.
     * @return True if the alert exists on-chain.
     */
    function alertExists(string memory _alertId) external view returns (bool) {
        return _alerts[_alertId].exists;
    }
}
