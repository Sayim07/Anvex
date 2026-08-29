from scapy.all import IP, TCP, UDP, DNS, DNSQR, Raw, wrpcap
import random
import os
import json

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

    for i in range(20):
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

        packets += [
            tcp_packet(
                SRC, DST, sport, 80, "S",
                client_seq
            ),

            tcp_packet(
                DST, SRC, 80, sport, "SA",
                server_seq, client_seq + 1
            ),

            tcp_packet(
                SRC, DST, sport, 80, "A",
                client_seq + 1, server_seq + 1
            ),

            tcp_packet(
                SRC, DST, sport, 80, "PA",
                client_seq + 1,
                server_seq + 1,
                request
            ),

            tcp_packet(
                DST, SRC, 80, sport, "PA",
                server_seq + 1,
                client_seq + 1 + len(request),
                response
            ),

            tcp_packet(
                SRC, DST, sport, 80, "FA",
                client_seq + 1 + len(request),
                server_seq + 1 + len(response)
            ),

            tcp_packet(
                DST, SRC, 80, sport, "FA",
                server_seq + 1 + len(response),
                client_seq + 2 + len(request)
            )
        ]

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

        packets.append(
            IP(src=src_ip, dst=target) /
            TCP(
                sport=sport,
                dport=80,
                flags="S",
                seq=random.randint(1, 1000000)
            )
        )

    return packets


# ============================================================
# 3. PORT SCAN
# ============================================================

def generate_port_scan():
    packets = []

    src = SRC
    target = DST

    for port in range(20, 121):
        packets.append(
            IP(src=src, dst=target) /
            TCP(
                sport=random.randint(30000, 60000),
                dport=port,
                flags="S",
                seq=random.randint(1, 1000000)
            )
        )

    return packets


# ============================================================
# 4. DGA / DNS-LIKE TRAFFIC
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
        "vkp62nqx.net"
    ]

    for i, domain in enumerate(domains):
        query = DNS(
            rd=1,
            qd=DNSQR(
                qname=domain,
                qtype="A"
            )
        )

        packets.append(
            IP(src=SRC, dst="8.8.8.8") /
            UDP(
                sport=40000 + i,
                dport=53
            ) /
            query
        )

    return packets


# ============================================================
# 5. JA4 / TLS-LIKE MALWARE TRAFFIC
# ============================================================

def generate_ja4_malware():
    packets = []

    # Synthetic TLS ClientHello-like payload.
    # The AI adapter can extract packet sizes and TLS-related
    # raw information from the standardized events.

    tls_payloads = [
        b"\x16\x03\x01" + b"A" * 180,
        b"\x16\x03\x01" + b"B" * 220,
        b"\x16\x03\x01" + b"C" * 260,
        b"\x16\x03\x01" + b"D" * 140
    ]

    for i, payload in enumerate(tls_payloads):
        sport = 45000 + i

        packets.append(
            tcp_packet(
                SRC,
                DST,
                sport,
                443,
                "PA",
                seq=1000 + i * 500,
                ack=2000,
                payload=payload
            )
        )

    return packets


# ============================================================
# 6. C2 BEACONING
# ============================================================

def generate_c2_beacon():
    packets = []

    # Repeated, similarly-sized outbound connections.
    # The regular packet sequence provides temporal information
    # for IAT / periodicity calculations.

    for i in range(30):
        sport = 46000 + i

        beacon = (
            b"BEACON:"
            + f"session={i:04d}".encode()
            + b":status=ok"
        )

        packets.append(
            tcp_packet(
                SRC,
                DST,
                sport,
                8080,
                "PA",
                seq=1000 + i * 100,
                ack=2000,
                payload=beacon
            )
        )

    return packets


# ============================================================
# 7. EXFILTRATION
# ============================================================

def generate_exfiltration():
    packets = []

    # Large outbound payloads with comparatively small
    # inbound traffic.

    for i in range(20):
        sport = 47000 + i

        payload = (
            b"EXFIL_DATA:"
            + bytes(random.getrandbits(8) for _ in range(1400))
        )

        packets.append(
            tcp_packet(
                SRC,
                DST,
                sport,
                9000,
                "PA",
                seq=1000 + i * 1500,
                ack=2000,
                payload=payload
            )
        )

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
