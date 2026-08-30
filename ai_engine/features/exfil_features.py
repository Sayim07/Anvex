def calculate_outbound_inbound_ratio(outbound_bytes, inbound_bytes):
    """Calculate outbound-to-inbound byte ratio.

    Returns 0.0 when both are 0 (missing bytes — not evidence of low ratio).
    """

    if inbound_bytes <= 0:
        # If inbound is 0 but outbound is also 0, ratio is undefined / zero.
        if outbound_bytes <= 0:
            return 0.0
        # Outbound only — asymmetric but not numerically representable as ratio.
        # Return outbound_bytes as a proxy (large values still detectable).
        return float(outbound_bytes)

    return outbound_bytes / inbound_bytes


def calculate_volume_baseline(current_volume, baseline_volume):
    """Compare current traffic volume against its baseline.

    Returns 0.0 if baseline_volume is None (unavailable) or <= 0.
    Callers should check 'baseline_available' in the feature dict.
    """

    if baseline_volume is None or baseline_volume <= 0:
        return 0.0

    return current_volume / baseline_volume


def extract_exfil_features(
    outbound_bytes,
    inbound_bytes,
    current_volume,
    baseline_volume,
):
    """
    Extract exfiltration features.

    Parameters
    ----------
    outbound_bytes : float
        Total originator bytes (must be from non-missing events only).
    inbound_bytes : float
        Total responder bytes (must be from non-missing events only).
    current_volume : float
        Sum of outbound + inbound.
    baseline_volume : float or None
        Historical baseline total bytes.  Pass None if no baseline exists.
        CRITICAL: do NOT pass current_volume as the baseline — that always
        produces ratio=1.0 which is semantically meaningless.

    Returns
    -------
    dict with keys:
        outbound_inbound_ratio : float  (0.0 if bytes unavailable)
        volume_baseline_ratio  : float  (0.0 if baseline unavailable)
        baseline_available     : bool   (False when baseline_volume is None)
    """
    return {
        "outbound_inbound_ratio": calculate_outbound_inbound_ratio(
            outbound_bytes,
            inbound_bytes,
        ),
        "volume_baseline_ratio": calculate_volume_baseline(
            current_volume,
            baseline_volume,
        ),
        "baseline_available": baseline_volume is not None and baseline_volume > 0,
    }