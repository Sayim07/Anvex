def calculate_threat_score(
    detector_score,
    xgboost_confidence,
    xgboost_prediction,
    anomaly_prediction,
):
    """
    Calculate a unified threat score.

    XGBoost confidence contributes to the threat score only
    when the predicted class is not normal.

    This is an initial development scoring policy and will
    be calibrated using real validation data later.
    """

    score = 0.0

    # Detector contribution
    score += 0.5 * detector_score

    # XGBoost contribution
    # Confidence in "normal" is NOT a threat signal.
    if xgboost_prediction != "normal":
        score += 0.4 * xgboost_confidence

    # Isolation Forest anomaly contribution
    if anomaly_prediction == -1:
        score += 0.1

    return min(score, 1.0)


def classify_severity(score):
    """
    Convert normalized threat score into severity.
    """

    if score < 0.25:
        return "LOW"

    if score < 0.50:
        return "MEDIUM"

    if score < 0.75:
        return "HIGH"

    return "CRITICAL"


def assess_threat(
    detector_score,
    xgboost_confidence,
    xgboost_prediction,
    anomaly_prediction,
):
    """
    Return unified threat score and severity.
    """

    score = calculate_threat_score(
        detector_score=detector_score,
        xgboost_confidence=xgboost_confidence,
        xgboost_prediction=xgboost_prediction,
        anomaly_prediction=anomaly_prediction,
    )

    severity = classify_severity(score)

    return {
        "threat_score": round(score, 4),
        "severity": severity,
    }