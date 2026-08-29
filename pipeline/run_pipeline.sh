#!/bin/bash

set -e

PCAP="../pcaps/test_traffic.pcap"
LOG_DIR="../zeek/logs"

echo "=== ANVEX FULL DATA PIPELINE ==="

echo "[1/4] Cleaning old Zeek logs..."
rm -f "$LOG_DIR"/*.log

echo "[2/4] Running Zeek on PCAP..."
docker run --rm \
  -v "$(realpath ../pcaps):/pcap" \
  -v "$(realpath ../zeek/logs):/logs" \
  zeek/zeek \
  zeek -r /pcap/test_traffic.pcap Log::default_logdir=/logs

echo "[3/4] Converting Zeek logs to JSON..."
python parser.py
python normalize.py

echo "[4/4] Sending events to Redis..."
python producer.py

echo "=== ANVEX PIPELINE COMPLETED ==="
