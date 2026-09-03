from pathlib import Path

import joblib
import pandas as pd


XGBOOST_PATH = Path("ai_engine/models/xgboost_model.joblib")
ISOLATION_PATH = Path("ai_engine/models/isolation_forest.joblib")


def load_models():
    """Load the trained XGBoost and Isolation Forest models."""

    xgb_package = joblib.load(XGBOOST_PATH)
    isolation_package = joblib.load(ISOLATION_PATH)

    return xgb_package, isolation_package


def predict(features):
    """
    Run XGBoost and Isolation Forest on one feature vector.
    """

    xgb_package, isolation_package = load_models()

    feature_names = xgb_package["feature_names"]

    # Keep the feature order identical to training.
    X = pd.DataFrame(
        [[features[name] for name in feature_names]],
        columns=feature_names,
    )

    # -------------------------
    # XGBoost prediction
    # -------------------------

    xgb_model = xgb_package["model"]

    predicted_id = int(xgb_model.predict(X)[0])

    probabilities = xgb_model.predict_proba(X)[0]

    label_names = xgb_package["label_names"]

    predicted_label = label_names[predicted_id]

    xgb_confidence = float(probabilities[predicted_id])

    # -------------------------
    # Isolation Forest
    # -------------------------

    isolation_model = isolation_package["model"]

    anomaly_prediction = int(
        isolation_model.predict(X)[0]
    )

    anomaly_score = float(
        isolation_model.decision_function(X)[0]
    )

    from ai_engine.explainability.shap_explainer import explain_prediction
    explanation = explain_prediction(features)["shap_values"]

    return {
        "xgboost_prediction": predicted_label,
        "xgboost_confidence": xgb_confidence,
        "anomaly_prediction": anomaly_prediction,
        "anomaly_score": anomaly_score,
        "explanation": explanation,
    }