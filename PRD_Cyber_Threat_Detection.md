# Product Requirements Document (PRD)
## AI-Based Cyber Threat Detection System for Unidirectional IP Traffic

**Project Codename:** Avnex
**Document Owner:** Sayim (Full-Stack & Blockchain Developer)
**Team:** Sayim (Backend/Blockchain/Frontend), Sarbottam (AI/Detection Models), Ruparna (Network/Data Pipeline)
**Version:** 1.0
**Status:** Active Build — Mock-First Strategy

---

## 1. Overview

### 1.1 Problem Statement
Modern networks are exposed to threats (DDoS, port scanning, DGA-based C2 domains, malware beaconing, TLS-based malware, data exfiltration) that must be detected in real time from **unidirectional IP traffic** (traffic observed one-way, e.g. via a network tap or mirrored port, with no ability to see return traffic). Security teams need a system that can:
- Detect threats using AI/ML models trained on unidirectional flow data
- Present detections to analysts in real time with full context and evidence
- Guarantee the detection record cannot be tampered with after the fact (forensic integrity)

### 1.2 Solution Summary
A three-layer system:
1. **Detection Layer** (Sarbottam) — AI models that classify unidirectional flows into threat categories with confidence scores
2. **Pipeline Layer** (Ruparna) — Ingests raw network flow data, normalizes it, and feeds it to the detection layer
3. **Trust & Visualization Layer** (Sayim, this PRD's scope) — Notarizes every alert on an immutable ledger (blockchain) and presents live threat intelligence via a Security Operations Center (SOC) dashboard

### 1.3 Build Strategy: Mock-First
Sayim's layer is built and fully functional **before** the AI model and pipeline are complete, using a realistic synthetic ("Ghost AI") data generator that mimics the exact schema and behavior of the real system. Switching from mock to real data requires **zero architectural changes** — only a config flag (`MOCK_MODE=false`).

---

## 2. Goals & Non-Goals

### 2.1 Goals
- Build a tamper-proof audit trail for every threat alert using a blockchain smart contract
- Provide a real-time, zero-hardcoded-values SOC dashboard for live monitoring
- Ensure the backend can accept real AI model output with no schema/API changes
- Allow any alert to be independently verified as authentic and unaltered ("Verify" feature)
- Demonstrate live system health (CPU, RAM, throughput) transparently, not simulated

### 2.2 Non-Goals
- Training or evaluating the AI detection models (Sarbottam's scope)
- Building the network traffic capture/ingestion pipeline (Ruparna's scope)
- Production-grade blockchain deployment (mainnet, gas optimization, multi-node consensus) — local Hardhat EVM is sufficient for this phase
- User authentication / role-based access control (out of scope for MVP/hackathon)

---

## 3. Hard Constraint: Zero Hardcoded Values
This is a **non-negotiable rule** across the entire system:

| Category | Rule |
|---|---|
| Timestamps | Always generated at runtime (`datetime.now(timezone.utc)`), never static strings |
| System metrics | CPU %, RAM MB/%, throughput must be polled live via `psutil`, never simulated with fixed numbers |
| Blockchain hashes | Every `tx_hash` must come from a real signed transaction sent to Hardhat, with an awaited receipt — never a fabricated hex string |
| IPs / Ports | Randomized dynamically within realistic ranges — never fixed sample values |
| Mock data schema | Must be structurally identical to real AI/pipeline output, so no refactor is needed when switching to live data |

---

## 4. System Architecture

```
┌─────────────────┐      ┌──────────────────────┐      ┌────────────────────┐
│  AI Detection /  │      │   FastAPI Backend     │      │   Hardhat Local     │
│  Pipeline Layer   │─────▶│   (dashboard_backend) │─────▶│   EVM + Solidity    │
│ (Sarbottam/       │ POST │                       │ web3.py │ ForensicAudit     │
│  Ruparna) OR       │      │  - /api/alerts        │      │ Ledger.sol         │
│  Mock Ghost AI     │      │  - /ws/alerts         │      └────────────────────┘
│  (MOCK_MODE=True)  │      │  - /ws/system-metrics │
└─────────────────┘      │  - /api/verify/{id}   │
                            │  - /api/health        │
                            └──────────┬────────────┘
                                       │ WebSocket
                                       ▼
                            ┌────────────────────────┐
                            │  React SOC Dashboard     │
                            │  - System Health Bar     │
                            │  - Live Threat Feed       │
                            │  - Evidence Drawer        │
                            │  - Blockchain Verifier    │
                            └────────────────────────┘
```

---

## 5. Functional Requirements

### 5.1 Phase 1 — Trust Layer (Hardhat + Solidity)

| ID | Requirement |
|---|---|
| FR-1.1 | Deploy `ForensicAuditLedger.sol` (Solidity ^0.8.20) to a local Hardhat node (`http://127.0.0.1:8545`) |
| FR-1.2 | Contract stores: `alertHash (bytes32)`, `alertId (string)`, `threatClass (string)`, `confidence (uint16, x100 scaled)`, `timestamp (uint256)` |
| FR-1.3 | Emit `AlertNotarized` event on every successful write |
| FR-1.4 | Expose `notarizeAlert()` (write) and `verifyAlert()` (read) functions |
| FR-1.5 | Provide a deploy script that writes contract address + ABI to a JSON file consumable by the backend |

### 5.2 Phase 2 — Backend (FastAPI + web3.py)

| ID | Requirement |
|---|---|
| FR-2.1 | `WS /ws/system-metrics` streams real CPU %, RAM MB/%, and flows/sec every 1 second |
| FR-2.2 | `notarize_to_blockchain()` computes SHA-256 of the sorted alert JSON, calls the smart contract, and returns the real `tx_hash` + `block_number` |
| FR-2.3 | Mock Ghost AI generator emits one synthetic alert every 2–4 seconds when `MOCK_MODE=True`, matching the real alert schema exactly |
| FR-2.4 | `POST /api/alerts` accepts real AI/pipeline payloads, hashes, notarizes on-chain, and broadcasts the enriched alert via `/ws/alerts` |
| FR-2.5 | `GET /api/verify/{alert_id}` queries the smart contract live and returns proof of on-chain existence |
| FR-2.6 | `GET /api/health` reports service, blockchain connection, and mock-mode status |
| FR-2.7 | Switching `MOCK_MODE` to `False` requires no code changes elsewhere in the system |

### 5.3 Phase 3 — SOC Dashboard (React + Vite + Tailwind + Recharts)

| ID | Requirement |
|---|---|
| FR-3.1 | Dark-mode, fully live-updating UI — no static placeholder values anywhere |
| FR-3.2 | Top bar shows live CPU %, RAM MB, flow ingest rate, and pipeline latency |
| FR-3.3 | Live threat feed table prepends new alerts in real time with animation, color-coded by severity (red = CRITICAL, amber = HIGH) |
| FR-3.4 | Each row displays local time, source → destination, threat class, confidence badge, and on-chain tx hash badge |
| FR-3.5 | Clicking a row expands an Evidence Drawer showing the raw, threat-specific evidence dictionary |
| FR-3.6 | A Blockchain Verifier widget accepts an `alert_id`/`flow_id`, calls the backend's verify endpoint, and displays hash, block timestamp, and a "🟢 Verified Immutable" status |

---

## 6. Data Contracts

### 6.1 Alert Schema (shared between mock and real data — must never diverge)
```json
{
  "flow_id": "FL-<uuid4hex>",
  "timestamp": "<ISO 8601 UTC>",
  "source_ip": "<IPv4>",
  "destination_ip": "<IPv4>",
  "threat_class": "DDOS | PORT_SCAN | DGA_DOMAIN | C2_BEACON | TLS_MALWARE | EXFILTRATION",
  "confidence": "<float 0.0–1.0>",
  "severity": "CRITICAL | HIGH",
  "evidence": { "...threat-specific dynamic metrics..." },
  "tx_hash": "<0x... populated after notarization>",
  "block_number": "<int, populated after notarization>"
}
```

### 6.2 System Metrics Schema
```json
{
  "cpu_percent": "<float>",
  "ram_used_mb": "<float>",
  "ram_percent": "<float>",
  "flows_per_second": "<float, rolling window>",
  "pipeline_latency_ms": "<float>"
}
```

---

## 7. Non-Functional Requirements

| Category | Requirement |
|---|---|
| Latency | Alerts must reach the dashboard within ~1 second of backend broadcast |
| Reliability | WebSocket connections must auto-reconnect on drop (frontend hook) |
| Integrity | Every alert's hash must be independently verifiable on-chain after the fact |
| Portability | Entire stack must run locally with three terminal commands (Hardhat, backend, frontend) |
| Extensibility | Mock → real data source swap must require config-only changes |

---

## 8. Milestones & Phase Gates

| Phase | Deliverable | Exit Criteria (must verify before moving on) |
|---|---|---|
| **Phase 1** | Solidity contract + Hardhat deployment | Contract deploys with a real address; `contract_info.json` written with `address` + `abi` |
| **Phase 2** | FastAPI backend with mock mode | `/api/health` shows `blockchain_ready: true`; real `tx_hash` values appear in logs every 2–4s |
| **Phase 3** | SOC Dashboard | Live-updating metrics, threat feed, evidence drawer, and successful on-chain verification via UI |
| **Phase 4** | Integration | Real AI/pipeline payload accepted via `POST /api/alerts` with `MOCK_MODE=false`, no schema errors |

---

## 9. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| web3.py fails to sign transactions (missing/misconfigured private key) | Verify Hardhat test account key is correctly loaded in backend `.env` before Phase 2 sign-off |
| Contract address/ABI mismatch between deploy script and backend | Single source of truth: `contract_info.json` read by backend at startup |
| CORS blocking frontend ↔ backend (REST + WebSocket) | Explicit CORS + WS origin allowlist for `localhost:5173` |
| Schema drift between mock and real AI/pipeline output | Freeze and document the alert schema (Section 6.1) and share with Sarbottam/Ruparna early |
| Hardhat node restart invalidates deployed contract | Re-run deploy script after every node restart; document this in run instructions |

---

## 10. Full Local Run Sequence

```powershell
# Terminal 1 — Hardhat EVM node (keep running)
cd trust_layer
npx hardhat node

# Terminal 2 — Deploy contract, then start backend
cd trust_layer
npm run deploy
cd ../dashboard_backend
uvicorn main:app --reload --port 8000

# Terminal 3 — Frontend
cd soc_frontend
npm run dev
# → http://localhost:5173
```

---

## 11. Definition of Done
- [ ] Contract deployed locally with verifiable address and ABI
- [ ] Backend generates real signed on-chain transactions for every alert (mock or real)
- [ ] Dashboard shows fully live, dynamically updating data with zero static values
- [ ] Any alert can be verified on-chain via the dashboard's Verify widget
- [ ] `MOCK_MODE=false` accepts real AI/pipeline data with no code changes
- [ ] All three services run via the documented 3-terminal sequence with no manual patching
