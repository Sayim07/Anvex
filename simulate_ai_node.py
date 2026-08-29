import time
import uuid
import random
import argparse
import requests
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Configuration & Threat Data Models
# ---------------------------------------------------------------------------
API_ENDPOINT = "http://localhost:8000/api/alerts"

THREAT_PROFILES = [
    {
        "threat_class": "DDOS",
        "severity": "CRITICAL",
        "conf_range": (0.92, 0.99),
        "dest_ports": [80, 443, 53],
        "evidence_gen": lambda: {
            "pps": round(random.uniform(2500, 15000), 2),
            "syn_ack_ratio": round(random.uniform(8.5, 32.0), 3),
            "source_ip_entropy": round(random.uniform(3.2, 4.8), 4),
            "attack_vector": "SYN_FLOOD_ANOMALY"
        }
    },
    {
        "threat_class": "C2_BEACON",
        "severity": "CRITICAL",
        "conf_range": (0.88, 0.97),
        "dest_ports": [443, 8443, 9001],
        "evidence_gen": lambda: {
            "iat_variance_ms": round(random.uniform(0.05, 1.2), 4),
            "fft_periodicity_score": round(random.uniform(0.88, 0.99), 4),
            "beacon_interval_sec": round(random.choice([30.0, 60.0, 120.0, 300.0]), 1),
            "ja3_fingerprint": uuid.uuid4().hex[:32]
        }
    },
    {
        "threat_class": "PORT_SCAN",
        "severity": "HIGH",
        "conf_range": (0.85, 0.94),
        "dest_ports": [22, 80, 443, 3389, 8080],
        "evidence_gen": lambda: {
            "dest_port_fanout": random.randint(1200, 65000),
            "connection_failure_rate": round(random.uniform(0.85, 0.99), 4),
            "scan_rate_pps": round(random.uniform(300, 1800), 2),
            "scan_technique": "STEALTH_SYN_SWEEP"
        }
    },
    {
        "threat_class": "TLS_MALWARE",
        "severity": "HIGH",
        "conf_range": (0.87, 0.96),
        "dest_ports": [443, 8443],
        "evidence_gen": lambda: {
            "ja4_fingerprint": f"t13d1516h2_{uuid.uuid4().hex[:10]}",
            "ja3_hash": uuid.uuid4().hex[:32],
            "splt_anomaly_score": round(random.uniform(0.78, 0.98), 4),
            "cipher_suite_anomaly": True
        }
    },
    {
        "threat_class": "EXFILTRATION",
        "severity": "CRITICAL",
        "conf_range": (0.90, 0.98),
        "dest_ports": [443, 53, 9999],
        "evidence_gen": lambda: {
            "outbound_inbound_ratio": round(random.uniform(15.0, 80.0), 2),
            "bytes_transferred_mb": round(random.uniform(120.0, 4500.0), 2),
            "baseline_deviation_sigma": round(random.uniform(4.5, 14.0), 3)
        }
    }
]

INTERNAL_IPS = [
    "10.0.0.12", "10.0.0.45", "10.0.0.88", "10.0.0.104",
    "192.168.1.15", "192.168.1.50", "192.168.1.110", "192.168.1.205"
]

EXTERNAL_IPS = [
    "185.220.101.5", "194.26.29.112", "45.154.255.89", "91.240.118.234",
    "198.51.100.44", "203.0.113.195", "103.145.13.72", "185.196.8.14"
]

# ---------------------------------------------------------------------------
# Generator & Dispatch Function
# ---------------------------------------------------------------------------
def generate_threat_payload() -> dict:
    profile = random.choice(THREAT_PROFILES)
    is_inbound = random.choice([True, True, False])
    
    src_ip = random.choice(EXTERNAL_IPS) if is_inbound else random.choice(INTERNAL_IPS)
    dst_ip = random.choice(INTERNAL_IPS) if is_inbound else random.choice(EXTERNAL_IPS)
    
    conf = round(random.uniform(*profile["conf_range"]), 4)
    alert_id = f"FL-{uuid.uuid4().hex[:12]}"
    
    payload = {
        "alert_id": alert_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_ip": src_ip,
        "destination_ip": dst_ip,
        "source_port": random.randint(10240, 65530),
        "destination_port": random.choice(profile["dest_ports"]),
        "threat_class": profile["threat_class"],
        "confidence": conf,
        "severity": profile["severity"],
        "evidence": profile["evidence_gen"](),
        "detector": "anvex-ai-engine"
    }
    return payload

def run_simulation(endpoint: str, interval: float, count: int = None):
    print("=" * 70)
    print(">> Anvex External AI Node Simulator (M2M Ingestion Pipeline)")
    print(f">> Target Backend Endpoint : {endpoint}")
    print(f">> Emission Interval       : {interval}s")
    print(f">> Total Alerts to Emit   : {'Infinite (Ctrl+C to stop)' if count is None else count}")
    print("=" * 70)
    
    sent = 0
    while True:
        payload = generate_threat_payload()
        try:
            t0 = time.time()
            resp = requests.post(endpoint, json=payload, timeout=5.0)
            latency = (time.time() - t0) * 1000
            
            if resp.status_code == 200:
                print(f"[OK - NOTARIZED] Alert: {payload['alert_id']} | Threat: {payload['threat_class']:<13} | "
                      f"{payload['source_ip']:<15} -> {payload['destination_ip']:<15} | "
                      f"Conf: {payload['confidence']*100:.1f}% | Latency: {latency:.1f}ms")
            else:
                print(f"[ERR HTTP {resp.status_code}] Failed: {resp.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"[WARN NETWORK ERROR] Unable to reach backend at {endpoint}: {e}")
            
        sent += 1
        if count and sent >= count:
            print("=" * 70)
            print(f">> Simulation Complete: {sent} alerts transmitted.")
            break
            
        time.sleep(interval)

# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Anvex External AI Sensor Simulator")
    parser.add_argument("--endpoint", default=API_ENDPOINT, help="FastAPI alert ingestion URL")
    parser.add_argument("--interval", type=float, default=4.0, help="Seconds between alerts (default: 4.0)")
    parser.add_argument("--count", type=int, default=None, help="Number of alerts to emit (default: continuous)")
    args = parser.parse_args()
    
    run_simulation(args.endpoint, args.interval, args.count)
