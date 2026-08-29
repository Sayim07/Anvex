import json
import os
import sys

LOG_FILE = "../zeek/logs/conn.log"
OUTPUT_FILE = "zeek_events.json"

LABEL = sys.argv[1] if len(sys.argv) > 1 else "normal"

with open(LOG_FILE, "r") as file:
    lines = file.readlines()

fields = None

for line in lines:
    line = line.strip()

    if line.startswith("#fields"):
        fields = line.split("\t")[1:]
        break

if not fields:
    raise ValueError("Could not find #fields in conn.log")

events = []

for line in lines:
    if line.startswith("#") or not line.strip():
        continue

    values = line.rstrip("\n").split("\t")

    if len(values) != len(fields):
        continue

    event = dict(zip(fields, values))

    # Preserve the scenario label for the AI pipeline.
    event["label"] = LABEL

    events.append(event)

with open(OUTPUT_FILE, "w") as file:
    json.dump(events, file, indent=2)

print(
    f"Created {OUTPUT_FILE} with "
    f"{len(events)} event(s), label={LABEL}"
)
