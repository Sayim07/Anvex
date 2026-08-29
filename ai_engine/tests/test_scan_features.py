from ai_engine.features.scan_features import extract_scan_features


result = extract_scan_features(
    destination_ports=[22, 23, 80, 443, 8080, 3389],
    failed_connections=8,
    total_connections=10,
)

print("Port Scan Features:")
print(result)