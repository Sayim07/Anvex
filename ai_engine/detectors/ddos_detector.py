from ai_engine.features.ddos_features import extract_ddos_features


def detect_ddos(
    source_ips,
    packet_count,
    duration_seconds,
    syn_count,
    ack_count
):
    """
    Perform an initial DDoS assessment using
    the features defined in the Anvex architecture.

    This is a baseline heuristic detector.
    ML-based detection will be added later.
    """

    features = extract_ddos_features(
        source_ips=source_ips,
        packet_count=packet_count,
        duration_seconds=duration_seconds,
        syn_count=syn_count,
        ack_count=ack_count,
    )

    pps = features["pps"]
    syn_ack_ratio = features["syn_ack_ratio"]
    source_ip_entropy = features["source_ip_entropy"]

    score = 0.0

    # Initial baseline thresholds.
    # These are development thresholds,
    # not final production thresholds.

    if pps >= 1000:
        score += 0.4

    if syn_ack_ratio >= 5:
        score += 0.3

    if source_ip_entropy >= 2:
        score += 0.3

    detected = score >= 0.5

    return {
        "detector": "ddos",
        "detected": detected,
        "score": score,
        "features": features,
    }