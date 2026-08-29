import json
from pathlib import Path

from ai_engine.features.ddos_features import extract_ddos_features
from ai_engine.features.scan_features import extract_scan_features
from ai_engine.features.c2_features import extract_c2_features
from ai_engine.features.exfil_features import extract_exfil_features


class ZeekAdapter:
    """
    Converts standardized Zeek connection events into
    inputs/features required by the Anvex AI detectors.

    This adapter currently supports connection-level data.
    DNS and TLS/JA4 integration will be added when those
    event types become available.
    """

    def __init__(self, events):
        if not events:
            raise ValueError("No Zeek events provided.")

        self.events = events

    @classmethod
    def from_json(cls, path):
        """Load standardized Zeek events from JSON."""

        path = Path(path)

        with path.open("r", encoding="utf-8") as file:
            events = json.load(file)

        return cls(events)

    # ---------------------------------
    # Common data
    # ---------------------------------

    def source_ips(self):
        return [
            event["src_ip"]
            for event in self.events
            if event.get("src_ip")
        ]

    def destination_ports(self):
        return [
            int(event["dst_port"])
            for event in self.events
            if event.get("dst_port") is not None
        ]

    def timestamps(self):
        return sorted(
            float(event["timestamp"])
            for event in self.events
            if event.get("timestamp") is not None
        )

    # ---------------------------------
    # DDoS
    # ---------------------------------

    def prepare_ddos_inputs(self):
        packet_count = sum(
            float(event.get("orig_pkts", 0))
            + float(event.get("resp_pkts", 0))
            for event in self.events
        )

        timestamps = self.timestamps()

        if len(timestamps) >= 2:
            duration_seconds = max(
                timestamps[-1] - timestamps[0],
                1e-6,
            )
        else:
            duration_seconds = sum(
                float(event.get("duration", 0))
                for event in self.events
            )

        # TCP flags are not currently preserved by
        # standardized_events.json, so true SYN counts
        # cannot be reconstructed reliably.
        syn_count = 0

        ack_count = sum(
            float(event.get("resp_pkts", 0))
            for event in self.events
        )

        return {
            "source_ips": self.source_ips(),
            "packet_count": packet_count,
            "duration_seconds": duration_seconds,
            "syn_count": syn_count,
            "ack_count": ack_count,
        }

    def extract_ddos_features(self):
        inputs = self.prepare_ddos_inputs()

        return extract_ddos_features(**inputs)

    # ---------------------------------
    # Port Scan
    # ---------------------------------

    def prepare_scan_inputs(self):
        total_connections = len(self.events)

        failed_connections = sum(
            1
            for event in self.events
            if event.get("conn_state") not in {
                "SF",
                "S1",
            }
        )

        return {
            "destination_ports": self.destination_ports(),
            "failed_connections": failed_connections,
            "total_connections": total_connections,
        }

    def extract_scan_features(self):
        inputs = self.prepare_scan_inputs()

        return extract_scan_features(**inputs)

    # ---------------------------------
    # C2 Beacon
    # ---------------------------------

    def prepare_c2_inputs(self):
        timestamps = self.timestamps()

        inter_arrival_times = [
            timestamps[i] - timestamps[i - 1]
            for i in range(1, len(timestamps))
        ]

        return {
            "inter_arrival_times": inter_arrival_times,
        }

    def extract_c2_features(self):
        inputs = self.prepare_c2_inputs()

        return extract_c2_features(**inputs)

    # ---------------------------------
    # Exfiltration
    # ---------------------------------

    def prepare_exfil_inputs(self):
        outbound_bytes = sum(
            float(event.get("orig_bytes", 0))
            for event in self.events
        )

        inbound_bytes = sum(
            float(event.get("resp_bytes", 0))
            for event in self.events
        )

        current_volume = outbound_bytes + inbound_bytes

        # No historical baseline is currently supplied
        # by the standardized Zeek data.
        baseline_volume = current_volume

        return {
            "outbound_bytes": outbound_bytes,
            "inbound_bytes": inbound_bytes,
            "current_volume": current_volume,
            "baseline_volume": baseline_volume,
        }

    def extract_exfil_features(self):
        inputs = self.prepare_exfil_inputs()

        return extract_exfil_features(**inputs)