import json
import os
import re
import sys

LOG_FILE = "../zeek/logs/conn.log"
DNS_LOG_FILE = "../zeek/logs/dns.log"

OUTPUT_FILE = "zeek_events.json"

LABEL = sys.argv[1] if len(sys.argv) > 1 else "normal"


def read_zeek_log(log_file):
    """Read a Zeek TSV log and return fields + rows."""
    if not os.path.exists(log_file):
        return [], []

    with open(log_file, "r") as file:
        lines = file.readlines()

    fields = None
    rows = []

    for line in lines:
        if line.startswith("#fields"):
            fields = line.strip().split()[1:]
            break

    if not fields:
        return [], []

    for line in lines:
        if line.startswith("#") or not line.strip():
            continue

        values = line.strip().split()

        if len(values) != len(fields):
            continue

        rows.append(dict(zip(fields, values)))

    return fields, rows


# ============================================================
# CONNECTION EVENTS
# ============================================================

_, conn_rows = read_zeek_log(LOG_FILE)

events = []

for event in conn_rows:

    normalized = {
        "source": "zeek",
        "event_type": "connection",
        "label": LABEL,

        "timestamp": event.get("ts", "0"),
        "uid": event.get("uid", ""),

        "src_ip": event.get("id.orig_h", ""),
        "src_port": event.get("id.orig_p", ""),

        "dst_ip": event.get("id.resp_h", ""),
        "dst_port": event.get("id.resp_p", ""),

        "protocol": event.get("proto", ""),
        "service": event.get("service", ""),

        "duration": event.get("duration", "0"),
        "orig_bytes": event.get("orig_bytes", "0"),
        "resp_bytes": event.get("resp_bytes", "0"),

        "orig_pkts": event.get("orig_pkts", "0"),
        "resp_pkts": event.get("resp_pkts", "0"),

        "conn_state": event.get("conn_state", ""),

        "local_orig": event.get("local_orig", ""),
        "local_resp": event.get("local_resp", ""),

        "missed_bytes": event.get("missed_bytes", "0"),
        "history": event.get("history", ""),
    }

    # --------------------------------------------------------
    # JA3 / JA4 metadata
    #
    # Our synthetic JA4 PCAP stores:
    # JA3=...;JA4=...;TLS=...;SERVER_NAME=...
    #
    # Zeek does not decode this synthetic TLS payload, so
    # metadata is extracted separately below.
    # --------------------------------------------------------

    events.append(normalized)


# ============================================================
# DNS EVENTS
# ============================================================

_, dns_rows = read_zeek_log(DNS_LOG_FILE)

for event in dns_rows:

    query = event.get("query", "")

    dns_event = {
        "source": "zeek",
        "event_type": "dns",
        "label": LABEL,

        "timestamp": event.get("ts", "0"),
        "uid": event.get("uid", ""),

        "src_ip": event.get("id.orig_h", ""),
        "src_port": event.get("id.orig_p", ""),

        "dst_ip": event.get("id.resp_h", ""),
        "dst_port": event.get("id.resp_p", ""),

        "protocol": event.get("proto", ""),
        "service": "dns",

        "dns_query": query,
        "dns_qtype": event.get("qtype_name", ""),
        "dns_rcode": event.get("rcode_name", ""),
        "dns_rejected": event.get("rejected", ""),

        "dns_trans_id": event.get("trans_id", ""),

        "dns_query_length": len(query),
    }

    events.append(dns_event)


# ============================================================
# JA3 / JA4 METADATA FROM SYNTHETIC PCAP
# ============================================================

if LABEL == "ja4_malware":

    PCAP_FILE = "../pcaps/ja4_malware.pcap"

    if os.path.exists(PCAP_FILE):

        with open(PCAP_FILE, "rb") as file:
            raw = file.read()

        text = raw.decode("latin1", errors="ignore")

        metadata_matches = re.findall(
            r"JA3=([^;]+);JA4=([^;]+);TLS=([^;]+);SERVER_NAME=([^\r\n]+)",
            text
        )

        for index, metadata in enumerate(metadata_matches):

            ja3, ja4, tls_version, server_name = metadata

            if index < len(conn_rows):

                # Find corresponding connection event.
                uid = conn_rows[index].get("uid", "")

                for event in events:

                    if (
                        event["event_type"] == "connection"
                        and event["uid"] == uid
                    ):
                        event["ja3"] = ja3
                        event["ja4"] = ja4
                        event["tls_version"] = tls_version
                        event["server_name"] = server_name
                        break


# ============================================================
# SORT EVENTS BY TIMESTAMP
# ============================================================

def timestamp_value(event):
    try:
        return float(event.get("timestamp", 0))
    except (ValueError, TypeError):
        return 0.0


events.sort(key=timestamp_value)


# ============================================================
# WRITE OUTPUT
# ============================================================

with open(OUTPUT_FILE, "w") as file:
    json.dump(events, file, indent=2)


print(
    f"Created {OUTPUT_FILE} with "
    f"{len(events)} event(s), label={LABEL}"
)

print(f"Connection events: {len(conn_rows)}")
print(f"DNS events: {len(dns_rows)}")

if LABEL == "ja4_malware":
    ja4_count = sum(
        1 for event in events
        if event.get("ja4")
    )

    print(f"JA4 enriched events: {ja4_count}")
