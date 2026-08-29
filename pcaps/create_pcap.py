from scapy.all import IP, TCP, Raw, wrpcap
import random

packets = []

src = "192.168.1.10"
dst = "192.168.1.20"

for i in range(20):
    sport = 5000 + i
    client_seq = 1000 + (i * 100)
    server_seq = 2000 + (i * 100)

    # TCP SYN
    packets.append(
        IP(src=src, dst=dst) /
        TCP(sport=sport, dport=80, flags="S", seq=client_seq)
    )

    # TCP SYN-ACK
    packets.append(
        IP(src=dst, dst=src) /
        TCP(sport=80, dport=sport, flags="SA",
            seq=server_seq, ack=client_seq + 1)
    )

    # TCP ACK
    packets.append(
        IP(src=src, dst=dst) /
        TCP(sport=sport, dport=80, flags="A",
            seq=client_seq + 1, ack=server_seq + 1)
    )

    # HTTP request
    request = (
        f"GET /page{i}.html HTTP/1.1\r\n"
        f"Host: test.local\r\n"
        f"Connection: close\r\n\r\n"
    ).encode()

    packets.append(
        IP(src=src, dst=dst) /
        TCP(sport=sport, dport=80, flags="PA",
            seq=client_seq + 1, ack=server_seq + 1) /
        Raw(request)
    )

    # HTTP response
    response = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Length: 5\r\n"
        "Connection: close\r\n\r\n"
        "Hello"
    ).encode()

    packets.append(
        IP(src=dst, dst=src) /
        TCP(sport=80, dport=sport, flags="PA",
            seq=server_seq + 1,
            ack=client_seq + 1 + len(request)) /
        Raw(response)
    )

    # FIN from client
    packets.append(
        IP(src=src, dst=dst) /
        TCP(sport=sport, dport=80, flags="FA",
            seq=client_seq + 1 + len(request),
            ack=server_seq + 1 + len(response))
    )

    # FIN-ACK from server
    packets.append(
        IP(src=dst, dst=src) /
        TCP(sport=80, dport=sport, flags="FA",
            seq=server_seq + 1 + len(response),
            ack=client_seq + 2 + len(request))
    )

print(f"Generated {len(packets)} packets for 20 TCP connections.")

wrpcap("../pcaps/test_traffic.pcap", packets)

print("Realistic multi-event PCAP created successfully!")

