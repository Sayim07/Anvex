from ai_engine.adapters.zeek_adapter import ZeekAdapter
from ai_engine.detectors.ddos_detector import detect_ddos
from ai_engine.detectors.port_scan_detector import detect_port_scan
from ai_engine.detectors.c2_detector import detect_c2
from ai_engine.detectors.exfil_detector import detect_exfil


adapter = ZeekAdapter.from_json(
    "pipeline/standardized_events.json"
)


# ---------------------------------
# DDoS
# ---------------------------------

ddos_inputs = adapter.prepare_ddos_inputs()

ddos_result = detect_ddos(
    **ddos_inputs
)

print("=== DDoS ===")
print(ddos_result)


# ---------------------------------
# Port Scan
# ---------------------------------

scan_inputs = adapter.prepare_scan_inputs()

scan_result = detect_port_scan(
    **scan_inputs
)

print("\n=== Port Scan ===")
print(scan_result)


# ---------------------------------
# C2 Beacon
# ---------------------------------

c2_inputs = adapter.prepare_c2_inputs()

c2_result = detect_c2(
    **c2_inputs
)

print("\n=== C2 Beacon ===")
print(c2_result)


# ---------------------------------
# Exfiltration
# ---------------------------------

exfil_inputs = adapter.prepare_exfil_inputs()

exfil_result = detect_exfil(
    **exfil_inputs
)

print("\n=== Exfiltration ===")
print(exfil_result)