from ai_engine.detectors.ddos_detector import detect_ddos


result = detect_ddos(
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

print("DDoS Detection Result:")
print(result)