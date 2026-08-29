from ai_engine.adapters.zeek_adapter import ZeekAdapter


adapter = ZeekAdapter.from_json(
    "pipeline/standardized_events.json"
)

features = {
    "ddos": adapter.extract_ddos_features(),
    "port_scan": adapter.extract_scan_features(),
    "c2_beacon": adapter.extract_c2_features(),
    "exfiltration": adapter.extract_exfil_features(),
}

print("Zeek Adapter Result:")

for detector, detector_features in features.items():
    print(f"{detector}:")
    print(detector_features)