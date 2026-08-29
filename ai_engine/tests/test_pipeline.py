from ai_engine.detectors.ddos_detector import detect_ddos
from ai_engine.pipeline import run_ai_pipeline


# -------------------------
# Step 1: Detector
# -------------------------

detector_result = detect_ddos(
    source_ips=[
        "192.168.1.10",
        "192.168.1.11",
        "192.168.1.12",
        "192.168.1.13",
        "192.168.1.14",
    ],
    packet_count=20000,
    duration_seconds=10,
    syn_count=900,
    ack_count=100,
)


# -------------------------
# Step 2: Features
# -------------------------

features = detector_result["features"]


# -------------------------
# Step 3: Complete AI pipeline
# -------------------------

alert = run_ai_pipeline(
    detector_result=detector_result,
    features={
        "source_ip_entropy": features["source_ip_entropy"],
        "pps": features["pps"],
        "syn_ack_ratio": features["syn_ack_ratio"],
        "port_fanout": 5,
        "connection_failure_rate": 0.2,
        "subdomain_entropy": 2.0,
        "ngram_probability": 0.2,
        "packet_size_variance": 3000,
        "mean_packet_size": 700,
        "iat_variance": 5,
        "fft_periodicity": 0.1,
        "outbound_inbound_ratio": 1,
        "volume_baseline_ratio": 1,
    },
    source_ip="192.168.1.100",
    destination_ip="10.0.0.10",
)


print("Complete AI Pipeline Result:")
print(alert)