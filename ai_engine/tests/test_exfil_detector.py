from ai_engine.detectors.exfil_detector import detect_exfil


result = detect_exfil(
    outbound_bytes=500000,
    inbound_bytes=50000,
    current_volume=900000,
    baseline_volume=200000,
)

print("Exfiltration Detection Result:")
print(result)