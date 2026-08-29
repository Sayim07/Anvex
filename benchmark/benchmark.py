import json
import time
import redis

REDIS_HOST = "localhost"
REDIS_PORT = 6379
QUEUE_NAME = "anvex_benchmark"

TEST_SIZES = [100, 1000, 5000]

r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)

event = {
    "source": "zeek",
    "event_type": "connection",
    "src_ip": "192.168.1.10",
    "src_port": 5000,
    "dst_ip": "192.168.1.20",
    "dst_port": 80,
    "protocol": "tcp",
    "service": "http",
    "duration": 0.001,
    "orig_bytes": 65,
    "resp_bytes": 62,
    "orig_pkts": 4,
    "resp_pkts": 3,
    "conn_state": "SF"
}

print("\n=== ANVEX REDIS INGESTION BENCHMARK ===")

for total_events in TEST_SIZES:

    r.delete(QUEUE_NAME)

    start = time.perf_counter()

    for _ in range(total_events):
        r.rpush(QUEUE_NAME, json.dumps(event))

    elapsed = time.perf_counter() - start
    throughput = total_events / elapsed

    queue_size = r.llen(QUEUE_NAME)

    print(f"\nEvents sent : {total_events}")
    print(f"Time taken  : {elapsed:.6f} seconds")
    print(f"Throughput  : {throughput:.2f} events/sec")
    print(f"Queue size  : {queue_size}")

print("\n=== BENCHMARK COMPLETED ===")
