import json

INPUT_FILE = "zeek_events.json"
OUTPUT_FILE = "standardized_events.json"

with open(INPUT_FILE, "r") as file:
    events = json.load(file)

standardized = []

for event in events:
    normalized_event = {
        "source": "zeek",
        "event_type": "connection",
        "timestamp": float(event["ts"]),
        "src_ip": event["id.orig_h"],
        "src_port": int(event["id.orig_p"]),
        "dst_ip": event["id.resp_h"],
        "dst_port": int(event["id.resp_p"]),
        "protocol": event["proto"],
        "service": event["service"],
        "duration": float(event["duration"]),
        "orig_bytes": int(event["orig_bytes"]),
        "resp_bytes": int(event["resp_bytes"]),
        "orig_pkts": int(event["orig_pkts"]),
        "resp_pkts": int(event["resp_pkts"]),
        "conn_state": event["conn_state"]
    }

    standardized.append(normalized_event)

with open(OUTPUT_FILE, "w") as file:
    json.dump(standardized, file, indent=2)

print(f"Created {OUTPUT_FILE} with {len(standardized)} event(s)")
