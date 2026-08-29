import joblib
import pandas as pd
import shap


MODEL_PATH = "ai_engine/models/xgboost_model.joblib"


def explain_prediction(features):
    """
    Generate SHAP feature contributions for an XGBoost prediction.
    """

    model_package = joblib.load(MODEL_PATH)

    model = model_package["model"]
    feature_names = model_package["feature_names"]
    label_names = model_package["label_names"]

    X = pd.DataFrame(
        [[features[name] for name in feature_names]],
        columns=feature_names,
    )

    # Get model prediction
    predicted_id = int(model.predict(X)[0])
    predicted_label = label_names[predicted_id]

    # Create SHAP explainer
    explainer = shap.TreeExplainer(model)

    shap_values = explainer.shap_values(X)

    # SHAP 0.52 with multiclass XGBoost can return:
    # (samples, features, classes)
    if hasattr(shap_values, "ndim") and shap_values.ndim == 3:
        values = shap_values[0, :, predicted_id]

    # Older SHAP versions may return:
    # list[class] -> (samples, features)
    elif isinstance(shap_values, list):
        values = shap_values[predicted_id][0]

    # Binary/single-output case
    else:
        values = shap_values[0]

    contributions = {
        feature: float(value)
        for feature, value in zip(feature_names, values)
    }

    # Sort by absolute contribution
    contributions = dict(
        sorted(
            contributions.items(),
            key=lambda item: abs(item[1]),
            reverse=True,
        )
    )

    return {
        "prediction": predicted_label,
        "shap_values": contributions,
    }