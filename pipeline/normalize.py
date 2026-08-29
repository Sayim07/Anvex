import json
import sys

INPUT_FILE = "zeek_events.json"
OUTPUT_FILE = "standardized_events.json"

DEFAULT_LABEL = sys.argv[1] if len(sys.argv) > 1 else "normal"


def is_missing(value):
    return value in ("-", "", None)


def to_int(value, default=0):
    try:
        if is_missing(value):
            return default
        return int(value)
    except (ValueError, TypeError):
        return default


def to_float(value, default=0.0):
    try:
        if is_missing(value):
            return default
        return float(value)
    except (ValueError, TypeError):
        return default


with open(INPUT_FILE, "r") as file:
    events = json.load(file)

standardized = []

for event in events:

    event_type = event.get("event_type", "connection")

    # ========================================================
    # CONNECTION EVENT
    # ========================================================

    if event_type == "connection":

        orig_bytes_missing = is_missing(event.get("orig_bytes"))
        resp_bytes_missing = is_missing(event.get("resp_bytes"))
        duration_missing = is_missing(event.get("duration"))
        orig_pkts_missing = is_missing(event.get("orig_pkts"))
        resp_pkts_missing = is_missing(event.get("resp_pkts"))

        orig_bytes = to_int(event.get("orig_bytes"))
        resp_bytes = to_int(event.get("resp_bytes"))
        orig_pkts = to_int(event.get("orig_pkts"))
        resp_pkts = to_int(event.get("resp_pkts"))
        duration = to_float(event.get("duration"))

        normalized_event = {
            "source": "zeek",
            "event_type": "connection",
            "label": event.get("label", DEFAULT_LABEL),

            "timestamp": to_float(event.get("timestamp")),
            "uid": event.get("uid", ""),

            "src_ip": event.get("src_ip", ""),
            "src_port": to_int(event.get("src_port")),

            "dst_ip": event.get("dst_ip", ""),
            "dst_port": to_int(event.get("dst_port")),

            "protocol": event.get("protocol", ""),
            "service": event.get("service", ""),

            "duration": duration,

            "orig_bytes": orig_bytes,
            "resp_bytes": resp_bytes,

            "orig_pkts": orig_pkts,
            "resp_pkts": resp_pkts,

            "conn_state": event.get("conn_state", ""),

            "local_orig": event.get("local_orig", ""),
            "local_resp": event.get("local_resp", ""),

            "missed_bytes": to_int(event.get("missed_bytes")),
            "history": event.get("history", ""),

            # ------------------------------------------------
            # Missing-value indicators
            # ------------------------------------------------

            "orig_bytes_missing": int(orig_bytes_missing),
            "resp_bytes_missing": int(resp_bytes_missing),
            "duration_missing": int(duration_missing),
            "orig_pkts_missing": int(orig_pkts_missing),
            "resp_pkts_missing": int(resp_pkts_missing),

            # ------------------------------------------------
            # Derived network features
            # ------------------------------------------------

            "total_bytes": orig_bytes + resp_bytes,
            "total_pkts": orig_pkts + resp_pkts,

            "byte_ratio": (
                orig_bytes / resp_bytes
                if resp_bytes > 0
                else float(orig_bytes)
            ),

            "packet_ratio": (
                orig_pkts / resp_pkts
                if resp_pkts > 0
                else float(orig_pkts)
            ),

            "bytes_per_packet": (
                (orig_bytes + resp_bytes) /
                (orig_pkts + resp_pkts)
                if (orig_pkts + resp_pkts) > 0
                else 0.0
            ),

            "bytes_per_second": (
                (orig_bytes + resp_bytes) / duration
                if duration > 0
                else 0.0
            ),
        }

        # ----------------------------------------------------
        # JA3 / JA4 / TLS metadata
        # ----------------------------------------------------

        if event.get("ja3"):
            normalized_event["ja3"] = event["ja3"]

        if event.get("ja4"):
            normalized_event["ja4"] = event["ja4"]

        if event.get("tls_version"):
            normalized_event["tls_version"] = event["tls_version"]

        if event.get("server_name"):
            normalized_event["server_name"] = event["server_name"]

        standardized.append(normalized_event)

    # ========================================================
    # DNS EVENT
    # ========================================================

    elif event_type == "dns":

        dns_query = event.get("dns_query", "")

        normalized_event = {
            "source": "zeek",
            "event_type": "dns",
            "label": event.get("label", DEFAULT_LABEL),

            "timestamp": to_float(event.get("timestamp")),
            "uid": event.get("uid", ""),

            "src_ip": event.get("src_ip", ""),
            "src_port": to_int(event.get("src_port")),

            "dst_ip": event.get("dst_ip", ""),
            "dst_port": to_int(event.get("dst_port")),

            "protocol": event.get("protocol", ""),
            "service": event.get("service", "dns"),

            "dns_query": dns_query,
            "dns_qtype": event.get("dns_qtype", ""),
            "dns_rcode": event.get("dns_rcode", ""),
            "dns_rejected": event.get("dns_rejected", ""),

            "dns_trans_id": to_int(event.get("dns_trans_id")),

            "dns_query_length": to_int(
                event.get("dns_query_length")
            ),

            # Useful DNS feature
            "dns_label_count": (
                len(dns_query.rstrip(".").split("."))
                if dns_query
                else 0
            ),

            "dns_digit_count": sum(
                c.isdigit() for c in dns_query
            ),

            "dns_hyphen_count": dns_query.count("-"),
        }

        standardized.append(normalized_event)


# ============================================================
# SORT BY TIMESTAMP
# ============================================================

standardized.sort(
    key=lambda x: to_float(x.get("timestamp"))
)


# ============================================================
# WRITE OUTPUT
# ============================================================

with open(OUTPUT_FILE, "w") as file:
    json.dump(standardized, file, indent=2)


print(
    f"Created {OUTPUT_FILE} with "
    f"{len(standardized)} event(s), "
    f"label={DEFAULT_LABEL}"
)

print(
    "Connection events:",
    sum(
        1 for x in standardized
        if x["event_type"] == "connection"
    )
)

print(
    "DNS events:",
    sum(
        1 for x in standardized
        if x["event_type"] == "dns"
    )
)

print(
    "JA4 events:",
    sum(
        1 for x in standardized
        if x.get("ja4")
    )
)
