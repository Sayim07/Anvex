# 🛡️ ANVEX (AI Cyber Threat Intelligence & Forensic Audit Platform)

<div align="center">

![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/Frontend-React%2018%20%2B%20Vite-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![XGBoost](https://img.shields.io/badge/AI%20Engine-XGBoost%2099.86%25-FF6600?style=for-the-badge&logo=xgboost&logoColor=white)
![Hardhat](https://img.shields.io/badge/Web3-Hardhat%20EVM-yellow?style=for-the-badge&logo=ethereum&logoColor=white)
![Status](https://img.shields.io/badge/System%20Status-100%25%20Operational-22c55e?style=for-the-badge)

**Real-Time Passive Network Anomaly Detection • Explainable AI (SHAP) • Immutable Blockchain Forensic Audit Ledger**

[SIH Problem Statement PS 26145: AI-Based Cyber Threat Detection]

</div>

---

## 📌 Executive Summary

**Anvex** is an enterprise-grade, passive cybersecurity intelligence platform engineered for high-stakes, classified network environments (such as military networks, critical infrastructure, and data-diode topologies). 

Modern cyber attacks hide behind heavy TLS/HTTPS encryption, making payload inspection impossible without compromising privacy and performance. **Anvex solves this by analyzing statistical network metadata and timing patterns with zero payload decryption.** The platform couples high-speed packet flow extraction with a dual-engine AI classifier (XGBoost + Isolation Forest), streams real-time threat intelligence to a React SOC dashboard, and permanently locks cryptographic receipts (SHA-256 hashes) onto an EVM blockchain ledger to guarantee **tamper-proof forensic non-repudiation**.

---

## 🏗️ End-to-End System Architecture

```
                                  NETWORK SENSOR LAYER
                              [ Live Traffic / PCAP Replay ]
                                            │
                                            ▼
                           [ Scapy / Zeek Flow Extractor ]
                                (13 Statistical Features)
                                            │
                        ┌───────────────────┴───────────────────┐
                        ▼                                       ▼
             [ XGBoost Classifier ]                 [ Isolation Forest ]
              (99.86% Multi-Class)                 (Unsupervised Anomaly)
                        │                                       │
                        └───────────────────┬───────────────────┘
                                            ▼
                                [ SHAP Explainability ]
                             (Dynamic Evidence Generation)
                                            │
                                            ▼ M2M HTTP POST (/api/alerts)
    ┌───────────────────────────────────────────────────────────────────────────────┐
    │                       ANVEX FASTAPI CORE BACKEND (:8000)                      │
    │  • SHA-256 Cryptographic Hashing     • WebSocket Streaming Hubs              │
    │  • Flow Rate & Latency Tracking      • MOCK_MODE=false Production Pipeline    │
    └───────────────────────┬───────────────────────────────────────┬───────────────┘
                            │                                       │
               JSON-RPC     ▼                                       ▼   WebSockets (/ws/alerts)
    ┌───────────────────────────────────────┐   ┌───────────────────────────────────┐
    │     TRUST LAYER: EVM BLOCKCHAIN       │   │      MISSION-CONTROL REACT SOC    │
    │  • ForensicAuditLedger.sol (Hardhat)  │   │  • Live Threat Radar Feed         │
    │  • Tamper-Proof Event Logging         │   │  • Pause / Resume Live Buffer     │
    │  • Instant Subpoena/Audit Verification│   │  • 1-Click On-Chain Verification  │
    └───────────────────────────────────────┘   └───────────────────────────────────┘
```

---

## 🚨 Threat Detection Vectors & Evidence Matrix

Anvex passively identifies **6 critical cyber threat classes** using mathematical and statistical behavioral footprints:

| Threat Class | Primary Attack Vectors | Key Mathematical Evidence Indicators | Severity |
| :--- | :--- | :--- | :---: |
| **`DDOS`** | SYN Flood, UDP/ICMP Amplification | • High Packets-Per-Second (`pps` > 2500)<br>• Asymmetric SYN/ACK Ratio (`syn_ack_ratio` > 8.0)<br>• High Source IP Entropy | **`CRITICAL`** |
| **`C2_BEACON`** | Advanced Persistent Threats (APT), Botnet Callbacks | • Low Inter-Arrival Time Variance (`iat_variance_ms` < 1.0)<br>• High FFT Periodicity Peak Score (`fft_periodicity` > 0.85)<br>• Fixed Interval Heartbeats | **`CRITICAL`** |
| **`PORT_SCAN`** | Reconnaissance, Stealth SYN Sweeps | • High Destination Port Fan-out (`port_fanout` > 50)<br>• Elevated Connection Failure Rate (`failure_rate` > 0.85) | **`HIGH`** |
| **`TLS_MALWARE`** | Encrypted C2 Channels, Malicious Handshakes | • JA3 / JA4 Fingerprint Anomalies<br>• High Packet Size Variance & SPLT Deviations | **`HIGH`** |
| **`DGA_DOMAIN`** | Fast-Flux DNS, Domain Generation Algorithms | • Elevated Subdomain Shannon Entropy (`entropy` > 3.8)<br>• Low N-gram Character Probabilities | **`HIGH`** |
| **`EXFILTRATION`**| Covert Data Theft, Tunneling | • Extreme Outbound/Inbound Byte Ratio (`out_in_ratio` > 15.0)<br>• Baseline Volume Deviation (> 5σ) | **`CRITICAL`** |

---

## 🌟 Key Platform Features

### 1. 🧠 Dual-Engine AI with 99.86% Accuracy
* **XGBoost Multi-Class Classifier**: Trained across 3,500 balanced network flows with $F_1 = 1.00$ performance across all threat profiles.
* **Isolation Forest**: Learns normal baseline traffic distributions to spot novel, zero-day anomalous behaviors.
* **SHAP Explainability**: Replaces black-box uncertainty with exact feature attribution metrics for every alert.

### 2. ⛓️ Blockchain-Backed Forensic Immutability
* Even if an adversary achieves root privileges and wipes local OS logs, every alert's SHA-256 fingerprint is permanently sealed into `ForensicAuditLedger.sol`.
* **Legal Chain-of-Custody**: Provides court-admissible, mathematically verifiable evidence with block height and transaction stamps.

### 3. 🖥️ Modern SOC Mission-Control Dashboard
* **Sub-Second Streaming**: Push notifications delivered via native WebSockets with `< 25ms` pipeline latency.
* **Stream Pause & Memory Buffer**: Freeze the incoming threat table during massive attack bursts without dropping events; resume flushes buffered alerts in correct chronological order.
* **1-Click Cryptographic Verifier**: Validate any alert against the on-chain smart contract directly from the UI.
* **Deep Forensic Drawer**: View complete telemetry, JA3/JA4 fingerprints, and plain-English metric explanations.

---

## 🧰 Technology Stack

| Domain | Technologies |
| :--- | :--- |
| **AI / Machine Learning** | Python 3.11, XGBoost, Scikit-Learn, SHAP, NumPy, Pandas |
| **Network Telemetry** | Scapy, Zeek Metadata Formats, PCAP Stream Replay |
| **Core API & Backend** | FastAPI, Uvicorn, WebSockets, Web3.py, Pydantic v2 |
| **Web3 Trust Layer** | Solidity (`^0.8.20`), Hardhat EVM Node, Ethers.js |
| **Frontend & UI** | React 18, Vite, Vanilla CSS Design System, Google Fonts |
| **Process Management** | PM2 Process Manager, Windows Task Scheduler / Startup Daemon |

---

## 🚀 System Startup & Live Demonstration Runbook

To run and demonstrate the entire platform in **Real-Time Production Mode (Zero Mock Data)**, follow the 4-terminal sequence below:

```
┌───────────────────────────┐    ┌───────────────────────────┐    ┌───────────────────────────┐
│        TERMINAL 1         │    │        TERMINAL 2         │    │        TERMINAL 3         │
│   EVM Blockchain Node     │    │   Smart Contract + API    │    │    Mission-Control SOC    │
│  http://127.0.0.1:8545    │    │   http://localhost:8000   │    │   http://localhost:5173   │
└─────────────┬─────────────┘    └─────────────┬─────────────┘    └─────────────┬─────────────┘
              │                                │                                │
              └────────────────────────┬───────┴────────────────────────────────┘
                                       │ 
                        ┌──────────────┴──────────────┐
                        │         TERMINAL 4          │
                        │   Live AI Attack Replay     │
                        │    (Your Demo Controller)   │
                        └─────────────────────────────┘
```

---

### 🖥️ Terminal 1: The Trust Layer (Blockchain Node)
*Runs your local Ethereum proof ledger in the background.*

```powershell
cd trust_layer
npx hardhat node
```
* **What it does:** Starts an isolated Ethereum blockchain JSON-RPC node on `http://127.0.0.1:8545`. It pre-funds 20 test accounts with 10,000 ETH each to notarize cryptographic threat hashes.
* **Status:** Leave running in the background.

---

### ⚙️ Terminal 2: The Core Backend (Deploy Contract + FastAPI)
*Deploys the smart contract and boots the real-time ingestion server.*

```powershell
# Step A: Deploy the ForensicAuditLedger contract to the running blockchain
cd trust_layer
npm run deploy

# Step B: Launch the FastAPI production server
cd dashboard_backend
uvicorn main:app --reload --port 8000
```
* **What it does:**
  * `npm run deploy`: Compiles `ForensicAuditLedger.sol`, deploys it to Hardhat, and writes the address to `deployed/contract_info.json`.
  * `uvicorn main:app`: Boots the async Python backend at `http://localhost:8000`, establishes Web3 connection to the contract, and streams live system resource metrics (`/ws/system-metrics`) and threat feeds (`/ws/alerts`).
* **Status:** Leave running in the background.

---

### 🎨 Terminal 3: The SOC Dashboard (React UI)
*Hosts the mission-control Security Operations Center dashboard.*

```powershell
cd soc_frontend
npm run dev
```
* **What it does:** Starts Vite dev server and opens the dashboard at **`http://localhost:5173`**. Connects via WebSockets and awaits incoming threats with status **`🟢 System Armed — No Threats Detected`**.
* **Status:** Leave running in the background. Open `http://localhost:5173` in your browser.

---

### 🧠 Terminal 4: The Live AI Attacker & Test Catalog (Your Controller)
*Use this terminal as your live controller to trigger real attacks against the network:*

#### 🎯 Option A: The "Hands-Free" Continuous Demonstration Loop (Recommended)
```powershell
python ai_engine/live_inference.py --loop --interval 3.5
```
* **What it does:** Continuously cycles through all network attack PCAPs every 3.5s, parses raw Scapy packet flows, computes XGBoost + Isolation Forest inferences, calculates SHAP feature attributions, notarizes hashes on-chain, and streams them into the UI.

---

#### 🎯 Option B: Targeted Individual Attack Testing
You can trigger any specific cyber threat vector on demand:

| Attack Vector | Terminal 4 Command | Detection Mechanism & Indicators |
| :--- | :--- | :--- |
| **Volumetric DDoS** | `python ai_engine/live_inference.py --pcap pcaps/ddos.pcap` | High packet rate (`pps`), asymmetric SYN/ACK ratio, high IP entropy. Triggers **`CRITICAL DDOS`** (~95.8% confidence). |
| **Stealthy C2 Beacon** | `python ai_engine/live_inference.py --pcap pcaps/c2_beacon.pcap` | High FFT periodicity score, microsecond inter-arrival variance. Triggers **`CRITICAL C2_BEACON`**. |
| **Port Reconnaissance** | `python ai_engine/live_inference.py --pcap pcaps/port_scan.pcap` | Massive destination port fanout (>100 ports) with high failure rate. Triggers **`HIGH PORT_SCAN`**. |
| **Data Exfiltration** | `python ai_engine/live_inference.py --pcap pcaps/exfiltration.pcap` | Heavy outbound payload volume deviation. Triggers **`CRITICAL EXFILTRATION`**. |
| **Encrypted TLS Malware** | `python ai_engine/live_inference.py --pcap pcaps/ja4_malware.pcap` | JA4 fingerprint match and packet size variance anomalies without SSL decryption. Triggers **`HIGH JA4_MALWARE`**. |
| **DGA Domain Fast-Flux** | `python ai_engine/live_inference.py --pcap pcaps/dga.pcap` | High Shannon entropy in DNS query strings + low n-gram probability. Triggers **`HIGH DGA`**. |
| **Normal Benign Traffic** | `python ai_engine/live_inference.py --pcap pcaps/normal.pcap` | Balanced HTTP client browsing timing. Correctly classified as **`NORMAL`** (Zero False Positives). |

---

### ⚡ Quick-Launch Alternative: Single-Command PM2 Daemon
If you prefer not to manage multiple terminal tabs, launch Terminals 1, 2, and 3 simultaneously with PM2:

```powershell
pm2 start ecosystem.config.js
```
* Automatically spawns `anvex-blockchain`, `anvex-backend`, and `anvex-frontend` in background daemons.
* Manage with `pm2 status`, `pm2 logs`, or `pm2 stop all`.

---


## 🔍 Independent Forensic Verification CLI (For Judges & Auditors)

To prove to judges, forensic investigators, or legal compliance auditors that alerts are sealed into an independent consensus ledger (and not merely inside a local database), you can verify any threat directly from the command line:

### 🎯 Universal Verification CLI (`verify_proof.py`)
Pass **ANY** identifier—an **Ethereum Transaction Hash**, an **Alert SHA-256 Hash**, or an **Alert ID**:

```powershell
# Option A: Query using the Ethereum Transaction Hash
python verify_proof.py fb8400c495ab9c7ce4d5af0d8333528688ab30958baf994fbdc577e1f0f918b3

# Option B: Query using the Alert's SHA-256 Payload Hash
python verify_proof.py 0xc6b94e2e5f0245fe806aad0c8428d07b02c9654855e54f3449e2d0c4aab998d0

# Option C: Query using the Alert ID
python verify_proof.py FL-5d1cc8dd86a1

# Option D: Hands-Free (Automatically verifies the latest mined alert on-chain)
python verify_proof.py
```

#### 📋 Terminal Receipt Output:
```text
====================================================================
ANVEX ON-CHAIN FORENSIC PROOF VERIFIER (ETHEREUM LEDGER)
====================================================================
 STATUS           : [CRYPTOGRAPHICALLY VERIFIED - IMMUTABLE]
 Alert ID         : FL-5d1cc8dd86a1
 Threat Class     : DDOS
 AI Confidence    : 95.48%
 Alert SHA-256    : 0xc6b94e2e5f0245fe806aad0c8428d07b02c9654855e54f3449e2d0c4aab998d0
 Transaction Hash : 0xfb8400c495ab9c7ce4d5af0d8333528688ab30958baf994fbdc577e1f0f918b3
 Mined in Block   : 8
 Block Timestamp  : 2026-09-07 14:28:49 UTC
 Smart Contract   : 0xDc64a140Aa3E981100a9becA4E685f962f0cF6C9
====================================================================
 [Integrity Validated] Payload cannot be altered without breaking hash.
 [Non-Repudiation]   Timestamp sealed in consensus block.
====================================================================
```

### ⚡ 1-Liner PowerShell On-Chain Query
```powershell
python -c "from web3 import Web3; import json; w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545')); info = json.load(open('trust_layer/deployed/contract_info.json')); c = w3.eth.contract(address=info['address'], abi=info['abi']); tx = w3.eth.get_transaction('0xfb8400c495ab9c7ce4d5af0d8333528688ab30958baf994fbdc577e1f0f918b3'); d = c.decode_function_input(tx.input)[1]; print(f'\n=== PROOF EXTRACTED FROM BLOCKCHAIN ===\nAlert ID     : {d[\"_alertId\"]}\nThreat Class : {d[\"_threatClass\"]}\nConfidence   : {d[\"_confidence\"]/100}%\nAlert Hash   : 0x{d[\"_alertHash\"].hex()}\nMined in Block: {tx.blockNumber}\n')"
```
275: 
276: ---
277: 
278: ## 🔌 Automated Machine-to-Machine API Contract

External AI engines or sensor nodes can transmit alerts automatically using a standard HTTP POST:

```http
POST http://localhost:8000/api/alerts
Content-Type: application/json

{
  "alert_id": "FL-b440ae4926e1",
  "timestamp": "2026-08-30T00:15:00Z",
  "source_ip": "185.220.101.5",
  "destination_ip": "10.0.0.45",
  "source_port": 54321,
  "destination_port": 443,
  "threat_class": "C2_BEACON",
  "confidence": 0.965,
  "severity": "CRITICAL",
  "evidence": {
    "iat_variance_ms": 0.08,
    "fft_periodicity_score": 0.94,
    "beacon_interval_sec": 60.0
  },
  "detector": "anvex-ai-engine"
}
```

---

## 👥 Engineering & Ownership

* **Sayim** — Full-Stack & Web3 Lead (FastAPI Backend, Hardhat EVM Smart Contracts, React SOC Dashboard, E2E Integration)
* **Sarbottam** — AI/ML Architecture Lead (Feature Engineering, XGBoost & Isolation Forest Training, SHAP Explainability)
* **Ruparna** — Data Pipeline Engineer (Traffic Generation, PCAP Scenarios, Zeek Normalization)

---

<div align="center">

**Built with 🛡️ for Smart India Hackathon (SIH PS: 26145)**  
*Making Cyber Threat Evidence Mathematically Immutable.*

</div>
