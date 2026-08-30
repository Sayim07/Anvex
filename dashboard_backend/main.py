"""
Anvex — Dashboard Backend
FastAPI server providing:
  - POST /api/alerts          — Real-time alert ingestion from the AI engine
  - GET  /api/verify/{id}     — On-chain alert verification via smart contract
  - WS   /ws/alerts           — Broadcasts enriched alerts to the SOC dashboard
  - WS   /ws/system-metrics   — Streams live psutil hardware + throughput metrics

Author: Sayim (Full-Stack & Web3 Developer)
"""

import asyncio
import collections
import hashlib
import json
import logging
import os
import random
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psutil
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from web3 import Web3
from web3.exceptions import ContractLogicError

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

load_dotenv(Path(__file__).parent / ".env")

MOCK_MODE: bool = os.getenv("MOCK_MODE", "true").lower() == "true"
HARDHAT_RPC_URL: str = os.getenv("HARDHAT_RPC_URL", "http://127.0.0.1:8545")
CONTRACT_INFO_PATH: str = os.getenv(
    "CONTRACT_INFO_PATH", str(Path(__file__).parent.parent / "trust_layer" / "deployed" / "contract_info.json")
)
CORS_ORIGINS: list[str] = os.getenv(
    "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
).split(",")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("anvex.backend")

# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Anvex SOC Backend",
    description="Real-time threat ingestion, blockchain notarization, and SOC WebSocket hub.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Blockchain Setup
# ---------------------------------------------------------------------------

w3: Web3 | None = None
contract = None
_blockchain_ready = False


def _load_contract_info() -> dict:
    """Load contract address and ABI from the file written by deploy.js."""
    info_path = Path(CONTRACT_INFO_PATH)
    if not info_path.exists():
        raise FileNotFoundError(
            f"contract_info.json not found at {info_path.resolve()}. "
            "Run: cd trust_layer && npx hardhat node && npm run deploy"
        )
    with open(info_path) as f:
        return json.load(f)


def _init_blockchain() -> None:
    """Connect to Hardhat and bind the ForensicAuditLedger contract."""
    global w3, contract, _blockchain_ready
    try:
        info = _load_contract_info()
        w3 = Web3(Web3.HTTPProvider(HARDHAT_RPC_URL))
        if not w3.is_connected():
            raise ConnectionError(f"Cannot connect to Hardhat at {HARDHAT_RPC_URL}")
        contract = w3.eth.contract(
            address=Web3.to_checksum_address(info["address"]),
            abi=info["abi"],
        )
        _blockchain_ready = True
        log.info("✅ Blockchain connected — contract at %s", info["address"])
    except Exception as exc:
        log.warning("⚠️  Blockchain unavailable (%s). Alerts will not be notarized.", exc)


# ---------------------------------------------------------------------------
# Blockchain Notarization
# ---------------------------------------------------------------------------

def _compute_sha256(payload: dict) -> str:
    """Compute SHA-256 of the canonical JSON representation of an alert."""
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


async def notarize_to_blockchain(alert: dict) -> dict:
    """
    Hash the alert payload, sign and send a transaction to notarizeAlert(),
    await the receipt, and return the real tx_hash and block_number.

    Returns a dict with keys: alert_hash, tx_hash, block_number.
    Falls back gracefully if the Hardhat node is not running.
    """
    if not _blockchain_ready or contract is None or w3 is None:
        return {
            "alert_hash": _compute_sha256(alert),
            "tx_hash": None,
            "block_number": None,
            "notarized": False,
        }

    try:
        alert_hash_hex = _compute_sha256(alert)
        alert_hash_bytes32 = bytes.fromhex(alert_hash_hex)

        # Scale confidence: 0.965 → 9650
        confidence_scaled = int(round(alert.get("confidence", 0.0) * 10_000))
        alert_id = alert["alert_id"]
        threat_class = alert["threat_class"]

        account = w3.eth.accounts[0]

        # Build and send the transaction
        tx = contract.functions.notarizeAlert(
            alert_id,
            alert_hash_bytes32,
            threat_class,
            confidence_scaled,
        ).transact({"from": account})

        # Await receipt (runs in executor to avoid blocking the event loop)
        loop = asyncio.get_event_loop()
        receipt = await loop.run_in_executor(
            None, lambda: w3.eth.wait_for_transaction_receipt(tx, timeout=30)
        )

        tx_hash = receipt.transactionHash.hex()
        block_number = receipt.blockNumber

        log.info("⛓  Notarized alert=%s  tx=%s  block=%d", alert_id, tx_hash, block_number)
        return {
            "alert_hash": alert_hash_hex,
            "tx_hash": tx_hash,
            "block_number": block_number,
            "notarized": True,
        }

    except ContractLogicError as exc:
        # Alert already exists (duplicate)
        log.warning("Contract revert for alert %s: %s", alert.get("alert_id"), exc)
        return {
            "alert_hash": _compute_sha256(alert),
            "tx_hash": None,
            "block_number": None,
            "notarized": False,
            "error": str(exc),
        }
    except Exception as exc:
        log.error("Blockchain error: %s", exc)
        return {
            "alert_hash": _compute_sha256(alert),
            "tx_hash": None,
            "block_number": None,
            "notarized": False,
            "error": str(exc),
        }


# ---------------------------------------------------------------------------
# Connection Manager (WebSocket hub)
# ---------------------------------------------------------------------------

class ConnectionManager:
    """Manages sets of active WebSocket connections for a named channel."""

    def __init__(self) -> None:
        self._sockets: set[WebSocket] = set()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._sockets.add(ws)

    def disconnect(self, ws: WebSocket) -> None:
        self._sockets.discard(ws)

    async def broadcast(self, data: Any) -> None:
        """Broadcast to all connected clients; silently drop stale connections."""
        dead: list[WebSocket] = []
        payload = json.dumps(data, default=str)
        for ws in list(self._sockets):
            try:
                await ws.send_text(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self._sockets.discard(ws)


alerts_hub = ConnectionManager()
metrics_hub = ConnectionManager()

# ---------------------------------------------------------------------------
# Throughput Tracker (sliding window)
# ---------------------------------------------------------------------------

# Stores event timestamps for the last 10 seconds
_event_timestamps: collections.deque[float] = collections.deque(maxlen=1000)
_pipeline_latencies: collections.deque[float] = collections.deque(maxlen=50)


def _record_event(latency_ms: float | None = None) -> None:
    now = time.monotonic()
    _event_timestamps.append(now)
    if latency_ms is not None:
        _pipeline_latencies.append(latency_ms)


def _flows_per_second(window: float = 10.0) -> float:
    now = time.monotonic()
    cutoff = now - window
    recent = [t for t in _event_timestamps if t >= cutoff]
    return round(len(recent) / window, 2)


def _avg_latency_ms() -> float:
    if not _pipeline_latencies:
        return 0.0
    return round(sum(_pipeline_latencies) / len(_pipeline_latencies), 2)


# ---------------------------------------------------------------------------
# Mock Alert Generator
# ---------------------------------------------------------------------------

_THREAT_CLASSES = ["DDOS", "PORT_SCAN", "DGA_DOMAIN", "C2_BEACON", "TLS_MALWARE", "EXFILTRATION"]

_PRIVATE_RANGES = [
    (10, 0, (1, 254), (1, 254)),
    (192, 168, (1, 10), (1, 254)),
    (172, (16, 31), (1, 254), (1, 254)),
]


def _random_private_ip() -> str:
    r = random.choice(_PRIVATE_RANGES)
    a = r[0]
    b = r[1] if isinstance(r[1], int) else random.randint(*r[1])
    c = random.randint(*r[2])
    d = random.randint(*r[3])
    return f"{a}.{b}.{c}.{d}"


def _generate_evidence(threat_class: str, confidence: float) -> dict:
    """Generate mathematically realistic evidence metrics for each threat type."""
    rng = random.random

    if threat_class == "DDOS":
        return {
            "pps": round(random.uniform(800, 5000), 2),
            "syn_ack_ratio": round(random.uniform(5.0, 20.0), 3),
            "source_ip_entropy": round(random.uniform(2.5, 4.5), 4),
        }
    elif threat_class == "PORT_SCAN":
        return {
            "dest_port_fanout": random.randint(500, 65000),
            "connection_failure_rate": round(random.uniform(0.75, 0.99), 4),
            "scan_rate_pps": round(random.uniform(100, 2000), 2),
        }
    elif threat_class == "DGA_DOMAIN":
        return {
            "subdomain_entropy": round(random.uniform(3.5, 5.2), 4),
            "ngram_anomaly_score": round(random.uniform(0.6, 0.98), 4),
            "query_frequency_hz": round(random.uniform(0.5, 8.0), 3),
        }
    elif threat_class == "C2_BEACON":
        return {
            "iat_variance_ms": round(random.uniform(0.1, 3.5), 4),
            "fft_periodicity_score": round(random.uniform(0.80, 0.99), 4),
            "beacon_interval_sec": round(random.uniform(30, 300), 1),
        }
    elif threat_class == "TLS_MALWARE":
        return {
            "ja4_fingerprint": "t13d1516h2_" + uuid.uuid4().hex[:12],
            "ja3_hash": uuid.uuid4().hex[:32],
            "splt_anomaly_score": round(random.uniform(0.70, 0.97), 4),
        }
    elif threat_class == "EXFILTRATION":
        return {
            "outbound_inbound_ratio": round(random.uniform(8.0, 50.0), 2),
            "bytes_transferred_mb": round(random.uniform(50, 2000), 2),
            "baseline_deviation_sigma": round(random.uniform(3.5, 12.0), 3),
        }
    return {}


def _generate_mock_alert() -> dict:
    """Generate a fully dynamic mock alert matching the Anvex schema."""
    threat_class = random.choice(_THREAT_CLASSES)
    confidence = round(random.uniform(0.82, 0.99), 4)
    severity = "CRITICAL" if confidence > 0.92 else "HIGH"
    alert_id = "FL-" + uuid.uuid4().hex

    return {
        "alert_id": alert_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_ip": _random_private_ip(),
        "destination_ip": _random_private_ip(),
        "source_port": random.randint(1024, 65535),
        "destination_port": random.choice([80, 443, 53, 8080, 22, 3389, 6667, random.randint(1024, 65535)]),
        "threat_class": threat_class,
        "confidence": confidence,
        "severity": severity,
        "evidence": _generate_evidence(threat_class, confidence),
        "detector": "anvex-ai-engine",
    }


# ---------------------------------------------------------------------------
# Background Tasks
# ---------------------------------------------------------------------------

async def _mock_generator_task() -> None:
    """Emits a fake alert every 2–4 seconds when MOCK_MODE is True."""
    log.info("👻 Ghost AI Generator started (MOCK_MODE=True)")
    while True:
        await asyncio.sleep(random.uniform(2.0, 4.0))
        alert = _generate_mock_alert()
        await _process_and_broadcast(alert)


async def _system_metrics_task() -> None:
    """Streams live psutil metrics to /ws/system-metrics every 1 second."""
    # Prime the CPU percent sampler
    psutil.cpu_percent(interval=None)
    while True:
        await asyncio.sleep(1.0)
        vm = psutil.virtual_memory()
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=None),
            "ram_used_mb": round(vm.used / 1024 / 1024, 1),
            "ram_percent": vm.percent,
            "flows_per_sec": _flows_per_second(),
            "avg_latency_ms": _avg_latency_ms(),
        }
        await metrics_hub.broadcast(payload)


async def _process_and_broadcast(alert: dict) -> None:
    """Notarize an alert on-chain and broadcast the enriched payload."""
    t0 = time.monotonic()
    chain_result = await notarize_to_blockchain(alert)
    latency_ms = (time.monotonic() - t0) * 1000.0

    enriched = {
        **alert,
        "alert_hash": chain_result["alert_hash"],
        "tx_hash": chain_result.get("tx_hash"),
        "block_number": chain_result.get("block_number"),
        "notarized": chain_result.get("notarized", False),
        "pipeline_latency_ms": round(latency_ms, 2),
    }

    _record_event(latency_ms)
    await alerts_hub.broadcast(enriched)


# ---------------------------------------------------------------------------
# App Lifecycle
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def on_startup() -> None:
    _init_blockchain()
    asyncio.create_task(_system_metrics_task())
    if MOCK_MODE:
        asyncio.create_task(_mock_generator_task())
    log.info("🚀 Anvex backend started  |  MOCK_MODE=%s", MOCK_MODE)


# ---------------------------------------------------------------------------
# Pydantic Models
# ---------------------------------------------------------------------------

class AlertPayload(BaseModel):
    """
    Standardized alert schema produced by the Anvex AI engine (Member 2).
    All fields matching the architecture spec.
    """
    alert_id: str = Field(..., description="Unique flow/alert identifier, e.g. FL-<uuid>")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    source_ip: str
    destination_ip: str
    source_port: int
    destination_port: int
    threat_class: str = Field(..., description="e.g. DDOS, PORT_SCAN, C2_BEACON")
    confidence: float = Field(..., ge=0.0, le=1.0)
    severity: str = Field(..., description="CRITICAL | HIGH | MEDIUM | LOW")
    evidence: dict = Field(default_factory=dict)
    detector: str = Field(default="anvex-ai-engine")


# ---------------------------------------------------------------------------
# HTTP Endpoints
# ---------------------------------------------------------------------------

@app.post("/api/alerts", summary="Ingest a threat alert from the AI engine")
async def ingest_alert(payload: AlertPayload) -> dict:
    """
    Handoff hook: the AI engine POSTs real threat detections here.
    The alert is hashed, notarized on the Hardhat blockchain, and broadcast
    to the SOC dashboard via /ws/alerts.
    """
    alert_dict = payload.model_dump()
    await _process_and_broadcast(alert_dict)
    return {"status": "accepted", "alert_id": payload.alert_id}


@app.get("/api/verify/{alert_id}", summary="Verify an alert on-chain")
async def verify_alert(alert_id: str) -> dict:
    """
    Calls verifyAlert() on the ForensicAuditLedger contract and returns
    the cryptographic proof for forensic auditors.
    """
    if not _blockchain_ready or contract is None:
        raise HTTPException(status_code=503, detail="Blockchain not available")

    try:
        result = contract.functions.verifyAlert(alert_id).call()
        alert_hash_bytes, threat_class, confidence_scaled, block_ts = result
        return {
            "alert_id": alert_id,
            "verified": True,
            "alert_hash": "0x" + alert_hash_bytes.hex(),
            "threat_class": threat_class,
            "confidence": confidence_scaled / 10_000,
            "block_timestamp": block_ts,
            "block_datetime": datetime.fromtimestamp(block_ts, tz=timezone.utc).isoformat(),
        }
    except ContractLogicError:
        raise HTTPException(status_code=404, detail=f"Alert '{alert_id}' not found on-chain")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/health", summary="Health check")
async def health() -> dict:
    return {
        "status": "ok",
        "mock_mode": MOCK_MODE,
        "blockchain_ready": _blockchain_ready,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# WebSocket Endpoints
# ---------------------------------------------------------------------------

@app.websocket("/ws/alerts")
async def ws_alerts(ws: WebSocket) -> None:
    """Live threat alert feed for the SOC dashboard."""
    await alerts_hub.connect(ws)
    try:
        while True:
            await ws.receive_text()  # Keep connection alive; client may send pings
    except WebSocketDisconnect:
        alerts_hub.disconnect(ws)


@app.websocket("/ws/system-metrics")
async def ws_system_metrics(ws: WebSocket) -> None:
    """Live hardware and throughput metrics stream."""
    await metrics_hub.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        metrics_hub.disconnect(ws)
