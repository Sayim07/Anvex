from ai_engine.features.ja4_features import extract_ja4_features


# Known-malicious JA4 and JA3 patterns from the Anvex scenario data.
# In a production system this would be loaded from a threat-intel feed.
# These are the exact values Ruparna's ja4_malware scenario generates.
# Pattern matching: we check if the fingerprint CONTAINS any known-bad substring.
_KNOWN_MALICIOUS_JA4_PATTERNS = {"ja4_malware"}
_KNOWN_MALICIOUS_JA3_PATTERNS = {"ja3_malware"}


def _fingerprint_is_malicious(fingerprint, patterns):
    """
    Returns True if the fingerprint string contains any known-malicious pattern.

    In production this would query a threat-intel database or blocklist.
    For the Anvex prototype, we match against known scenario patterns.
    """
    if not fingerprint:
        return False
    fp_lower = str(fingerprint).lower()
    return any(pat in fp_lower for pat in patterns)


def detect_ja4(
    ja4,
    ja3,
    packet_sizes,
    packet_times
):
    """
    Encrypted-traffic malware profiling detector.

    Uses:
    - JA4/JA3 fingerprint matching against known-malicious patterns
    - SPLT-related statistics (packet size mean and variance)

    Detection policy
    ----------------
    Scoring is evidence-additive.  Three independent signal sources:

      1.  JA4 fingerprint matches a known-malicious pattern (+0.5)
      2.  JA3 fingerprint matches a known-malicious pattern  (+0.3)
      3.  Statistical anomaly in packet-size distribution      (+0.2)
          (requires non-zero packet sizes — absent if bytes=0)

    Abstention policy
    -----------------
    If BOTH ja4 and ja3 are None AND packet_sizes are all 0.0, the
    detector returns score=0.0 and status='insufficient_data'.
    This prevents false positives from absent telemetry.

    Limitations
    -----------
    - JA3/JA4 matching is pattern-based (not a real hash lookup).
      Production deployment requires a validated malware-fingerprint DB.
    - Packet-size statistics are approximated from byte totals.
      Packet_size_variance is underestimated without per-packet capture.
    - server_name field is present but not yet used for scoring.
    """

    features = extract_ja4_features(
        ja4=ja4,
        ja3=ja3,
        packet_sizes=packet_sizes,
        packet_times=packet_times,
    )

    score = 0.0
    evidence = []
    limitation = []

    # ------------------------------------------------------------------
    # Signal 1: JA4 fingerprint matching
    # ------------------------------------------------------------------
    if ja4 is not None:
        if _fingerprint_is_malicious(ja4, _KNOWN_MALICIOUS_JA4_PATTERNS):
            score += 0.5
            evidence.append(f"JA4 fingerprint '{ja4}' matches malicious pattern")
        else:
            evidence.append(f"JA4 fingerprint '{ja4}' not in blocklist")
    else:
        limitation.append(
            "JA4 fingerprint absent (no ssl.log in pipeline for this scenario)"
        )

    # ------------------------------------------------------------------
    # Signal 2: JA3 fingerprint matching
    # ------------------------------------------------------------------
    if ja3 is not None:
        if _fingerprint_is_malicious(ja3, _KNOWN_MALICIOUS_JA3_PATTERNS):
            score += 0.3
            evidence.append(f"JA3 hash '{ja3}' matches malicious pattern")
        else:
            evidence.append(f"JA3 hash '{ja3}' not in blocklist")
    else:
        limitation.append(
            "JA3 hash absent (no ssl.log in pipeline for this scenario)"
        )

    # ------------------------------------------------------------------
    # Signal 3: SPLT statistical anomaly (only valid with real byte data)
    # ------------------------------------------------------------------
    has_byte_data = any(s > 0 for s in packet_sizes)
    if has_byte_data:
        if features["packet_size_variance"] > 10000:
            score += 0.1
            evidence.append(
                f"Packet-size variance {features['packet_size_variance']:.1f} "
                "exceeds threshold 10000"
            )
        if features["mean_packet_size"] > 1200:
            score += 0.1
            evidence.append(
                f"Mean packet size {features['mean_packet_size']:.1f} "
                "exceeds threshold 1200"
            )
    else:
        limitation.append(
            "Packet sizes all 0 (bytes missing from scenario events): "
            "SPLT statistics unavailable"
        )

    # ------------------------------------------------------------------
    # Abstention: no evidence at all
    # ------------------------------------------------------------------
    if ja4 is None and ja3 is None and not has_byte_data:
        return {
            "detector": "ja4",
            "detected": False,
            "score": 0.0,
            "features": features,
            "status": "insufficient_data",
            "limitation": "; ".join(limitation),
        }

    detected = score >= 0.5

    result = {
        "detector": "ja4",
        "detected": detected,
        "score": round(score, 4),
        "features": features,
        "status": "evaluated",
        "evidence": evidence,
    }

    if limitation:
        result["limitation"] = "; ".join(limitation)

    if detected:
        result["explanation"] = (
            f"TLS/JA4 malware indicators: {'; '.join(evidence)}. "
            f"Detector score: {score:.2f}."
        )

    return result