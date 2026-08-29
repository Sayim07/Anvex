from datetime import datetime, timezone


def create_alert(
    threat_type,
    severity,
    threat_score,
    confidence,
    features,
    explanation=None,
    source_ip=None,
    destination_ip=None,
):
    """
    Create the standardized Anvex AI alert.
    """

    alert = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "threat_detected": severity != "LOW",
        "threat_type": threat_type,
        "severity": severity,
        "threat_score": round(float(threat_score), 4),
        "confidence": round(float(confidence), 4),
        "features": features,
        "explanation": explanation or {},
    }

    if source_ip is not None:
        alert["source_ip"] = source_ip

    if destination_ip is not None:
        alert["destination_ip"] = destination_ip

    return alert