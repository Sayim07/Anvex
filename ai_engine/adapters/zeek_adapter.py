"""
ZeekAdapter
===========
Converts standardised Zeek connection events (pipeline/scenario_output/)
into the inputs and feature vectors required by the Anvex AI detectors.

Supported event types
---------------------
- ``connection`` events (Zeek conn.log): present in all scenarios.
- ``dns`` events (Zeek dns.log): present in the DGA scenario with field
  ``dns_query``.  Enables subdomain_entropy / ngram_probability features.
  Other scenarios do not have DNS events.
- TLS fingerprints (ja3/ja4): present in the ja4_malware scenario as fields
  on connection events.  Other scenarios do not have TLS fingerprints.

Field availability notes (current pipeline state, 2026-08)
-----------------------------------------------------------
- No TCP flag counts  -> syn_ack_ratio derived from ``history`` proxy.
- DNS ``dns_query``   -> present in DGA scenario events (event_type=="dns").
                         Absent in all other scenarios -> features remain 0.0.
- JA3/JA4 strings     -> present in ja4_malware scenario connection events.
                         Absent in other scenarios -> ja3/ja4 = None.
- No per-packet sizes -> mean_packet_size approximated as orig_bytes/orig_pkts;
                         packet_size_variance = 0.0 (requires packet-level data).
- orig_bytes/resp_bytes missing in most attack scenarios (marked by
  orig_bytes_missing=1).  Zero bytes must NOT be treated as payload evidence.
- No historical volume baseline -> volume_baseline_ratio explicitly unavailable.
"""

import json
from pathlib import Path

from ai_engine.features.ddos_features import extract_ddos_features
from ai_engine.features.scan_features import extract_scan_features
from ai_engine.features.c2_features import extract_c2_features
from ai_engine.features.exfil_features import extract_exfil_features
from ai_engine.features.dga_features import extract_dga_features
from ai_engine.features.ja4_features import extract_ja4_features


# ---------------------------------------------------------------------------
# Zeek ``history`` field helpers
# ---------------------------------------------------------------------------
# Zeek encodes the packet exchange history as a string of single-character
# codes.  Upper-case = originator; lower-case = responder.
#   S / s  -- SYN sent/received
#   A / a  -- ACK sent/received
#   D / d  -- data packet
#   F / f  -- FIN
#   R / r  -- RST
#   H      -- SYN+ACK (half-open reply)
#
# These are *connection-level* aggregates, not per-packet counts, so the
# derived SYN/ACK counts are approximate proxies only.

def _syn_ack_from_history(history_string):
    """
    Derive approximate SYN and ACK counts from a Zeek history string.

    Returns (syn_count, ack_count).

    Limitation: history is a *set* of observed codes, not a packet count.
    'S' means at least one SYN was observed, not that exactly one was sent.
    """
    if not history_string:
        return 0, 0

    h = history_string  # e.g. "ShADdFf" or "S" or "D"

    # Upper-case 'S' = originator SYN
    syn_count = h.count("S")

    # Upper-case 'A' = originator ACK; lower-case 'a' = responder ACK
    ack_count = h.count("A") + h.count("a")

    return syn_count, ack_count


def _aggregate_syn_ack(events):
    """Sum approximate syn/ack counts across all events via history proxy."""
    total_syn = 0
    total_ack = 0
    for event in events:
        history = event.get("history", "")
        s, a = _syn_ack_from_history(history)
        total_syn += s
        total_ack += a
    return total_syn, total_ack


# ---------------------------------------------------------------------------
# Packet-size approximation helper
# ---------------------------------------------------------------------------

def _approximate_packet_sizes(events):
    """
    Approximate per-packet sizes from connection-level byte totals.

    Each connection contributes one representative size:
        (orig_bytes + resp_bytes) / (orig_pkts + resp_pkts)

    This is a coarse approximation.  Real per-packet sizes require
    Zeek packet-capture data.  Variance from these values will
    significantly understate the true per-packet variance.

    Returns a list of float sizes (one per connection with non-zero packets).
    """
    sizes = []
    for event in events:
        orig_bytes = float(event.get("orig_bytes", 0) or 0)
        resp_bytes = float(event.get("resp_bytes", 0) or 0)
        orig_pkts = float(event.get("orig_pkts", 0) or 0)
        resp_pkts = float(event.get("resp_pkts", 0) or 0)

        total_bytes = orig_bytes + resp_bytes
        total_pkts = orig_pkts + resp_pkts

        if total_pkts > 0:
            sizes.append(total_bytes / total_pkts)

    return sizes


# ---------------------------------------------------------------------------
# ZeekAdapter
# ---------------------------------------------------------------------------

class ZeekAdapter:
    """
    Converts standardised Zeek connection events into
    inputs/features required by the Anvex AI detectors.

    This adapter supports connection-level data only.
    DNS and TLS/JA4 integration requires upstream pipeline changes
    (see prepare_dga_inputs and prepare_ja4_inputs docstrings).
    """

    def __init__(self, events):
        if not events:
            raise ValueError("No Zeek events provided.")
        self.events = events

    # ------------------------------------------------------------------
    # Constructors
    # ------------------------------------------------------------------

    @classmethod
    def from_json(cls, path):
        """Load standardised Zeek events from a JSON file."""
        path = Path(path)
        with path.open("r", encoding="utf-8") as fh:
            events = json.load(fh)
        return cls(events)

    @classmethod
    def from_scenario_json(cls, path):
        """
        Load a per-scenario JSON file (e.g. pipeline/scenario_output/ddos.json).

        Identical to from_json but makes the intent explicit: one file
        corresponds to one scenario/label, and all events share the same
        label field.
        """
        return cls.from_json(path)

    # ------------------------------------------------------------------
    # Common data accessors
    # ------------------------------------------------------------------

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

    def get_labels(self):
        """
        Return the list of unique labels present in the loaded events.

        For a per-scenario file this will be a single-element list.
        For all_standardized_events.json it will be all seven labels.
        """
        return list({
            event.get("label")
            for event in self.events
            if event.get("label") is not None
        })

    def primary_label(self):
        """
        Return the single label for a per-scenario file.

        Raises ValueError if more than one label is present.
        """
        labels = self.get_labels()
        if len(labels) == 1:
            return labels[0]
        raise ValueError(
            f"Multiple labels present ({labels}). "
            "Use from_scenario_json() on a single-label file, "
            "or call get_labels() and handle each group separately."
        )

    # ------------------------------------------------------------------
    # DDoS
    # ------------------------------------------------------------------

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
            duration_seconds = max(
                sum(
                    float(event.get("duration", 0))
                    for event in self.events
                ),
                1e-6,
            )

        # Use history-field proxy for SYN/ACK counts.
        # Limitation: history 'S' indicates at least one SYN was observed;
        # it is not an exact per-packet count.
        syn_count, ack_count = _aggregate_syn_ack(self.events)

        return {
            "source_ips": self.source_ips(),
            "packet_count": packet_count,
            "duration_seconds": duration_seconds,
            "syn_count": syn_count,
            "ack_count": ack_count,
        }

    def extract_ddos_features(self):
        return extract_ddos_features(**self.prepare_ddos_inputs())

    # ------------------------------------------------------------------
    # Port Scan
    # ------------------------------------------------------------------

    def prepare_scan_inputs(self):
        total_connections = len(self.events)

        failed_connections = sum(
            1
            for event in self.events
            if event.get("conn_state") not in {"SF", "S1"}
        )

        return {
            "destination_ports": self.destination_ports(),
            "failed_connections": failed_connections,
            "total_connections": total_connections,
        }

    def extract_scan_features(self):
        return extract_scan_features(**self.prepare_scan_inputs())

    # ------------------------------------------------------------------
    # DGA
    # ------------------------------------------------------------------

    def prepare_dga_inputs(self):
        """
        Prepare DGA feature inputs from Zeek events.

        DNS availability (updated 2026-08)
        -----------------------------------
        Ruparna's pipeline now emits ``dns`` events (event_type=="dns") in the
        DGA scenario with the field ``dns_query`` containing the full DNS
        query string.  This method extracts those queries and passes the most
        representative one (longest) to the DGA feature extractor.

        For scenarios without DNS events (normal, ddos, port_scan, c2_beacon,
        ja4_malware, exfiltration) the method returns subdomain=None, which
        causes the DGA detector to abstain rather than produce a false result.

        Field lookup order (tolerates variations from future pipeline changes):
            1. ``dns_query``   -- Ruparna's current field name (2026-08)
            2. ``query``       -- alternative field name
            3. ``subdomain``   -- legacy field name
        """
        queries = []
        for event in self.events:
            if event.get("event_type") != "dns":
                continue
            # Prefer dns_query (Ruparna's field), fall back to alternatives.
            q = (
                event.get("dns_query")
                or event.get("query")
                or event.get("subdomain")
            )
            if q:
                queries.append(str(q))

        if queries:
            # Use the longest query string as most representative.
            subdomain = max(queries, key=len)
        else:
            # No DNS events in this scenario — DGA detector will abstain.
            subdomain = None

        return {
            "subdomain": subdomain,
        }

    def extract_dga_features(self):
        return extract_dga_features(**self.prepare_dga_inputs())

    # ------------------------------------------------------------------
    # JA4 / TLS
    # ------------------------------------------------------------------

    def prepare_ja4_inputs(self):
        """
        Prepare JA4/TLS feature inputs from Zeek events.

        LIMITATION -- upstream data required
        -------------------------------------
        JA4 detection requires TLS fingerprint strings (ja4, ja3) from
        Zeek ssl.log.  The current standardised event schema is connection-
        level only and does not include TLS fields.

        This method returns:
        - ja4=None, ja3=None  (TLS fingerprints absent upstream)
        - packet_sizes approximated as (orig_bytes+resp_bytes)/total_pkts
          (coarse proxy; real SPLT requires per-packet capture data)
        - packet_times=[]  (per-packet timestamps absent upstream)

        To unblock JA4 detection, Ruparna needs to enrich the scenario output
        with Zeek ssl.log records containing at minimum:
            { "event_type": "ssl", "ja3": "<md5>", "ja4": "<fingerprint>",
              "orig_bytes": <int>, "resp_bytes": <int> }
        """
        # Read JA3/JA4 if upstream ever adds them.
        ja4 = next(
            (event.get("ja4") for event in self.events if event.get("ja4")),
            None,
        )
        ja3 = next(
            (event.get("ja3") for event in self.events if event.get("ja3")),
            None,
        )

        # Approximate packet sizes from connection byte totals.
        # Variance will be underestimated -- see helper docstring.
        packet_sizes = _approximate_packet_sizes(self.events)

        # Per-packet timestamps are unavailable from conn.log.
        packet_times = []

        return {
            "ja4": ja4,
            "ja3": ja3,
            "packet_sizes": packet_sizes,
            "packet_times": packet_times,
        }

    def extract_ja4_features(self):
        return extract_ja4_features(**self.prepare_ja4_inputs())

    # ------------------------------------------------------------------
    # C2 Beacon
    # ------------------------------------------------------------------

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
        return extract_c2_features(**self.prepare_c2_inputs())

    # ------------------------------------------------------------------
    # Exfiltration
    # ------------------------------------------------------------------

    def prepare_exfil_inputs(self):
        """
        Prepare exfiltration feature inputs.

        Byte availability note
        ----------------------
        Most attack scenarios (c2, ddos, port_scan, exfil, ja4) have
        orig_bytes_missing=1 and orig_bytes=0.  When bytes are all 0 the
        outbound_inbound_ratio will be 0.0 and the exfil detector cannot fire.
        This is correct behaviour — absent bytes must not generate exfil evidence.

        Baseline note
        -------------
        No historical volume baseline is supplied by the pipeline.  We do NOT
        set baseline_volume = current_volume (that always yields ratio=1.0 which
        is a meaningless constant).  Instead we signal baseline as unavailable
        so the scorer/detector can treat volume_baseline_ratio as UNAVAILABLE.
        """
        # Only count bytes for events where byte fields are not missing.
        outbound_bytes = sum(
            float(event.get("orig_bytes", 0) or 0)
            for event in self.events
            if not event.get("orig_bytes_missing", 0)
        )

        inbound_bytes = sum(
            float(event.get("resp_bytes", 0) or 0)
            for event in self.events
            if not event.get("resp_bytes_missing", 0)
        )

        current_volume = outbound_bytes + inbound_bytes

        # No historical baseline available — do not fabricate one.
        # Pass None to signal unavailability to extract_exfil_features.
        # The caller will receive volume_baseline_ratio = 0.0 (formula:
        # current/None -> 0.0 via the safe guard in extract_exfil_features).
        baseline_volume = None

        return {
            "outbound_bytes": outbound_bytes,
            "inbound_bytes": inbound_bytes,
            "current_volume": current_volume,
            "baseline_volume": baseline_volume,
        }

    def extract_exfil_features(self):
        return extract_exfil_features(**self.prepare_exfil_inputs())

    # ------------------------------------------------------------------
    # Full 13-feature vector assembly
    # ------------------------------------------------------------------

    def assemble_feature_vector(self):
        """
        Assemble the complete 13-feature AI input vector.

        Returns a dict with all 13 named features expected by the XGBoost
        model and SHAP explainer.  Feature names match the training schema
        in ai_engine/data/training.csv exactly.

        Feature availability by source
        --------------------------------
        AVAILABLE (computed from connection events):
          source_ip_entropy, pps, port_fanout,
          connection_failure_rate, iat_variance, fft_periodicity

        AVAILABLE IN SPECIFIC SCENARIOS:
          subdomain_entropy   -- available in DGA scenario (dns_query field present)
          ngram_probability   -- available in DGA scenario (dns_query field present)
          ja3 / ja4           -- available in ja4_malware scenario (connection events)
          subdomain_entropy / ngram_probability = 0.0 for all non-DGA scenarios

        PARTIAL (approximated or degenerate for zero-byte events):
          syn_ack_ratio       -- history-field proxy, not exact flag counts
          mean_packet_size    -- orig_bytes/orig_pkts approx; 0 if bytes=0
          packet_size_variance-- approximated; underestimated; 0 if bytes=0
          outbound_inbound_ratio -- 0.0 when orig_bytes=resp_bytes=0 (most attacks)

        UNAVAILABLE (absent from upstream data):
          volume_baseline_ratio  -- no historical baseline; marked unavailable
                                    (returned as None, not 1.0)

        Returns
        -------
        dict : keys are the 13 feature names, values are float.
        """
        ddos_feat = self.extract_ddos_features()
        scan_feat = self.extract_scan_features()
        dga_feat = self.extract_dga_features()
        ja4_feat = self.extract_ja4_features()
        c2_feat = self.extract_c2_features()
        exfil_feat = self.extract_exfil_features()

        return {
            # DDoS features
            "source_ip_entropy": ddos_feat["source_ip_entropy"],
            "pps": ddos_feat["pps"],
            "syn_ack_ratio": ddos_feat["syn_ack_ratio"],
            # Port Scan features
            "port_fanout": float(scan_feat["port_fanout"]),
            "connection_failure_rate": scan_feat["connection_failure_rate"],
            # DGA features  (0.0 when DNS query field absent upstream)
            "subdomain_entropy": dga_feat["subdomain_entropy"],
            "ngram_probability": dga_feat["ngram_probability"],
            # JA4/TLS features  (approximated from byte totals)
            "mean_packet_size": ja4_feat["mean_packet_size"],
            "packet_size_variance": ja4_feat["packet_size_variance"],
            # C2 features
            "iat_variance": c2_feat["iat_variance"],
            "fft_periodicity": c2_feat["fft_periodicity"],
            # Exfil features
            "outbound_inbound_ratio": exfil_feat["outbound_inbound_ratio"],
            "volume_baseline_ratio": exfil_feat["volume_baseline_ratio"],
        }