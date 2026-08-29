import os
import math
import numpy as np
from scapy.all import rdpcap, IP, TCP, UDP, DNS, DNSQR

def compute_entropy(labels):
    if not labels:
        return 0.0
    total = len(labels)
    counts = {}
    for item in labels:
        counts[item] = counts.get(item, 0) + 1
    entropy = 0.0
    for count in counts.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy

def compute_fft_periodicity(timestamps):
    if len(timestamps) < 4:
        return 0.0
    diffs = np.diff(timestamps)
    if len(diffs) < 2 or np.std(diffs) == 0:
        return 0.95
    # Normalizing FFT spectrum peak
    fft_vals = np.abs(np.fft.rfft(diffs - np.mean(diffs)))
    if len(fft_vals) <= 1:
        return 0.0
    peak = np.max(fft_vals[1:])
    total = np.sum(fft_vals[1:])
    return float(np.clip(peak / (total + 1e-6) * 2.0, 0.0, 0.99))

def extract_features_from_pcap(pcap_path: str) -> tuple[dict, dict]:
    """
    Parses a PCAP file and extracts:
    1. Flow Context (src_ip, dst_ip, src_port, dst_port, packet_count)
    2. 13-column Feature Vector for AI Model inference.
    """
    packets = rdpcap(pcap_path)
    if not packets:
        raise ValueError(f'Empty PCAP file: {pcap_path}')

    src_ips = []
    dst_ips = []
    src_ports = []
    dst_ports = []
    packet_sizes = []
    timestamps = []
    syn_count = 0
    ack_count = 0
    rst_count = 0
    dns_queries = []
    outbound_bytes = 0
    inbound_bytes = 0

    primary_src = None
    primary_dst = None

    for pkt in packets:
        ts = float(pkt.time)
        timestamps.append(ts)
        size = len(pkt)
        packet_sizes.append(size)

        if IP in pkt:
            s_ip = pkt[IP].src
            d_ip = pkt[IP].dst
            src_ips.append(s_ip)
            dst_ips.append(d_ip)
            if not primary_src:
                primary_src = s_ip
                primary_dst = d_ip

            if s_ip == primary_src:
                outbound_bytes += size
            else:
                inbound_bytes += size

        if TCP in pkt:
            src_ports.append(pkt[TCP].sport)
            dst_ports.append(pkt[TCP].dport)
            flags = pkt[TCP].flags
            if 'S' in flags:
                syn_count += 1
            if 'A' in flags:
                ack_count += 1
            if 'R' in flags:
                rst_count += 1

        elif UDP in pkt:
            src_ports.append(pkt[UDP].sport)
            dst_ports.append(pkt[UDP].dport)

        if DNS in pkt and pkt.haslayer(DNSQR):
            qname = pkt[DNSQR].qname.decode('utf-8', errors='ignore')
            dns_queries.append(qname)

    # Calculate features
    duration = max(timestamps[-1] - timestamps[0], 0.001) if len(timestamps) > 1 else 1.0
    pps = len(packets) / duration
    syn_ack_ratio = (syn_count / max(ack_count, 1)) if syn_count > 0 else 1.0
    port_fanout = len(set(dst_ports)) if dst_ports else 1
    failure_rate = (rst_count + max(0, syn_count - ack_count)) / max(len(packets), 1)
    
    # DNS / Subdomain Entropy
    if dns_queries:
        subdomain_entropy = np.mean([compute_entropy(list(q.split('.')[0])) for q in dns_queries])
        ngram_prob = max(0.01, 1.0 / (len(set(dns_queries[0])) + 1))
    else:
        subdomain_entropy = 1.5
        ngram_prob = 0.25

    # Timing / IAT / Periodicity
    if len(timestamps) > 2:
        iats = np.diff(timestamps) * 1000.0  # ms
        iat_variance = float(np.var(iats))
        fft_periodicity = compute_fft_periodicity(timestamps)
    else:
        iat_variance = 5.0
        fft_periodicity = 0.1

    # Packet Sizes
    mean_pkt_size = float(np.mean(packet_sizes))
    pkt_size_var = float(np.var(packet_sizes)) if len(packet_sizes) > 1 else 100.0

    # Volume Ratios
    out_in_ratio = (outbound_bytes / max(inbound_bytes, 1)) if inbound_bytes > 0 else 5.0
    vol_ratio = (outbound_bytes + inbound_bytes) / 2000.0

    flow_meta = {
        'source_ip': primary_src or '192.168.1.10',
        'destination_ip': primary_dst or '192.168.1.20',
        'source_port': src_ports[0] if src_ports else 45000,
        'destination_port': dst_ports[0] if dst_ports else 80,
        'packet_count': len(packets),
        'duration_sec': round(duration, 3)
    }

    feature_vector = {
        'source_ip_entropy': round(float(compute_entropy(src_ips)), 4),
        'pps': round(float(pps), 2),
        'syn_ack_ratio': round(float(syn_ack_ratio), 3),
        'port_fanout': int(port_fanout),
        'connection_failure_rate': round(float(np.clip(failure_rate, 0.0, 1.0)), 4),
        'subdomain_entropy': round(float(subdomain_entropy), 4),
        'ngram_probability': round(float(ngram_prob), 4),
        'packet_size_variance': round(float(pkt_size_var), 2),
        'mean_packet_size': round(float(mean_pkt_size), 2),
        'iat_variance': round(float(iat_variance), 4),
        'fft_periodicity': round(float(fft_periodicity), 4),
        'outbound_inbound_ratio': round(float(out_in_ratio), 2),
        'volume_baseline_ratio': round(float(vol_ratio), 2),
    }

    return flow_meta, feature_vector

if __name__ == '__main__':
    import glob
    pcap_files = glob.glob('pcaps/*.pcap')
    print(f'Discovered {len(pcap_files)} PCAP files to test.')
    for p in pcap_files:
        meta, feats = extract_features_from_pcap(p)
        print(f'---\nFile: {p}\nMeta: {meta}\nFeatures sample: pps={feats["pps"]}, syn_ack_ratio={feats["syn_ack_ratio"]}, fanout={feats["port_fanout"]}')
