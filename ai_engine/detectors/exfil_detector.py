from ai_engine.features.exfil_features import extract_exfil_features


def detect_exfil(
    outbound_bytes,
    inbound_bytes,
    current_volume,
    baseline_volume
):
    """
    Initial baseline data-exfiltration detector.

    Uses:
    - Outbound/inbound byte ratio
    - Traffic volume baseline ratio
    """

    features = extract_exfil_features(
        outbound_bytes=outbound_bytes,
        inbound_bytes=inbound_bytes,
        current_volume=current_volume,
        baseline_volume=baseline_volume,
    )

    byte_ratio = features["outbound_inbound_ratio"]
    volume_ratio = features["volume_baseline_ratio"]

    score = 0.0

    if byte_ratio >= 5:
        score += 0.5

    if volume_ratio >= 3:
        score += 0.5

    detected = score >= 0.5

    return {
        "detector": "exfiltration",
        "detected": detected,
        "score": score,
        "features": features,
    }