# 🚀 Hackathon Build Prompt: by Sayim - Full stack & Blockchain developer role

**Target Phases:** 
- **Phase 3:** The API & Trust Layer (FastAPI Backend + Smart Contract)
- **Phase 4:** The Visuals (Real-Time SOC Dashboard)

## 📌 Project Context
I am building an AI-Based Cyber Threat Detection system for unidirectional IP traffic[cite: 2]. My teammates are building the AI models and the network pipeline[cite: 2]. I am operating independently using a "Mock-First" strategy that seamlessly switches to real data.

---

## ⚠️ STRICT RULE: ZERO HARDCODED VALUES
All data must be dynamic and generated/calculated in real-time:
1. **No static timestamps:** Generate real-time ISO UTC timestamps dynamically (`datetime.utcnow()`).
2. **No static system metrics:** Use Python `psutil` to poll actual system CPU %, RAM MB/%, and dynamically calculate real sustained alerts/flows per second[cite: 2].
3. **No fake blockchain hashes:** The backend MUST actually send a signed transaction to the local Hardhat node, await receipt, and return the authentic `tx_hash` (`receipt.transactionHash.hex()`).
4. **No static IP/Port strings:** The Ghost AI generator must dynamically randomize realistic IPv4 addresses, port distributions, and mathematical evidence.

---

## 🛠️ Step 1: The Trust Layer (Hardhat + Solidity)
Generate the setup commands and code for a local Hardhat EVM environment.
1. Write a Solidity smart contract `ForensicAuditLedger.sol` (Solidity ^0.8.20).
2. Store alerts using a dynamic struct:
   - `bytes32 alertHash` (SHA-256 of the complete incoming payload)
   - `string alertId`
   - `string threatClass`
   - `uint16 confidence` (scaled by 100, e.g. 9650 = 96.50%)
   - `uint256 timestamp` (`block.timestamp`)
3. Events & Functions:
   - `event AlertNotarized(string indexed alertId, bytes32 alertHash, string threatClass, uint256 timestamp)`
   - `function notarizeAlert(string memory _alertId, bytes32 _alertHash, string memory _threatClass, uint16 _confidence) external returns (bytes32)`
   - `function verifyAlert(string memory _alertId) external view returns (bytes32 alertHash, string memory threatClass, uint16 confidence, uint256 timestamp)`
4. Provide the Hardhat deployment script `deploy.js` to deploy to `http://127.0.0.1:8545`.

---

## 🔌 Step 2: The Dynamic Backend & Ingestion Engine (FastAPI + Web3.py)
Generate a Python FastAPI server (`main.py`) with zero hardcoding:

1. **Live System Health Poller:**
   - Use `psutil` to dynamically measure CPU utilization %, RAM usage (MB & %), and measure throughput (events processed per second via a sliding rolling window)[cite: 2].
   - Provide a WebSocket or route `/ws/system-metrics` streaming real hardware and throughput metrics every 1 second[cite: 2].

2. **Blockchain Integration (`web3.py`):**
   - Connect to local Hardhat node at `http://127.0.0.1:8545`.
   - Function `notarize_to_blockchain(alert_dict)`:
     - Calculates `hashlib.sha256(json.dumps(alert_dict, sort_keys=True).encode()).hexdigest()`.
     - Calls `notarizeAlert` on the contract.
     - Awaits `w3.eth.wait_for_transaction_receipt(tx_hash)` and extracts the real transaction hash and block number.

3. **Live Ghost AI Generator (Mock Mode):**
   - When `MOCK_MODE = True`, run a background async task emitting an alert every 2 to 4 seconds.
   - Dynamically generate:
     - `timestamp`: Current UTC time (`datetime.now(timezone.utc).isoformat()`).
     - `flow_id`: Unique dynamic UUID or monotonic identifier (e.g., `FL-` + uuid4 hex).
     - `source` / `destination`: Random dynamic private IPs (e.g., `10.0.X.X`, `192.168.1.X`).
     - `threat_class`: Selected dynamically from `["DDOS", "PORT_SCAN", "DGA_DOMAIN", "C2_BEACON", "TLS_MALWARE", "EXFILTRATION"]`[cite: 2].
     - `confidence`: Dynamic float between `0.82` and `0.99`.
     - `severity`: Dynamically set to `"CRITICAL"` if confidence > 0.92 else `"HIGH"`.
     - `evidence`: Dynamically generated mathematical metrics corresponding to the threat (e.g., random high fan-out ports for Port Scan, high entropy float for DGA, tight IAT standard deviations for C2)[cite: 2].

4. **Real Ingest Hook:**
   - Create `POST /api/alerts`. Accepts real payloads matching the schema from Member 2[cite: 2].
   - Automatically computes SHA-256 hash, notarizes on Hardhat blockchain, and broadcasts the enriched payload (including real `tx_hash` and `block_number`) to `/ws/alerts`.

---

## 🖥️ Step 3: The Real-Time SOC Dashboard (React + Vite + Tailwind + Recharts)
Build a dark-mode frontend dashboard that renders live, dynamically updating data:

1. **System Health & Throughput Bar (Top):**
   - Connects to `/ws/system-metrics`[cite: 2].
   - Displays real-time gauges: **Live CPU %**, **RAM Usage MB**, **Current Flow Ingest Rate (flows/sec)**, and **Pipeline Latency (ms)**[cite: 2].

2. **Live Threat Feed Table:**
   - Connects to `/ws/alerts`.
   - Prepends new alerts in real-time with smooth animations.
   - Color code dynamically based on `severity` (Red: CRITICAL, Amber: HIGH).
   - Display dynamic local time, Source -> Destination, Threat Class, Confidence badge, and verified On-Chain Tx Hash badge.

3. **Expandable Evidence & Explainability Drawer:**
   - Clicking any alert row expands to show the raw dynamic `evidence` dictionary (e.g., fanout metrics, entropy values, JA4 hashes)[cite: 2].

4. **Live On-Chain Verification Widget:**
   - An input bar where judges can paste any `flow_id` / `alert_id`.
   - Calls the smart contract's `verifyAlert()` function live via the backend and displays the matching on-chain cryptographic hash, block timestamp, and verification status (🟢 Verified Immutable).

---

**Execution Instruction for AI:** Please acknowledge these dynamic constraints and start with Step 1 by providing the Hardhat configuration, Solidity smart contract, and deployment script.