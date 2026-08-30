"""
test_scenario_pipeline.py
=========================
Comprehensive seven-scenario AI pipeline test.

For each of Ruparna's labelled scenario files, this test:
  1. Loads the scenario via ZeekAdapter.from_scenario_json()
  2. Assembles the full 13-feature vector via assemble_feature_vector()
  3. Runs all six heuristic detectors
  4. Runs XGBoost + Isolation Forest inference
  5. Runs SHAP explainability
  6. Runs threat scoring + severity
  7. Produces a final alert
  8. Reports feature availability per scenario

Run with:
    python -m ai_engine.tests.test_scenario_pipeline

No assertions are hard-coded against expected labels.
Results are reported honestly, including known data limitations.
"""

import json
import sys
from pathlib import Path

from ai_engine.adapters.zeek_adapter import ZeekAdapter
from ai_engine.detectors.ddos_detector import detect_ddos
from ai_engine.detectors.port_scan_detector import detect_port_scan
from ai_engine.detectors.dga_detector import detect_dga
from ai_engine.detectors.ja4_detector import detect_ja4
from ai_engine.detectors.c2_detector import detect_c2
from ai_engine.detectors.exfil_detector import detect_exfil
from ai_engine.models.inference import predict
from ai_engine.explainability.shap_explainer import explain_prediction
from ai_engine.scoring.threat_scorer import assess_threat
from ai_engine.alerts.alert_schema import create_alert


# ---------------------------------------------------------------------------
# Scenario files
# ---------------------------------------------------------------------------

SCENARIO_DIR = Path("pipeline/scenario_output")

SCENARIOS = [
    "normal",
    "ddos",
    "port_scan",
    "dga",
    "ja4_malware",
    "c2_beacon",
    "exfiltration",
]

# ---------------------------------------------------------------------------
# Feature availability flags (determined from inspection report)
# ---------------------------------------------------------------------------

# Features that are always 0.0 / degraded for specific scenarios due to
# missing upstream data.  These are documented, not hidden.

KNOWN_LIMITATIONS = {
    # Unavailable for ALL scenarios (DNS/TLS fields absent from pipeline)
    "subdomain_entropy": "UNAVAILABLE — requires dns.log query field",
    "ngram_probability": "UNAVAILABLE — requires dns.log query field",
    # Proxy-based for all scenarios
    "syn_ack_ratio": "PARTIAL — derived from Zeek history field proxy, not exact TCP flags",
    # Degenerate for zero-byte scenarios
    "mean_packet_size": "PARTIAL — approximated from byte totals; 0 if all bytes=0",
    "packet_size_variance": "PARTIAL — approximated; 0 if all bytes=0",
    "outbound_inbound_ratio": "PARTIAL — 0.0 when orig_bytes=resp_bytes=0 (most attack scenarios)",
    "volume_baseline_ratio": "PARTIAL — always 1.0 (no historical baseline available)",
}


# ---------------------------------------------------------------------------
# Helper: select the most relevant heuristic detector result
# ---------------------------------------------------------------------------

def _pick_primary_detector(label, all_results):
    """
    For scenarios with a clear primary detector, return that result.
    For others, return the highest-scoring result.
    """
    label_to_detector = {
        "ddos": "ddos",
        "port_scan": "port_scan",
        "dga": "dga",
        "ja4_malware": "ja4",
        "c2_beacon": "c2_beacon",
        "exfiltration": "exfiltration",
        "normal": None,  # no primary attack detector
    }
    primary_name = label_to_detector.get(label)

    if primary_name:
        for r in all_results:
            if r["detector"] == primary_name:
                return r

    # Fallback: return highest-scoring detector
    return max(all_results, key=lambda r: r["score"])


# ---------------------------------------------------------------------------
# Main scenario loop
# ---------------------------------------------------------------------------

def run_scenario(scenario_name):
    """Run the full AI pipeline for one scenario. Returns the alert dict."""

    path = SCENARIO_DIR / f"{scenario_name}.json"
    if not path.exists():
        print(f"  [SKIP] File not found: {path}")
        return None

    adapter = ZeekAdapter.from_scenario_json(str(path))
    ground_truth_label = adapter.primary_label()
    event_count = len(adapter.events)

    print(f"\n{'='*60}")
    print(f"SCENARIO: {scenario_name.upper()}  (ground truth: {ground_truth_label})")
    print(f"Events loaded: {event_count}")
    print(f"{'='*60}")

    # ------------------------------------------------------------------
    # Step 1: Assemble full 13-feature vector
    # ------------------------------------------------------------------
    features = adapter.assemble_feature_vector()

    print("\n[1] Feature Vector (13 features):")
    for name, value in features.items():
        limitation = KNOWN_LIMITATIONS.get(name, "")
        note = f"  <-- {limitation}" if limitation else ""
        print(f"    {name:35s}: {value:.6f}{note}")

    # ------------------------------------------------------------------
    # Step 2: All six heuristic detectors
    # ------------------------------------------------------------------
    print("\n[2] Heuristic Detectors:")

    # DDoS
    ddos_inputs = adapter.prepare_ddos_inputs()
    ddos_result = detect_ddos(**ddos_inputs)
    print(f"    ddos        -> detected={ddos_result['detected']}, score={ddos_result['score']:.3f}")

    # Port Scan
    scan_inputs = adapter.prepare_scan_inputs()
    scan_result = detect_port_scan(**scan_inputs)
    print(f"    port_scan   -> detected={scan_result['detected']}, score={scan_result['score']:.3f}")

    # DGA
    dga_inputs = adapter.prepare_dga_inputs()
    dga_result = detect_dga(**dga_inputs)
    print(f"    dga         -> detected={dga_result['detected']}, score={dga_result['score']:.3f}  [DNS data absent — 0.0 features expected]")

    # JA4
    ja4_inputs = adapter.prepare_ja4_inputs()
    ja4_result = detect_ja4(**ja4_inputs)
    print(f"    ja4         -> detected={ja4_result['detected']}, score={ja4_result['score']:.3f}  [TLS data absent — approx packet sizes]")

    # C2
    c2_inputs = adapter.prepare_c2_inputs()
    c2_result = detect_c2(**c2_inputs)
    iat_n = len(c2_inputs["inter_arrival_times"])
    print(f"    c2_beacon   -> detected={c2_result['detected']}, score={c2_result['score']:.3f}  [{iat_n} IAT intervals]")

    # Exfil
    exfil_inputs = adapter.prepare_exfil_inputs()
    exfil_result = detect_exfil(**exfil_inputs)
    print(f"    exfiltration-> detected={exfil_result['detected']}, score={exfil_result['score']:.3f}  [outbound={exfil_inputs['outbound_bytes']:.0f}B, inbound={exfil_inputs['inbound_bytes']:.0f}B]")

    all_detector_results = [
        ddos_result, scan_result, dga_result,
        ja4_result, c2_result, exfil_result,
    ]

    # Pick the primary detector for the pipeline score
    primary_detector = _pick_primary_detector(ground_truth_label, all_detector_results)
    print(f"\n    Primary detector used: {primary_detector['detector']} (score={primary_detector['score']:.3f})")

    # ------------------------------------------------------------------
    # Step 3: XGBoost + Isolation Forest inference
    # ------------------------------------------------------------------
    print("\n[3] ML Inference:")
    ml_result = predict(features)
    print(f"    XGBoost prediction : {ml_result['xgboost_prediction']}")
    print(f"    XGBoost confidence : {ml_result['xgboost_confidence']:.4f}")
    print(f"    Anomaly prediction : {ml_result['anomaly_prediction']} (1=normal, -1=anomaly)")
    print(f"    Anomaly score      : {ml_result['anomaly_score']:.6f}")

    label_match = ml_result['xgboost_prediction'] == ground_truth_label
    print(f"    Ground truth match : {'YES' if label_match else 'NO'} "
          f"(predicted={ml_result['xgboost_prediction']}, actual={ground_truth_label})")

    # ------------------------------------------------------------------
    # Step 4: SHAP explanation
    # ------------------------------------------------------------------
    print("\n[4] SHAP Explanation (top 5 contributors):")
    explanation = explain_prediction(features)
    shap_values = explanation["shap_values"]
    sorted_shap = sorted(shap_values.items(), key=lambda x: abs(x[1]), reverse=True)
    for feat_name, shap_val in sorted_shap[:5]:
        print(f"    {feat_name:35s}: {shap_val:+.6f}")

    # ------------------------------------------------------------------
    # Step 5: Threat scoring + severity
    # ------------------------------------------------------------------
    print("\n[5] Threat Assessment:")
    threat = assess_threat(
        detector_score=primary_detector["score"],
        xgboost_confidence=ml_result["xgboost_confidence"],
        xgboost_prediction=ml_result["xgboost_prediction"],
        anomaly_prediction=ml_result["anomaly_prediction"],
    )
    print(f"    Threat score : {threat['threat_score']:.4f}")
    print(f"    Severity     : {threat['severity']}")

    # ------------------------------------------------------------------
    # Step 6: Final alert
    # ------------------------------------------------------------------
    src_ip = adapter.source_ips()
    src_ip_str = src_ip[0] if src_ip else None
    dst_ips = [str(e.get("dst_ip", "")) for e in adapter.events if e.get("dst_ip")]
    dst_ip_str = dst_ips[0] if dst_ips else None

    # Check if a specialist heuristic overrides the XGBoost label in terms of evidence
    # (We don't override the actual ml label, just surface the heuristic's finding)
    heuristic_override = None
    if primary_detector["score"] >= 0.5 and primary_detector["detected"]:
        if primary_detector["detector"] != ml_result["xgboost_prediction"]:
            heuristic_override = primary_detector["detector"]

    alert = create_alert(
        threat_type=ml_result["xgboost_prediction"],
        severity=threat["severity"],
        threat_score=threat["threat_score"],
        confidence=ml_result["xgboost_confidence"],
        features=features,
        explanation=shap_values,
        source_ip=src_ip_str,
        destination_ip=dst_ip_str,
        heuristic_threat_type=heuristic_override,
    )

    print("\n[6] Final Alert:")
    for key, value in alert.items():
        if key not in ("features", "explanation"):
            print(f"    {key}: {value}")

    return alert


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    print("ANVEX — Seven-Scenario AI Pipeline Test")
    print("="*60)
    print("NOTE: DGA and JA4 features are 0.0 in all scenarios because")
    print("dns.log and ssl.log fields are not yet in the pipeline output.")
    print("This is a known upstream limitation, not a code bug.")
    print("="*60)

    results = {}
    errors = {}

    for scenario in SCENARIOS:
        try:
            alert = run_scenario(scenario)
            if alert:
                results[scenario] = alert
        except Exception as exc:
            errors[scenario] = str(exc)
            print(f"\n  [ERROR] {scenario}: {exc}")

    # ------------------------------------------------------------------
    # Summary table
    # ------------------------------------------------------------------
    print(f"\n\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"{'Scenario':<16} {'GT Label':<14} {'XGB Pred':<14} {'Match':<6} {'Score':>6} {'Severity':<12}")
    print("-"*70)

    for scenario in SCENARIOS:
        if scenario in errors:
            print(f"{scenario:<16} ERROR: {errors[scenario]}")
            continue
        if scenario not in results:
            continue
        alert = results[scenario]
        gt = scenario  # ground truth IS the scenario name
        pred = alert.get("threat_type", "?")
        match = "YES" if pred == gt else "NO"
        score = alert.get("threat_score", 0)
        sev = alert.get("severity", "?")
        print(f"{scenario:<16} {gt:<14} {pred:<14} {match:<6} {score:>6.4f} {sev:<12}")

    print("-"*70)
    print(f"\nCompleted: {len(results)} scenarios, {len(errors)} errors.")

    # ------------------------------------------------------------------
    # Known limitations reminder
    # ------------------------------------------------------------------
    print("\nKNOWN DATA LIMITATIONS:")
    print("  - subdomain_entropy, ngram_probability: always 0.0 (no dns.log)")
    print("  - syn_ack_ratio: history-proxy only (not exact TCP flags)")
    print("  - mean_packet_size, packet_size_variance: 0.0 for all-zero-byte scenarios")
    print("  - outbound_inbound_ratio: 0.0 for all-zero-byte scenarios")
    print("  - volume_baseline_ratio: 1.0 (no historical baseline)")
    print("  - C2 false positive risk: compressed timestamps -> near-zero IAT variance")

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
