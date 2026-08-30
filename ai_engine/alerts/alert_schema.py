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
    confidence_type="xgboost_softmax_probability",
    detector_status=None,
    telemetry_completeness=None,
    unavailable_features=None,
    heuristic_threat_type=None,
):
    """
    Create the standardized Anvex AI alert.

    Parameters
    ----------
    threat_type : str
        The predicted threat class (from XGBoost label_names).
    severity : str
        CRITICAL | HIGH | MEDIUM | LOW
    threat_score : float
        Composite score from threat_scorer (0.0 – 1.0).
    confidence : float
        The raw XGBoost softmax probability for the predicted class.
    features : dict
        The 13-feature input vector.
    explanation : dict, optional
        SHAP values keyed by feature name.
    source_ip : str, optional
    destination_ip : str, optional
    confidence_type : str
        IMPORTANT: Describes exactly what 'confidence' represents.
        DO NOT claim this is calibrated probability unless it has been
        calibrated via Platt scaling or isotonic regression.
        Default: "xgboost_softmax_probability"
        Possible values:
            "xgboost_softmax_probability"  -- raw XGBoost class probability
            "detector_heuristic_score"     -- heuristic detector score
            "composite_score"              -- combination of signals
    detector_status : dict, optional
        Per-detector status (e.g. {'dga': 'insufficient_data', 'exfil': 'abstained'})
    telemetry_completeness : str, optional
        Summary of data availability: 'full' | 'partial' | 'degraded'
    unavailable_features : list, optional
        List of feature names that could not be computed from upstream data.
    """

    alert = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "threat_detected": severity != "LOW",
        "threat_type": threat_type,
        "severity": severity,
        "threat_score": round(float(threat_score), 4),
        "confidence": round(float(confidence), 4),
        "confidence_type": confidence_type,
        "features": features,
        "explanation": explanation or {},
    }

    if source_ip is not None:
        alert["source_ip"] = source_ip

    if destination_ip is not None:
        alert["destination_ip"] = destination_ip

    if detector_status is not None:
        alert["detector_status"] = detector_status

    if telemetry_completeness is not None:
        alert["telemetry_completeness"] = telemetry_completeness

    if unavailable_features is not None:
        alert["unavailable_features"] = unavailable_features

    if heuristic_threat_type is not None:
        alert["heuristic_threat_type"] = heuristic_threat_type

    return alert