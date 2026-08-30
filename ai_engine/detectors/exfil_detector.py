from ai_engine.features.exfil_features import extract_exfil_features


def detect_exfil(
    outbound_bytes,
    inbound_bytes,
    current_volume,
    baseline_volume
):
    """
    Baseline data-exfiltration detector.

    Uses:
    - Outbound/inbound byte ratio  (asymmetric outbound traffic)
    - Traffic volume baseline ratio (anomalous volume vs history)

    Detection policy
    ----------------
    Both signals are independent:
      - byte_ratio  >= 5.0 -> score += 0.5  (high outbound asymmetry)
      - volume_ratio >= 3.0 -> score += 0.5  (volume spike vs baseline)

    Abstention policy
    -----------------
    - If outbound_bytes == 0 AND inbound_bytes == 0: return insufficient_data.
      Zero bytes are not evidence of low exfiltration — they indicate missing
      payload data (orig_bytes_missing=1 in Zeek events).
    - If baseline_volume is None (unavailable): the volume_baseline_ratio
      signal is suppressed — missing baseline must NOT contribute evidence.

    Limitations
    -----------
    - The exfiltration scenario currently has all orig_bytes=resp_bytes=0
      (marked orig_bytes_missing=1). Detection is structurally impossible
      until the upstream PCAP carries actual payload bytes.
    - volume_baseline_ratio always produces 0.0 when no historical baseline
      is available from the pipeline (pass baseline_volume=None to signal this).
    """

    features = extract_exfil_features(
        outbound_bytes=outbound_bytes,
        inbound_bytes=inbound_bytes,
        current_volume=current_volume,
        baseline_volume=baseline_volume,
    )

    byte_ratio = features["outbound_inbound_ratio"]
    volume_ratio = features["volume_baseline_ratio"]
    baseline_available = features.get("baseline_available", False)

    # Abstain: bytes are missing — we have no payload evidence.
    if outbound_bytes == 0 and inbound_bytes == 0:
        return {
            "detector": "exfiltration",
            "detected": False,
            "score": 0.0,
            "features": features,
            "status": "insufficient_data",
            "limitation": (
                "Exfiltration detection requires non-zero byte counts. "
                "Current scenario has orig_bytes=resp_bytes=0 "
                "(orig_bytes_missing=1 in Zeek events). "
                "Cannot detect exfiltration without payload data."
            ),
        }

    score = 0.0
    evidence = []

    # Signal 1: asymmetric outbound ratio.
    if byte_ratio >= 5:
        score += 0.5
        evidence.append(
            f"outbound/inbound ratio = {byte_ratio:.2f} (>= 5.0 threshold)"
        )

    # Signal 2: volume anomaly vs baseline (only if baseline is available).
    if baseline_available:
        if volume_ratio >= 3:
            score += 0.5
            evidence.append(
                f"volume/baseline ratio = {volume_ratio:.2f} (>= 3.0 threshold)"
            )
    else:
        # No baseline: cannot evaluate volume signal.
        evidence.append(
            "volume_baseline_ratio: UNAVAILABLE (no historical baseline in pipeline)"
        )

    detected = score >= 0.5

    result = {
        "detector": "exfiltration",
        "detected": detected,
        "score": score,
        "features": features,
        "status": "evaluated",
        "baseline_available": baseline_available,
        "evidence": evidence,
    }

    if detected:
        result["explanation"] = (
            f"Exfiltration indicators: {'; '.join(evidence)}. "
            f"outbound={outbound_bytes:.0f}B, inbound={inbound_bytes:.0f}B."
        )

    return result