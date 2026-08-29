from ai_engine.detectors.port_scan_detector import detect_port_scan


result = detect_port_scan(
    destination_ports=[
        21, 22, 23, 25, 53,
        80, 110, 135, 139, 443,
        445, 8080
    ],
    failed_connections=8,
    total_connections=10,
)

print("Port Scan Detection Result:")
print(result)