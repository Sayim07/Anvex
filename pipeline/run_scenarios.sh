#!/bin/bash

set -e

PCAP_DIR="$(realpath pcaps)"
LOG_DIR="$(realpath zeek/logs)"
PIPELINE_DIR="$(realpath pipeline)"
OUTPUT_DIR="$PIPELINE_DIR/scenario_output"

mkdir -p "$OUTPUT_DIR"

SCENARIOS=(
    normal
    ddos
    port_scan
    dga
    ja4_malware
    c2_beacon
    exfiltration
)

echo "======================================"
echo "   ANVEX SCENARIO DATA PIPELINE"
echo "======================================"

for SCENARIO in "${SCENARIOS[@]}"; do

    echo ""
    echo "--------------------------------------"
    echo "Processing: $SCENARIO"
    echo "--------------------------------------"

    PCAP="$PCAP_DIR/${SCENARIO}.pcap"

    if [ ! -f "$PCAP" ]; then
        echo "[ERROR] PCAP not found: $PCAP"
        exit 1
    fi

    echo "[1/3] Cleaning old Zeek logs..."
    rm -f "$LOG_DIR"/*.log

    echo "[2/3] Running Zeek..."

    docker run --rm \
        -v "$PCAP_DIR:/pcap" \
        -v "$LOG_DIR:/logs" \
        zeek/zeek \
        zeek -r "/pcap/${SCENARIO}.pcap" Log::default_logdir=/logs

    echo "[3/3] Parsing and normalizing..."

    cd "$PIPELINE_DIR"

    python parser.py "$SCENARIO"
    python normalize.py "$SCENARIO"

    cp standardized_events.json \
        "$OUTPUT_DIR/${SCENARIO}.json"

    EVENT_COUNT=$(python -c "
import json
with open('standardized_events.json') as f:
    print(len(json.load(f)))
")

    echo "[OK] $SCENARIO -> $EVENT_COUNT standardized events"

done

echo ""
echo "======================================"
echo " ALL SCENARIOS PROCESSED SUCCESSFULLY"
echo "======================================"

echo ""
echo "Output directory:"
echo "$OUTPUT_DIR"

ls -lh "$OUTPUT_DIR"


