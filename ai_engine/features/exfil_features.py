def calculate_outbound_inbound_ratio(outbound_bytes, inbound_bytes):
    """Calculate outbound-to-inbound byte ratio."""

    if inbound_bytes <= 0:
        return float(outbound_bytes)

    return outbound_bytes / inbound_bytes


def calculate_volume_baseline(current_volume, baseline_volume):
    """Compare current traffic volume against its baseline."""

    if baseline_volume <= 0:
        return 0.0

    return current_volume / baseline_volume


def extract_exfil_features(
    outbound_bytes,
    inbound_bytes,
    current_volume,
    baseline_volume,
):
    return {
        "outbound_inbound_ratio": calculate_outbound_inbound_ratio(
            outbound_bytes,
            inbound_bytes,
        ),
        "volume_baseline_ratio": calculate_volume_baseline(
            current_volume,
            baseline_volume,
        ),
    }