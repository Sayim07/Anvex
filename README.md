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

## 🚀 Quickstart & Setup Guide

### 1. Clone & Install Dependencies

```bash
# Clone the repository
git clone https://github.com/Sayim07/Anvex.git
cd Anvex

# Install Python AI & Backend Dependencies
pip install -r dashboard_backend/requirements.txt
pip install xgboost scikit-learn scapy shap joblib

# Install Trust Layer & Frontend Dependencies
cd trust_layer && npm install
cd ../soc_frontend && npm install
cd ..
```

---

### 2. Start the Complete Stack

Open separate terminal windows or use PM2:

```bash
# Terminal 1: Start Blockchain Node & Deploy Contract
cd trust_layer
npx hardhat node
# In a new tab: npm run deploy

# Terminal 2: Start FastAPI Backend (Production Mode)
cd dashboard_backend
uvicorn main:app --reload --port 8000

# Terminal 3: Launch React SOC Dashboard
cd soc_frontend
npm run dev
# Dashboard is live at: http://localhost:5173

# Terminal 4: Run Real-Time AI Inference Loop
python ai_engine/live_inference.py --loop --interval 3.5
```

---

## 🔌 Automated Machine-to-Machine API Contract

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
