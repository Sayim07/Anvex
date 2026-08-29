# Project Progress Checker

## 1. PRD-aligned status overview

This project matches the requirements described in [PRD_Cyber_Threat_Detection.md](PRD_Cyber_Threat_Detection.md). The PRD clearly defines a three-layer system:

1. Data pipeline and traffic processing
2. AI/ML threat detection engine
3. Trust layer + SOC dashboard

The actual repo reflects that structure and shows different completion levels across the three layers.

---

## 2. Team roles and ownership

### Ruparna — Data Pipeline & Benchmark Engineer
Responsible for:
- traffic generation
- packet capture / replay flow
- Zeek metadata extraction
- event normalization
- benchmark and data quality validation

### Sarbottam — AI/ML & Threat Detection Lead
Responsible for:
- feature extraction
- threat detectors
- model-based classification
- scoring and confidence logic
- evaluating threat-specific evidence

### Sayim — Full-Stack & Web3 Developer
Responsible for:
- FastAPI backend
- blockchain notarization
- WebSocket live streaming
- SOC dashboard
- API contract compatibility with AI output

---

## 3. Progress by phase and member

### Phase 1 — Trust Layer (Hardhat + Solidity)
Owner: Sayim

Status: Implemented and largely complete

Completed work:
- Solidity smart contract added in [trust_layer/contracts/ForensicAuditLedger.sol](trust_layer/contracts/ForensicAuditLedger.sol)
- deployment script added in [trust_layer/scripts/deploy.js](trust_layer/scripts/deploy.js)
- Hardhat config and package setup added in [trust_layer/hardhat.config.js](trust_layer/hardhat.config.js) and [trust_layer/package.json](trust_layer/package.json)
- contract exposes the required write and verification functions
- event schema matches the PRD

PRD match:
- FR-1.1 to FR-1.5 are all covered by the current implementation

Progress estimate: 85% - 95%

Remaining work:
- runtime validation in a live Hardhat node
- final verification of deployment and function behavior in practice

---

### Phase 2 — Backend (FastAPI + web3.py)
Owner: Sayim

Status: Implemented and strongly advanced

Completed work:
- backend created in [dashboard_backend/main.py](dashboard_backend/main.py)
- streaming system metrics via WebSockets
- mock AI alert generator implemented
- blockchain notarization integration added
- API ingest route added
- verification endpoint added
- health endpoint added

PRD match:
- FR-2.1 through FR-2.7 are directly represented in the code

Progress estimate: 80% - 90%

Remaining work:
- verify live backend + Hardhat integration in one clean run
- ensure compatibility with real pipeline output when mock mode is disabled
- fix any runtime issues discovered under actual execution

---

### Phase 3 — SOC Dashboard (React + Vite)
Owner: Sayim

Status: Implemented and functionally aligned to PRD

Completed work:
- main app layout in [soc_frontend/src/App.jsx](soc_frontend/src/App.jsx)
- live metrics panel in [soc_frontend/src/components/SystemHealthBar.jsx](soc_frontend/src/components/SystemHealthBar.jsx)
- live threat feed in [soc_frontend/src/components/ThreatFeed.jsx](soc_frontend/src/components/ThreatFeed.jsx)
- evidence drawer in [soc_frontend/src/components/EvidenceDrawer.jsx](soc_frontend/src/components/EvidenceDrawer.jsx)
- blockchain verification widget in [soc_frontend/src/components/BlockchainVerifier.jsx](soc_frontend/src/components/BlockchainVerifier.jsx)
- WebSocket hook in [soc_frontend/src/hooks/useWebSocket.js](soc_frontend/src/hooks/useWebSocket.js)

PRD match:
- FR-3.1 through FR-3.6 are represented in the frontend code

Progress estimate: 80% - 90%

Remaining work:
- final live test against real backend stream
- verify all UI states with actual data, not only mock data

---

### Data pipeline and traffic processing
Owner: Ruparna

Status: Major progress, key pipeline files exist

Completed work:
- parser added in [pipeline/parser.py](pipeline/parser.py)
- producer added in [pipeline/producer.py](pipeline/producer.py)
- consumer added in [pipeline/consumer.py](pipeline/consumer.py)
- normalizer added in [pipeline/normalize.py](pipeline/normalize.py)
- standardized events and Zeek event data files added
- benchmark scripts added in [benchmark/benchmark.py](benchmark/benchmark.py) and [benchmark/run_pipeline.sh](benchmark/run_pipeline.sh)
- PCAP generation support added in [pcaps/create_pcap.py](pcaps/create_pcap.py)

PRD alignment:
- This matches the intended pipeline layer described in the PRD and is the strongest upstream contribution in the repo

Progress estimate: 60% - 75%

Remaining work:
- connect the pipeline output to the AI detector schema
- ensure the structured flow is directly usable by the detection engine
- validate real traffic flow end-to-end

---

### AI/ML engine
Owner: Sarbottam

Status: In progress, but still behind the other two areas

Completed work:
- DDoS feature extraction implemented in [ai_engine/features/ddos_features.py](ai_engine/features/ddos_features.py)
- DDoS detector implemented in [ai_engine/detectors/ddos_detector.py](ai_engine/detectors/ddos_detector.py)
- initial tests added in [ai_engine/tests/test_ddos_detector.py](ai_engine/tests/test_ddos_detector.py) and [ai_engine/tests/test_ddos_features.py](ai_engine/tests/test_ddos_features.py)

PRD alignment:
- The PRD expects a broader detection engine beyond DDoS, so this is still partial completion

Progress estimate: 25% - 35%

Remaining work:
- implement the remaining threat categories
- integrate feature extraction for all six classes
- connect outputs to the exact alert schema defined in the PRD
- validate with real or realistic pipeline data

---

## 4. Team-wise completion estimate

| Member | Area | Completion estimate | Current status |
|---|---|---:|---|
| Sayim | Trust layer + backend + dashboard | 80% - 90% | Most complete and integration-ready |
| Ruparna | Data pipeline | 60% - 75% | Strong pipeline progress |
| Sarbottam | AI/ML detector engine | 25% - 35% | Early but real implementation |

Overall system readiness: approximately 55% - 65%

This is not final completion, because the system still needs live integration between all three layers.

---

## 5. Dependency order for the next milestone

The PRD makes the dependency clearly visible:

1. Ruparna must finalize the real data flow
   - traffic -> normalized events -> AI-ready schema
2. Sarbottam must turn that into real threat detection
   - detector outputs aligned to the PRD alert schema
3. Sayim must finalize integration and validation
   - backend ingest + blockchain + dashboard live flow

This ordering is important because the backend and dashboard are designed to accept the AI output format and should not be blocked by incomplete data sources.

---

## 6. What should happen next

### Ruparna
Next priority:
- ensure pipeline outputs are consistent and use-ready for the AI layer
- validate real event structure against the PRD schema
- finish the pipeline-to-AI compatibility layer

### Sarbottam
Next priority:
- move beyond DDoS baseline
- implement all remaining detection categories
- align outputs to the expected backend schema

### Sayim
Next priority:
- verify the deployed contract, backend, and dashboard together in one working flow
- confirm the mock-first architecture remains compatible with the real AI schema
- be ready to accept real AI alerts without code refactor

---

## 7. Current project conclusion

The repo and the PRD line up well:

- Sayim has the most complete layer and is effectively the integration lead
- Ruparna has built the strongest upstream data-processing foundation
- Sarbottam has started the detection engine but is still behind the target PRD scope

The project is not finished yet, but the work is well organized and the next milestone is clear:

Real data pipeline output should feed the AI detection engine, whose threat alerts should then be consumed by Sayim's backend and displayed in the blockchain-backed SOC dashboard.

---

## 8. Final action summary

### Who is ready now
- Sayim: yes, for integration and runtime validation
- Ruparna: yes, for final pipeline stabilization
- Sarbottam: not yet for full integration, but the DDoS work is real progress

### Who should do what next
- Ruparna: finish data flow quality and AI-ready format
- Sarbottam: expand from DDoS to the full threat model set
- Sayim: finish end-to-end validation and wiring

### Best next sequence
Ruparna -> Sarbottam -> Sayim

This is the most realistic and PRD-aligned execution order for the remaining project completion.
