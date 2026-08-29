from ai_engine.scoring.threat_scorer import assess_threat


result = assess_threat(
    detector_score=1.0,
    xgboost_confidence=0.998847,
    xgboost_prediction="ddos",
    anomaly_prediction=1,
)


print("Threat Assessment:")
print(result)