from ai_engine.features.ddos_features import extract_ddos_features


source_ips = [
    "192.168.1.10",
    "192.168.1.10",
    "192.168.1.11",
    "192.168.1.12",
    "192.168.1.13",
]

features = extract_ddos_features(
    source_ips=source_ips,
    packet_count=1000,
    duration_seconds=10,
    syn_count=900,
    ack_count=100,
)

print("DDoS Features:")
print(features)