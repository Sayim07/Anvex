from ai_engine.features.c2_features import extract_c2_features


def detect_c2(inter_arrival_times):
    """
    Initial baseline C2 beaconing detector.

    Uses:
    - IAT variance
    - FFT periodicity
    """

    features = extract_c2_features(inter_arrival_times)

    iat_variance = features["iat_variance"]
    fft_periodicity = features["fft_periodicity"]

    score = 0.0

    # Regular timing can indicate beacon-like behavior.
    if iat_variance <= 1.0:
        score += 0.5

    if fft_periodicity >= 0.4:
        score += 0.5

    detected = score >= 0.5

    return {
        "detector": "c2_beacon",
        "detected": detected,
        "score": score,
        "features": features,
    }