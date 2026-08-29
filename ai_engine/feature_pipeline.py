import json
from pathlib import Path
from statistics import mean, variance

from ai_engine.features.ddos_features import extract_ddos_features
from ai_engine.features.scan_features import extract_scan_features
from ai_engine.features.dga_features import extract_dga_features
from ai_engine.features.c2_features import extract_c2_features
from ai_engine.features.exfil_features import extract_exfil_features
from ai_engine.features.ja4_features import extract_ja4_features


FEATURE_NAMES = [
    "source_ip_entropy",
    "pps",
    "syn_ack_ratio",
    "port_fanout",
    "connection_failure_rate",
    "subdomain_entropy",
    "ngram_probability",
    "packet_size_variance",
    "mean_packet_size",
    "iat_variance",
    "fft_periodicity",
    "outbound_inbound_ratio",
    "volume_baseline_ratio",
]


def safe_float(value, default=0.0):
    try:
        if value in ("", "-", None):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value, default=0):
    try:
        if value in ("", "-", None):
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def load_events(path):
    path = Path(path)

    with open(path, "r") as f:
        return json.load(f)


def build_features(events):
    """
    Build the exact 13-feature vector expected by XGBoost.
    """

    if not events:
        return {
            name: 0.0
            for name in FEATURE_NAMES
        }

    # =========================================================
    # Basic packet / connection information
    # =========================================================

    timestamps = sorted(
        safe_float(event.get("timestamp"))
        for event in events
        if event.get("timestamp") is not None
    )

    source_ips = [
        event.get("src_ip", "")
        for event in events
        if event.get("src_ip")
    ]

    destination_ports = [
        safe_int(event.get("dst_port"))
        for event in events
        if event.get("dst_port") is not None
    ]

    # =========================================================
    # Packet counts
    # =========================================================

    packet_counts = []

    for event in events:
        orig_pkts = safe_int(event.get("orig_pkts"))
        resp_pkts = safe_int(event.get("resp_pkts"))

        total_pkts = orig_pkts + resp_pkts

        if total_pkts > 0:
            packet_counts.append(total_pkts)

    if packet_counts:
        total_packets = sum(packet_counts)
    else:
        total_packets = len(events)

    # =========================================================
    # Duration
    # =========================================================

    durations = [
        safe_float(event.get("duration"))
        for event in events
        if safe_float(event.get("duration")) > 0
    ]

    if durations:
        total_duration = sum(durations)
    elif len(timestamps) >= 2:
        total_duration = timestamps[-1] - timestamps[0]
    else:
        total_duration = 1.0

    if total_duration <= 0:
        total_duration = 1.0

    # =========================================================
    # SYN / ACK
    # =========================================================

    syn_count = 0
    ack_count = 0

    for event in events:

        history = str(
            event.get("history", "")
        )

        # Zeek history:
        # S = SYN
        # A = ACK

        syn_count += history.count("S")
        ack_count += history.count("A")

    # =========================================================
    # Failed connections
    # =========================================================

    failed_connections = 0
    total_connections = 0

    for event in events:

        if event.get("event_type") != "connection":
            continue

        total_connections += 1

        state = str(
            event.get("conn_state", "")
        )

        if state not in ("SF", "S1"):
            failed_connections += 1

    # =========================================================
    # DDoS features
    # =========================================================

    ddos_features = extract_ddos_features(
        source_ips=source_ips,
        packet_count=total_packets,
        duration_seconds=total_duration,
        syn_count=syn_count,
        ack_count=ack_count,
    )

    # =========================================================
    # Port scan features
    # =========================================================

    scan_features = extract_scan_features(
        destination_ports=destination_ports,
        failed_connections=failed_connections,
        total_connections=total_connections,
    )

    # =========================================================
    # DGA features
    # =========================================================

    dns_queries = [
        str(event.get("dns_query", ""))
        for event in events
        if event.get("event_type") == "dns"
        and event.get("dns_query")
    ]

    if dns_queries:

        # Use the longest DNS query as representative input.
        representative_domain = max(
            dns_queries,
            key=len
        )

        dga_features = extract_dga_features(
            representative_domain
        )

    else:

        dga_features = {
            "subdomain_entropy": 0.0,
            "ngram_probability": 0.0,
        }

    # =========================================================
    # Packet size features / JA4 related features
    # =========================================================

    packet_sizes = []

    for event in events:

        orig_bytes = safe_int(
            event.get("orig_bytes")
        )

        resp_bytes = safe_int(
            event.get("resp_bytes")
        )

        if orig_bytes > 0:
            packet_sizes.append(orig_bytes)

        if resp_bytes > 0:
            packet_sizes.append(resp_bytes)

    if not packet_sizes:
        packet_sizes = [0.0]

    packet_times = timestamps

    ja4_values = [
        event.get("ja4")
        for event in events
        if event.get("ja4")
    ]

    ja3_values = [
        event.get("ja3")
        for event in events
        if event.get("ja3")
    ]

    ja4_value = ja4_values[0] if ja4_values else ""
    ja3_value = ja3_values[0] if ja3_values else ""

    ja4_features = extract_ja4_features(
        ja4=ja4_value,
        ja3=ja3_value,
        packet_sizes=packet_sizes,
        packet_times=packet_times,
    )

    # =========================================================
    # C2 Beacon features
    # =========================================================

    inter_arrival_times = []

    if len(timestamps) >= 2:

        for i in range(1, len(timestamps)):

            difference = (
                timestamps[i]
                - timestamps[i - 1]
            )

            if difference >= 0:
                inter_arrival_times.append(
                    difference
                )

    c2_features = extract_c2_features(
        inter_arrival_times
    )

    # =========================================================
    # Exfiltration features
    # =========================================================

    outbound_bytes = 0
    inbound_bytes = 0

    for event in events:

        outbound_bytes += safe_int(
            event.get("orig_bytes")
        )

        inbound_bytes += safe_int(
            event.get("resp_bytes")
        )

    current_volume = (
        outbound_bytes
        + inbound_bytes
    )

    # Estimate baseline as average event volume.
    event_volumes = []

    for event in events:

        orig = safe_int(
            event.get("orig_bytes")
        )

        resp = safe_int(
            event.get("resp_bytes")
        )

        volume = orig + resp

        if volume > 0:
            event_volumes.append(volume)

    if event_volumes:

        baseline_volume = mean(
            event_volumes
        )

    else:

        baseline_volume = 1.0

    exfil_features = extract_exfil_features(
        outbound_bytes=outbound_bytes,
        inbound_bytes=inbound_bytes,
        current_volume=current_volume,
        baseline_volume=baseline_volume,
    )

    # =========================================================
    # Build final 13-feature vector
    # =========================================================

    features = {

        "source_ip_entropy":
            safe_float(
                ddos_features["source_ip_entropy"]
            ),

        "pps":
            safe_float(
                ddos_features["pps"]
            ),

        "syn_ack_ratio":
            safe_float(
                ddos_features["syn_ack_ratio"]
            ),

        "port_fanout":
            safe_float(
                scan_features["port_fanout"]
            ),

        "connection_failure_rate":
            safe_float(
                scan_features[
                    "connection_failure_rate"
                ]
            ),

        "subdomain_entropy":
            safe_float(
                dga_features[
                    "subdomain_entropy"
                ]
            ),

        "ngram_probability":
            safe_float(
                dga_features[
                    "ngram_probability"
                ]
            ),

        "packet_size_variance":
            safe_float(
                ja4_features[
                    "packet_size_variance"
                ]
            ),

        "mean_packet_size":
            safe_float(
                ja4_features[
                    "mean_packet_size"
                ]
            ),

        "iat_variance":
            safe_float(
                c2_features[
                    "iat_variance"
                ]
            ),

        "fft_periodicity":
            safe_float(
                c2_features[
                    "fft_periodicity"
                ]
            ),

        "outbound_inbound_ratio":
            safe_float(
                exfil_features[
                    "outbound_inbound_ratio"
                ]
            ),

        "volume_baseline_ratio":
            safe_float(
                exfil_features[
                    "volume_baseline_ratio"
                ]
            ),
    }

    # =========================================================
    # Guarantee exact feature order
    # =========================================================

    return {
        name: safe_float(
            features.get(name, 0.0)
        )
        for name in FEATURE_NAMES
    }


# =============================================================
# TEST
# =============================================================

if __name__ == "__main__":

    path = "pipeline/scenario_output/dga.json"

    events = load_events(path)

    features = build_features(events)

    print("===== ANVEX FEATURE PIPELINE TEST =====")
    print("Events:", len(events))
    print("Features:", len(features))

    for name, value in features.items():
        print(f"{name}: {value}")
