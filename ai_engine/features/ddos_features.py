from collections import Counter
from math import log2


def calculate_source_ip_entropy(source_ips):
    """
    Calculate Shannon entropy of source IP addresses.

    Higher entropy generally means the traffic is distributed
    across a larger/more varied set of source IPs.
    """

    if not source_ips:
        return 0.0

    counts = Counter(source_ips)
    total = len(source_ips)

    entropy = 0.0

    for count in counts.values():
        probability = count / total
        entropy -= probability * log2(probability)

    return entropy


def calculate_pps(packet_count, duration_seconds):
    """
    Calculate packets per second (PPS).
    """

    if duration_seconds <= 0:
        return 0.0

    return packet_count / duration_seconds


def calculate_syn_ack_ratio(syn_count, ack_count):
    """
    Calculate SYN-to-ACK ratio.
    """

    if ack_count == 0:
        return float(syn_count)

    return syn_count / ack_count


def extract_ddos_features(
    source_ips,
    packet_count,
    duration_seconds,
    syn_count,
    ack_count
):
    """
    Extract the three DDoS-related features defined
    in the Anvex architecture.
    """

    return {
        "source_ip_entropy": calculate_source_ip_entropy(source_ips),
        "pps": calculate_pps(packet_count, duration_seconds),
        "syn_ack_ratio": calculate_syn_ack_ratio(syn_count, ack_count),
    }