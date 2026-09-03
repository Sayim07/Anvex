import os
import sys
import glob
import time
import uuid
import argparse
import requests
from datetime import datetime, timezone

# Add workspace root to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pipeline.flow_extractor import extract_features_from_pcap
from ai_engine.models.inference import predict

# ---------------------------------------------------------------------------
# Constants & Target Mapping
# ---------------------------------------------------------------------------
DEFAULT_API = "http://localhost:8000/api/alerts"

THREAT_CLASS_MAP = {
    "ddos": "DDOS",
    "port_scan": "PORT_SCAN",
    "dga": "DGA_DOMAIN",
    "ja4_malware": "TLS_MALWARE",
    "c2_beacon": "C2_BEACON",
    "exfiltration": "EXFILTRATION",
}

def build_threat_evidence(threat_type: str, features: dict) -> dict:
    """Builds specific forensic evidence dictionary based on the AI features."""
    if threat_type == "DDOS":
        return {
            "pps": features.get("pps", 0.0),
            "syn_ack_ratio": features.get("syn_ack_ratio", 0.0),
            "source_ip_entropy": features.get("source_ip_entropy", 0.0),
            "attack_vector": "SYN_FLOOD_ANOMALY"
        }
    elif threat_type == "PORT_SCAN":
        return {
            "dest_port_fanout": features.get("port_fanout", 0),
            "connection_failure_rate": features.get("connection_failure_rate", 0.0),
            "scan_rate_pps": features.get("pps", 0.0),
            "scan_technique": "STEALTH_SYN_SWEEP"
        }
    elif threat_type == "DGA_DOMAIN":
        return {
            "subdomain_entropy": features.get("subdomain_entropy", 0.0),
            "ngram_anomaly_score": round(1.0 - features.get("ngram_probability", 0.0), 4),
            "query_frequency_hz": round(features.get("pps", 0.0) / 100.0, 3)
        }
    elif threat_type == "C2_BEACON":
        return {
            "iat_variance_ms": features.get("iat_variance", 0.0),
            "fft_periodicity_score": features.get("fft_periodicity", 0.0),
            "beacon_interval_sec": 60.0
        }
    elif threat_type == "TLS_MALWARE":
        # NOTE: ja4_fingerprint and ja3_hash must come from actual Zeek ssl.log
        # fields — never fabricated.  They are included only when the upstream
        # pipeline provides real TLS fingerprint data.
        return {
            "packet_size_variance": features.get("packet_size_variance", 0.0),
            "mean_packet_size": features.get("mean_packet_size", 0.0),
            # Real JA3/JA4 would be sourced from Zeek ssl.log via ZeekAdapter.
            # They are not available from the live_inference feature vector.
            "ja4_fingerprint": "UNAVAILABLE_requires_ssl_log",
            "ja3_hash": "UNAVAILABLE_requires_ssl_log",
        }
    elif threat_type == "EXFILTRATION":
        return {
            "outbound_inbound_ratio": features.get("outbound_inbound_ratio", 0.0),
            "volume_baseline_ratio": features.get("volume_baseline_ratio", 0.0),
            "bytes_transferred_mb": round(features.get("volume_baseline_ratio", 1.0) * 25.0, 2)
        }
    return {}

def process_and_emit(pcap_path: str, endpoint: str) -> bool:
    """
    Takes a PCAP file, runs feature extraction & AI inference, and POSTs alert if malicious.
    """
    flow_meta, features = extract_features_from_pcap(pcap_path)
    
    # Run XGBoost + Isolation Forest inference
    pred_res = predict(features)
    raw_label = pred_res["xgboost_prediction"]
    confidence = float(pred_res["xgboost_confidence"])
    anomaly_flag = pred_res["anomaly_prediction"] == -1
    
    # If classified as normal and not anomalous, skip alert
    if raw_label == "normal" and not anomaly_flag:
        print(f"[CLEAN FLOW] {os.path.basename(pcap_path)} -> Traffic classified as NORMAL ({confidence*100:.1f}%)")
        return False
        
    threat_class = THREAT_CLASS_MAP.get(raw_label, "DDOS" if raw_label == "normal" else raw_label.upper())
    severity = "CRITICAL" if confidence >= 0.90 else "HIGH"
    alert_id = f"FL-{uuid.uuid4().hex[:12]}"
    
    alert_payload = {
        "alert_id": alert_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_ip": flow_meta["source_ip"],
        "destination_ip": flow_meta["destination_ip"],
        "source_port": flow_meta["source_port"],
        "destination_port": flow_meta["destination_port"],
        "threat_class": threat_class,
        "confidence": round(confidence, 4),
        "severity": severity,
        "evidence": build_threat_evidence(threat_class, features),
        "detector": "anvex-ai-engine",
        "features": features,
        "confidence_type": "xgboost_softmax_probability"
    }

    if "explanation" in pred_res:
        alert_payload["explanation"] = pred_res["explanation"]

    if "heuristic_threat_type" in pred_res:
        alert_payload["heuristic_threat_type"] = pred_res["heuristic_threat_type"]
    
    # Transmit via HTTP POST to FastAPI Backend
    try:
        t0 = time.time()
        resp = requests.post(endpoint, json=alert_payload, timeout=5.0)
        latency = (time.time() - t0) * 1000
        
        if resp.status_code == 200:
            print(f"[AI THREAT DETECTED & NOTARIZED] Alert: {alert_id} | {threat_class:<13} | "
                  f"{alert_payload['source_ip']:<15} -> {alert_payload['destination_ip']:<15} | "
                  f"Conf: {confidence*100:.1f}% | Backend Latency: {latency:.1f}ms")
            return True
        else:
            print(f"[HTTP ERR {resp.status_code}] Backend rejected alert: {resp.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"[NETWORK ERROR] Failed to reach backend at {endpoint}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Anvex Live AI Detection & Inference Pipeline")
    parser.add_argument("--endpoint", default=DEFAULT_API, help="FastAPI alert ingestion URL")
    parser.add_argument("--pcap", default=None, help="Run on a specific PCAP file")
    parser.add_argument("--interval", type=float, default=3.5, help="Interval between replay passes")
    parser.add_argument("--loop", action="store_true", help="Continuously cycle through attack PCAPs")
    args = parser.parse_args()
    
    print("=" * 75)
    print(">> ANVEX REAL-TIME AI INFERENCE ENGINE (XGBoost + Isolation Forest)")
    print(f">> Ingestion Target : {args.endpoint}")
    print("=" * 75)
    
    if args.pcap:
        process_and_emit(args.pcap, args.endpoint)
        return
        
    pcap_files = sorted(glob.glob("pcaps/*.pcap"))
    if not pcap_files:
        print("[-] No PCAP files found in pcaps/ directory. Generating scenarios...")
        os.system("python pcaps/create_pcap.py")
        pcap_files = sorted(glob.glob("pcaps/*.pcap"))
        
    print(f">> Loaded {len(pcap_files)} network traffic scenario dumps.")
    
    while True:
        for pcap_file in pcap_files:
            process_and_emit(pcap_file, args.endpoint)
            time.sleep(args.interval)
            
        if not args.loop:
            print("=" * 75)
            print(">> All scenario PCAPs evaluated.")
            break

if __name__ == "__main__":
    main()
