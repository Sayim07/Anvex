from ai_engine.explainability.shap_explainer import explain_prediction


features = {
    "source_ip_entropy": 3.5,
    "pps": 5000,
    "syn_ack_ratio": 10,
    "port_fanout": 5,
    "connection_failure_rate": 0.2,
    "subdomain_entropy": 2,
    "ngram_probability": 0.2,
    "packet_size_variance": 3000,
    "mean_packet_size": 700,
    "iat_variance": 5,
    "fft_periodicity": 0.1,
    "outbound_inbound_ratio": 1,
    "volume_baseline_ratio": 1,
}


result = explain_prediction(features)

print("SHAP Explanation:")
print("Prediction:", result["prediction"])

print("\nFeature Contributions:")

for feature, value in result["shap_values"].items():
    print(f"{feature}: {value:.6f}")