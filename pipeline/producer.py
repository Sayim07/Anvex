import json
import redis

REDIS_HOST = "localhost"
REDIS_PORT = 6379
QUEUE_NAME = "anvex_events"
INPUT_FILE = "standardized_events.json"


def main():
    try:
        # Connect to Redis
        r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True
        )

        r.ping()
        print("Redis connection successful.")

        # Load standardized events
        try:
            with open(INPUT_FILE, "r") as file:
                events = json.load(file)
        except FileNotFoundError:
            print(f"ERROR: Input file not found: {INPUT_FILE}")
            return
        except json.JSONDecodeError:
            print(f"ERROR: Invalid JSON in {INPUT_FILE}")
            return

        if not isinstance(events, list):
            print("ERROR: Expected a list of events in the JSON file.")
            return

        # Send events to Redis
        sent = 0

        for event in events:
            try:
                r.rpush(QUEUE_NAME, json.dumps(event))
                sent += 1
            except (TypeError, ValueError) as e:
                print(f"WARNING: Skipping invalid event: {e}")

        print(
            f"Successfully sent {sent}/{len(events)} "
            f"event(s) to Redis queue: {QUEUE_NAME}"
        )

    except redis.exceptions.ConnectionError:
        print("ERROR: Could not connect to Redis.")
        print("Make sure the anvex-redis container is running.")

    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    main()
