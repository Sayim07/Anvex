import json
import redis

REDIS_HOST = "localhost"
REDIS_PORT = 6379
QUEUE_NAME = "anvex_events"

r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)

print("Waiting for events...")

while True:
    result = r.blpop(QUEUE_NAME, timeout=0)

    if result:
        _, data = result
        event = json.loads(data)

        print("\nReceived event:")
        print(json.dumps(event, indent=2))

