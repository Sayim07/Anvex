from ai_engine.features.scan_features import extract_scan_features


def detect_port_scan(
    destination_ports,
    failed_connections,
    total_connections
):
    """
    Initial baseline Port Scan detector.

    Uses:
    - Destination port fan-out
    - Connection failure rate
    """

    features = extract_scan_features(
        destination_ports=destination_ports,
        failed_connections=failed_connections,
        total_connections=total_connections,
    )

    port_fanout = features["port_fanout"]
    failure_rate = features["connection_failure_rate"]

    score = 0.0

    # Development thresholds only.
    if port_fanout >= 10:
        score += 0.5

    if failure_rate >= 0.5:
        score += 0.5

    detected = score >= 0.5

    return {
        "detector": "port_scan",
        "detected": detected,
        "score": score,
        "features": features,
    }