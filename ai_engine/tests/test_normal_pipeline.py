from ai_engine.pipeline import run_ai_pipeline


detector_result = {
    "detector": "normal",
    "detected": False,
    "score": 0.0,
    "features": {},
}


features = {
    "source_ip_entropy": 1.5,
    "pps": 100,
    "syn_ack_ratio": 1.0,
    "port_fanout": 3,
    "connection_failure_rate": 0.1,
    "subdomain_entropy": 2.0,
    "ngram_probability": 0.2,
    "packet_size_variance": 1000,
    "mean_packet_size": 600,
    "iat_variance": 10,
    "fft_periodicity": 0.1,
    "outbound_inbound_ratio": 1.0,
    "volume_baseline_ratio": 1.0,
}


alert = run_ai_pipeline(
    detector_result=detector_result,
    features=features,
    source_ip="192.168.1.50",
    destination_ip="10.0.0.10",
)


print("Normal Traffic Pipeline Result:")
print(alert)
