from ai_engine.models.inference import predict
from ai_engine.explainability.shap_explainer import explain_prediction
from ai_engine.scoring.threat_scorer import assess_threat
from ai_engine.alerts.alert_schema import create_alert


def run_ai_pipeline(
    detector_result,
    features,
    source_ip=None,
    destination_ip=None,
):
    """
    Run the complete Anvex AI processing pipeline.

    Flow:
        detector
        -> XGBoost + Isolation Forest
        -> SHAP
        -> threat scoring
        -> standardized alert
    """

    # -------------------------
    # ML inference
    # -------------------------

    ml_result = predict(features)

    # -------------------------
    # SHAP explanation
    # -------------------------

    explanation = ml_result.get("explanation", {})

    # -------------------------
    # Unified threat score
    # -------------------------

    threat_assessment = assess_threat(
    detector_score=detector_result["score"],
    xgboost_confidence=ml_result["xgboost_confidence"],
    xgboost_prediction=ml_result["xgboost_prediction"],
    anomaly_prediction=ml_result["anomaly_prediction"],
)

    # -------------------------
    # Standardized alert
    # -------------------------

    alert = create_alert(
        threat_type=ml_result["xgboost_prediction"],
        severity=threat_assessment["severity"],
        threat_score=threat_assessment["threat_score"],
        confidence=ml_result["xgboost_confidence"],
        features=features,
        explanation=explanation,
        source_ip=source_ip,
        destination_ip=destination_ip,
    )

    return alert