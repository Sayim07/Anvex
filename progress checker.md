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

Status: Implemented / Complete for current available data, pending final validation with improved upstream telemetry.

Completed work:
- Feature extraction implemented (source_ip_entropy, pps, syn_ack_ratio, port_fanout, connection_failure_rate, subdomain_entropy, ngram_probability, mean_packet_size, packet_size_variance, iat_variance, fft_periodicity, outbound_inbound_ratio, volume_baseline_ratio)
- Threat detection implemented for all six required categories (DDoS, Port Scan, DGA, JA4/TLS, C2 Beacon, Exfiltration)
- ML layer implemented (XGBoost inference, anomaly detection / Isolation Forest, model loading, confidence generation)
- Explainability implemented (SHAP explanations, feature contribution output)
- Threat scoring implemented (unified threat score, severity classification)
- Alert schema implemented and validated for downstream backend integration
- Zeek integration implemented ([ai_engine/adapters/zeek_adapter.py](ai_engine/adapters/zeek_adapter.py), standardized Zeek event loading, scenario event loading, AI feature preparation)
- Scenario validation implemented ([ai_engine/tests/test_scenario_pipeline.py](ai_engine/tests/test_scenario_pipeline.py), [ai_engine/tests/validate_scenarios.py](ai_engine/tests/validate_scenarios.py))
- FP/FN analysis documented ([ai_engine/docs/fp_fn_analysis.md](ai_engine/docs/fp_fn_analysis.md))
- Upstream data requirements documented ([UPSTREAM_REQUIREMENTS.md](UPSTREAM_REQUIREMENTS.md))
- DGA missing-data false-positive issue was fixed (`detect_dga(None)` no longer incorrectly triggers)
- Regression validation: All current AI/ML regression tests pass (test_pipeline, test_normal_pipeline, test_shap, test_threat_scorer, test_alert_schema, test_inference, test_zeek_adapter, test_zeek_all_available, test_dga_detector, test_scenario_pipeline, validate_scenarios)

PRD alignment:
- Matches PRD detection engine requirements, but seven-scenario validation is currently blocked by upstream data limitations (synthetic timing, missing DNS/TLS fields, limited TCP flags/bytes). These are upstream data/integration limitations, not unfinished AI modules.

Progress estimate: 90% - 100% (final production-quality validation depends on Ruparna's improved telemetry)

Remaining work:
- pull and validate improved upstream data from Ruparna
- update the adapter only if the new upstream schema requires it
- rerun seven-scenario validation
- measure final FP/FN and detection performance
- participate in final end-to-end integration with Sayim

---

## 4. Team-wise completion estimate

| Member | Area | Completion estimate | Current status |
|---|---|---:|---|
| Sayim | Trust layer + backend + dashboard | 80% - 90% | Most complete and integration-ready |
| Ruparna | Data pipeline | 60% - 75% | Strong pipeline progress |
| Sarbottam | AI/ML detector engine | 90% - 100% | Complete for current data, pending upstream telemetry |

Overall system readiness: approximately 80% - 90%

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
- improved telemetry/data

### Sarbottam
Next priority:
- final AI validation

### Sayim
Next priority:
- backend/dashboard/blockchain integration

### Team
Next priority:
- final end-to-end localhost prototype validation

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
- Sarbottam: yes, implementation is complete for current data and awaiting improved upstream telemetry

### Who should do what next
- Ruparna: improved telemetry/data
- Sarbottam: final AI validation
- Sayim: backend/dashboard/blockchain integration


### Best next sequence
Ruparna -> Sarbottam -> Sayim

This is the most realistic and PRD-aligned execution order for the remaining project completion.
