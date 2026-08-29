#!/bin/bash

set -e

echo "=== Anvex Data Pipeline ==="

echo "[1/3] Parsing Zeek logs..."
python parser.py

echo "[2/3] Normalizing events..."
python normalize.py

echo "[3/3] Sending events to Redis..."
python producer.py

echo "=== Pipeline completed successfully ==="
