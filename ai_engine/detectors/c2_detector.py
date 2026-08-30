from ai_engine.features.c2_features import extract_c2_features


# Minimum number of inter-arrival time samples required before the C2
# detector makes a positive claim.  With fewer samples, IAT variance and
# FFT periodicity are statistically unreliable.
_MIN_IAT_SAMPLES = 8

# IAT variance must be below this threshold to be considered "regular".
# Normal scenario IAT variance = ~0.096, so 0.05 is safely below that.
# C2 beacon scenario IAT variance = ~0.017, well within this bound.
# Set conservatively: do not lower further without real-traffic calibration.
_IAT_VARIANCE_THRESHOLD = 0.05

# FFT periodicity must exceed this threshold to support a beacon claim.
# Unchanged from original design.
_FFT_PERIODICITY_THRESHOLD = 0.40


def detect_c2(inter_arrival_times):
    """
    Baseline C2 beaconing detector.

    Uses:
    - IAT variance      (regularity of timing)
    - FFT periodicity   (dominant frequency signal)

    Detection policy (JOINT evidence required):
    -------------------------------------------
    Both conditions must be satisfied simultaneously:
      1.  >= _MIN_IAT_SAMPLES inter-arrival times available
      2.  iat_variance  <  _IAT_VARIANCE_THRESHOLD   (regular timing)
      3.  fft_periodicity >= _FFT_PERIODICITY_THRESHOLD (strong frequency peak)

    Rationale: iat_variance alone is insufficient.  With fewer than
    _MIN_IAT_SAMPLES samples the statistics are unreliable.  Requiring
    both low variance AND significant FFT periodicity prevents a single
    weak signal from generating a false positive.

    Limitations:
    - The normal scenario has IAT variance ~0.096 (above threshold).
    - The C2 scenario has IAT variance ~0.017 and FFT ~0.221.
    - FFT periodicity in both scenarios is below the 0.40 threshold,
      so the detector currently returns score=0.0 / not-detected for both.
    - This is intentionally conservative: insufficient periodicity evidence
      should NOT fire, even when timing is regular.
    - A higher-confidence C2 signal requires a longer observation window
      with a cleaner beacon pattern.

    False positive guard:
    ---------------------
    Do NOT lower _IAT_VARIANCE_THRESHOLD to catch more cases without
    verifying against real normal traffic data first.
    """

    n = len(inter_arrival_times)

    features = extract_c2_features(inter_arrival_times)

    iat_variance = features["iat_variance"]
    fft_periodicity = features["fft_periodicity"]

    # Insufficient data: cannot make a reliable claim.
    if n < _MIN_IAT_SAMPLES:
        return {
            "detector": "c2_beacon",
            "detected": False,
            "score": 0.0,
            "features": features,
            "status": "insufficient_data",
            "limitation": (
                f"C2 detection requires >= {_MIN_IAT_SAMPLES} inter-arrival "
                f"time samples. Only {n} available. Result: abstain."
            ),
        }

    score = 0.0

    # Condition 1: Regular timing (low variance).
    # Both conditions contribute 0.5 each — BOTH must fire to reach detected.
    timing_regular = iat_variance < _IAT_VARIANCE_THRESHOLD
    if timing_regular:
        score += 0.5

    # Condition 2: Strong periodic signal in frequency domain.
    strong_periodicity = fft_periodicity >= _FFT_PERIODICITY_THRESHOLD
    if strong_periodicity:
        score += 0.5

    detected = score >= 1.0  # Requires BOTH conditions.

    result = {
        "detector": "c2_beacon",
        "detected": detected,
        "score": score,
        "features": features,
        "status": "evaluated",
        "iat_samples": n,
        "timing_regular": timing_regular,
        "strong_periodicity": strong_periodicity,
    }

    if detected:
        result["explanation"] = (
            f"C2 beacon detected: IAT variance {iat_variance:.6f} < "
            f"{_IAT_VARIANCE_THRESHOLD} (regular timing) AND FFT periodicity "
            f"{fft_periodicity:.4f} >= {_FFT_PERIODICITY_THRESHOLD} "
            f"(dominant periodic component). {n} IAT samples."
        )

    return result