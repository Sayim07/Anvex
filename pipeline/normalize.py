import json
import sys

INPUT_FILE = "zeek_events.json"
OUTPUT_FILE = "standardized_events.json"

DEFAULT_LABEL = sys.argv[1] if len(sys.argv) > 1 else "normal"

with open(INPUT_FILE, "r") as file:
    events = json.load(file)

standardized = []

for event in events:

    def to_int(value, default=0):
        try:
            if value in ("-", "", None):
                return default
            return int(value)
        except (ValueError, TypeError):
            return default

    def to_float(value, default=0.0):
        try:
            if value in ("-", "", None):
                return default
            return float(value)
        except (ValueError, TypeError):
            return default

    normalized_event = {
        "source": "zeek",
        "event_type": "connection",

        # AI training label
        "label": event.get("label", DEFAULT_LABEL),

        # Connection identity
        "timestamp": to_float(event.get("ts")),
        "uid": event.get("uid", ""),

        "src_ip": event.get("id.orig_h", ""),
        "src_port": to_int(event.get("id.orig_p")),

        "dst_ip": event.get("id.resp_h", ""),
        "dst_port": to_int(event.get("id.resp_p")),

        "protocol": event.get("proto", ""),
        "service": event.get("service", ""),

        # Connection statistics
        "duration": to_float(event.get("duration")),
        "orig_bytes": to_int(event.get("orig_bytes")),
        "resp_bytes": to_int(event.get("resp_bytes")),
        "orig_pkts": to_int(event.get("orig_pkts")),
        "resp_pkts": to_int(event.get("resp_pkts")),

        "conn_state": event.get("conn_state", ""),

        # TCP / connection metadata
        "local_orig": event.get("local_orig", ""),
        "local_resp": event.get("local_resp", ""),
        "missed_bytes": to_int(event.get("missed_bytes")),

        # Keep history of Zeek's original fields.
        "history": event.get("history", ""),
    }

    standardized.append(normalized_event)

with open(OUTPUT_FILE, "w") as file:
    json.dump(standardized, file, indent=2)

print(
    f"Created {OUTPUT_FILE} with "
    f"{len(standardized)} event(s), "
    f"label={DEFAULT_LABEL}"
)
