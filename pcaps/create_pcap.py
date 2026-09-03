from scapy.all import IP, TCP, UDP, DNS, DNSQR, Raw, wrpcap
import random
import os
import json
import time

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

SRC = "192.168.1.10"
DST = "192.168.1.20"


def tcp_packet(src, dst, sport, dport, flags, seq=1000, ack=0, payload=b""):
    packet = (
        IP(src=src, dst=dst)
        / TCP(
            sport=sport,
            dport=dport,
            flags=flags,
            seq=seq,
            ack=ack
        )
    )

    if payload:
        packet = packet / Raw(payload)

    return packet


# ============================================================
# 1. NORMAL TRAFFIC
# ============================================================

def generate_normal():
    packets = []

    # Multiple internal clients
    sources = [
        "192.168.1.10",
        "192.168.1.11",
        "192.168.1.12"
    ]

    # Spread traffic over >60 seconds.
    base_time = time.time()

    for i in range(30):
        src = sources[i % len(sources)]
        sport = 5000 + i

        client_seq = 1000 + (i * 100)
        server_seq = 2000 + (i * 100)

        request = (
            f"GET /page{i}.html HTTP/1.1\r\n"
            f"Host: test.local\r\n"
            f"Connection: close\r\n\r\n"
        ).encode()

        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Length: 5\r\n"
            "Connection: close\r\n\r\n"
            "Hello"
        ).encode()

        connection_packets = [
            tcp_packet(
                src, DST, sport, 80, "S",
                client_seq
            ),

            tcp_packet(
                DST, src, 80, sport, "SA",
                server_seq, client_seq + 1
            ),

            tcp_packet(
                src, DST, sport, 80, "A",
                client_seq + 1, server_seq + 1
            ),

            tcp_packet(
                src, DST, sport, 80, "PA",
                client_seq + 1,
                server_seq + 1,
                request
            ),

            tcp_packet(
                DST, src, 80, sport, "PA",
                server_seq + 1,
                client_seq + 1 + len(request),
                response
            ),

            tcp_packet(
                src, DST, sport, 80, "FA",
                client_seq + 1 + len(request),
                server_seq + 1 + len(response)
            ),

            tcp_packet(
                DST, src, 80, sport, "FA",
                server_seq + 1 + len(response),
                client_seq + 2 + len(request)
            )
        ]

        # Give packets realistic timestamps.
        start = base_time + (i * 2.5) + random.uniform(0.0, 0.8)

        for j, packet in enumerate(connection_packets):
            packet.time = start + (j * random.uniform(0.002, 0.015))
            packets.append(packet)

    return packets


# ============================================================
# 2. DDOS-LIKE HIGH RATE TRAFFIC
# ============================================================

def generate_ddos():
    packets = []

    target = DST

    for i in range(300):
        src_ip = f"10.0.{(i // 250) + 1}.{(i % 250) + 1}"
        sport = random.randint(1024, 65535)

        packet = (
            IP(src=src_ip, dst=target) /
            TCP(
                sport=sport,
                dport=80,
                flags="S",
                seq=random.randint(1, 1000000)
            )
        )

        packet.time = time.time() + (i * 0.001)
        packets.append(packet)

    return packets


# ============================================================
# 3. PORT SCAN
# ============================================================

def generate_port_scan():
    packets = []

    src = SRC
    target = DST

    for i, port in enumerate(range(20, 121)):
        packet = (
            IP(src=src, dst=target) /
            TCP(
                sport=random.randint(30000, 60000),
                dport=port,
                flags="S",
                seq=random.randint(1, 1000000)
            )
        )

        packet.time = time.time() + (i * 0.02)
        packets.append(packet)

    return packets


# ============================================================
# 4. DGA / DNS TRAFFIC
# ============================================================

def generate_dga():
    packets = []

    domains = [
        "xkq93mzn.net",
        "qpl8v2kx.com",
        "mzq71xpa.org",
        "vbn42kqz.net",
        "pqw83nmx.com",
        "zkr19qpl.org",
        "nqx72vbm.net",
        "kxp91zqt.com",
        "qmw48xzn.org",
        "vkp62nqx.net",
        "a9k2m7qx.net",
        "p8z4v1mn.com",
        "x7q3k9za.org",
        "m2n8x5qp.net",
        "q4v7z1kx.com",
        "z9p3m6qn.org",
        "k5x8q2mv.net",
        "n7q1z4px.com",
        "v3m9k6qa.org",
        "x8p2q7zn.net",
        "q6z1m4kx.com",
        "m9x3v7qp.org",
        "k2q8z5mn.net",
        "p7n4x9qa.com"
    ]

    base_time = time.time()

    for i, domain in enumerate(domains):
        query = DNS(
            id=random.randint(1, 65535),
            qr=0,
            rd=1,
            qd=DNSQR(
                qname=domain,
                qtype="A"
            )
        )

        packet = (
            IP(src=SRC, dst="8.8.8.8") /
            UDP(
                sport=40000 + i,
                dport=53
            ) /
            query
        )

        packet.time = base_time + i * random.uniform(0.5, 2.0)
        packets.append(packet)

    return packets


# ============================================================
# 5. JA4 / TLS MALWARE TRAFFIC
# ============================================================

def generate_ja4_malware():
    packets = []

    # Synthetic TLS ClientHello-like records.
    # Metadata is included in payload so downstream adapters
    # have explicit JA3/JA4 fields available.
    for i in range(20):
        sport = 45000 + i

        ja3 = f"ja3_malware_{i % 3}"
        ja4 = f"ja4_malware_{i % 4}"

        metadata = (
            f"JA3={ja3};JA4={ja4};TLS=1.2;"
            f"SERVER_NAME=malicious-c2.example\r\n"
        ).encode()

        tls_payload = (
            b"\x16\x03\x03"
            + bytes(random.getrandbits(8) for _ in range(180 + (i % 5) * 20))
        )

        payload = metadata + tls_payload

        packet = tcp_packet(
            SRC,
            DST,
            sport,
            443,
            "PA",
            seq=1000 + i * 500,
            ack=2000,
            payload=payload
        )

        packet.time = time.time() + i * 0.25
        packets.append(packet)

    return packets


# ============================================================
# 6. C2 BEACONING
# ============================================================

def generate_c2_beacon():
    packets = []

    base_time = time.time()

    for i in range(30):
        sport = 46000 + i

        beacon = (
            b"BEACON:"
            + f"session={i:04d}".encode()
            + b":status=ok"
        )

        packet = tcp_packet(
            SRC,
            DST,
            sport,
            8080,
            "PA",
            seq=1000 + i * 100,
            ack=2000,
            payload=beacon
        )

        # Periodic beacon timing with small jitter.
        packet.time = base_time + (i * 5.0) + random.uniform(-0.15, 0.15)

        packets.append(packet)

    return packets


# ============================================================
# 7. EXFILTRATION
# ============================================================

def generate_exfiltration():
    packets = []

    base_time = time.time()

    for i in range(20):
        sport = 47000 + i

        # Large realistic outbound application payload.
        payload = (
            b"EXFIL_DATA:"
            + bytes(random.getrandbits(8) for _ in range(3000))
        )

        packet = tcp_packet(
            SRC,
            DST,
            sport,
            9000,
            "PA",
            seq=1000 + i * 3200,
            ack=2000,
            payload=payload
        )

        packet.time = base_time + (i * 0.3) + random.uniform(0.02, 0.15)
        packets.append(packet)

    return packets


# ============================================================
# WRITE SCENARIO PCAPS
# ============================================================

SCENARIOS = {
    "normal": generate_normal,
    "ddos": generate_ddos,
    "port_scan": generate_port_scan,
    "dga": generate_dga,
    "ja4_malware": generate_ja4_malware,
    "c2_beacon": generate_c2_beacon,
    "exfiltration": generate_exfiltration,
}


def main():
    labels = []

    for label, generator in SCENARIOS.items():
        packets = generator()

        filename = os.path.join(
            OUTPUT_DIR,
            f"{label}.pcap"
        )

        wrpcap(filename, packets)

        labels.append({
            "pcap": f"{label}.pcap",
            "label": label,
            "packet_count": len(packets)
        })

        print(
            f"[+] {label:15s} -> "
            f"{len(packets):4d} packets -> {filename}"
        )

    manifest_path = os.path.join(
        OUTPUT_DIR,
        "scenario_labels.json"
    )

    with open(manifest_path, "w") as f:
        json.dump(labels, f, indent=2)

    print("\n=== ANVEX SCENARIO GENERATION COMPLETE ===")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
