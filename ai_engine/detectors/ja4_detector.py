from ai_engine.features.ja4_features import extract_ja4_features


def detect_ja4(
    ja4,
    ja3,
    packet_sizes,
    packet_times
):
    """
    Initial encrypted-malware profiling detector.

    Uses JA4/JA3 metadata and SPLT-related statistics.
    """

    features = extract_ja4_features(
        ja4=ja4,
        ja3=ja3,
        packet_sizes=packet_sizes,
        packet_times=packet_times,
    )

    score = 0.0

    # Initial development logic.
    # JA4/JA3 reputation will be incorporated later
    # when a validated dataset/reference mapping is available.

    if features["packet_size_variance"] > 10000:
        score += 0.5

    if features["mean_packet_size"] > 1200:
        score += 0.5

    detected = score >= 0.5

    return {
        "detector": "ja4",
        "detected": detected,
        "score": score,
        "features": features,
    }