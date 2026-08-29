from ai_engine.alerts.alert_schema import create_alert


result = create_alert(
    threat_type="DDoS",
    severity="CRITICAL",
    threat_score=0.8995,
    confidence=0.998847,
    features={
        "source_ip_entropy": 3.5,
        "pps": 5000,
        "syn_ack_ratio": 10,
    },
    explanation={
        "top_features": [
            "pps",
            "syn_ack_ratio",
            "source_ip_entropy",
        ]
    },
    source_ip="192.168.1.100",
    destination_ip="10.0.0.10",
)


print("Generated Alert:")
print(result)