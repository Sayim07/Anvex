# ANVEX — Upstream Data Requirements for AI Integration

**For:** Ruparna (Data Pipeline / Traffic Processing)
**From:** Sarbottam (AI/ML)
**Date:** 2026-08-29
**Priority:** Required before full AI validation is possible

---

## Context

The AI engine is complete. All six detectors, XGBoost, Isolation Forest, SHAP,
threat scoring, and alert generation are implemented and working.

Running the pipeline against the current scenario output (`pipeline/scenario_output/`)
shows that **3 of 7 scenarios are correctly classified**. The 4 misclassifications
are entirely caused by missing or degenerate upstream data — not AI model bugs.

This document specifies exactly what changes are needed in the pipeline output
to unblock the remaining 4 scenarios.

---

## Status Summary

| Scenario | AI Detection | Status | Blocking Issue |
|----------|-------------|--------|---------------|
| `ddos` | ✅ CORRECT | Working | — |
| `port_scan` | ✅ CORRECT | Working | — |
| `c2_beacon` | ✅ CORRECT | Working (low confidence) | Byte data missing |
| `normal` | ❌ FALSE POSITIVE | Blocked | Compressed synthetic timing |
| `dga` | ❌ MISSED | Blocked | No dns.log query field |
| `ja4_malware` | ❌ MISSED | Blocked | No ssl.log JA3/JA4 field |
| `exfiltration` | ❌ MISSED | Blocked | Zero byte counts |

---

## Currently Implemented (AI side — no changes needed)

The following are fully implemented in the AI engine and ready to consume data
as soon as it becomes available:

| Feature | AI Module | Status |
|---------|-----------|--------|
| `source_ip_entropy` | `ddos_features.py` | ✅ Implemented |
| `pps` | `ddos_features.py` | ✅ Implemented |
| `syn_ack_ratio` | `ddos_features.py` | ✅ Implemented (history proxy) |
| `port_fanout` | `scan_features.py` | ✅ Implemented |
| `connection_failure_rate` | `scan_features.py` | ✅ Implemented |
| `subdomain_entropy` | `dga_features.py` | ✅ Implemented — awaiting DNS field |
| `ngram_probability` | `dga_features.py` | ✅ Implemented — awaiting DNS field |
| `mean_packet_size` | `ja4_features.py` | ✅ Implemented — awaiting byte data |
| `packet_size_variance` | `ja4_features.py` | ✅ Implemented — awaiting byte data |
| `iat_variance` | `c2_features.py` | ✅ Implemented |
| `fft_periodicity` | `c2_features.py` | ✅ Implemented |
| `outbound_inbound_ratio` | `exfil_features.py` | ✅ Implemented — awaiting byte data |
| `volume_baseline_ratio` | `exfil_features.py` | ✅ Implemented — awaiting baseline |
| DGA adapter stub | `zeek_adapter.py` | ✅ Ready — reads `query`/`subdomain` if present |
| JA4 adapter stub | `zeek_adapter.py` | ✅ Ready — reads `ja3`/`ja4` if present |

---

## Currently Unavailable (Upstream Changes Required)

### REQ-1: DGA — Zeek dns.log Events with Query Field

**Blocking:** `subdomain_entropy`, `ngram_probability` → both 0.0 → DGA undetectable

**What is needed:**
The `dga` scenario events must include Zeek `dns.log` records in the standardised
output. The minimum required fields are:

```json
{
  "source": "zeek",
  "event_type": "dns",
  "label": "dga",
  "timestamp": 1788000143.680094,
  "uid": "<uid>",
  "src_ip": "192.168.1.10",
  "dst_ip": "8.8.8.8",
  "query": "xkj29fmnaqbvzlpt.evil.com",
  "subdomain": "xkj29fmnaqbvzlpt",
  "qtype_name": "A",
  "rcode_name": "NXDOMAIN"
}
```

**Key fields:**
- `event_type`: must be `"dns"` (so the adapter can filter by type)
- `query`: full DNS query string (e.g. `"xkj29fmnaqbvzlpt.evil.com"`)
- `subdomain`: the left-most label(s) before the registered domain
  (e.g. `"xkj29fmnaqbvzlpt"` — the algorithmically generated part)

**Why subdomain matters:**
DGA detection works on the *generated* portion of the domain, not the full query.
For `"xkj29fmnaqbvzlpt.evil.com"`, the DGA part is `"xkj29fmnaqbvzlpt"`.
Shannon entropy of random-looking strings like this is 3.8+, which crosses the
detection threshold. Entropy of the full query would be diluted by the TLD.

**Realistic DGA query characteristics:**
- Length: 12–22 characters
- Character distribution: nearly uniform over [a-z0-9]
- Entropy: > 3.5 bits/char
- Bigram probability: < 0.08 (uncommon character pairs)
- Response: usually NXDOMAIN (domain not registered) or to a sinkhole IP

**Recommended event count:** minimum 20 DNS events per scenario file.

**How to generate:**
Zeek automatically generates `dns.log` when processing PCAPs containing DNS traffic.
Ensure the DGA PCAP uses realistic DGA-generated domain names as query strings.
Run the existing Zeek processing pipeline on the DGA PCAP and include the
normalised dns.log output alongside the conn.log output.

---

### REQ-2: JA4/TLS — Zeek ssl.log Events with JA3 and JA4 Fingerprints

**Blocking:** `ja3`, `ja4` → None → JA4 detector cannot fingerprint → falls back
to packet size proxy which is also 0.0 (zero byte counts in scenario)

**What is needed:**
The `ja4_malware` scenario events must include Zeek `ssl.log` records in the
standardised output. The minimum required fields are:

```json
{
  "source": "zeek",
  "event_type": "ssl",
  "label": "ja4_malware",
  "timestamp": 1788000143.694765,
  "uid": "<uid>",
  "src_ip": "192.168.1.10",
  "src_port": 45002,
  "dst_ip": "192.168.1.20",
  "dst_port": 443,
  "ja3": "e7d705a3286e19ea42f587b344ee6865",
  "ja4": "t13d191000_9dc949149365_97f8aa674fd9",
  "orig_bytes": 8192,
  "resp_bytes": 2048,
  "conn_state": "SF"
}
```

**Key fields:**
- `event_type`: must be `"ssl"` (so the adapter can filter by type)
- `ja3`: MD5 hash of the TLS ClientHello fingerprint (32-char hex string)
- `ja4`: JA4 fingerprint string (format: `t<version>d<ciphers>_<extensions>_<sig_algs>`)
- `orig_bytes`: **non-zero** — TLS handshake + application data sent by client
- `resp_bytes`: **non-zero** — TLS handshake + application data sent by server

**Why JA3/JA4 matters:**
Real TLS malware fingerprinting works by matching client hello characteristics
(TLS version, cipher suite order, extensions, elliptic curves) to known-malicious
toolkits (e.g. Cobalt Strike, Metasploit, custom RATs). The `ja4` string encodes
these characteristics in a stable, comparable form.

**Recommended malicious JA3 examples for scenario:**
Zeek will generate these automatically from the TLS ClientHello in the PCAP.
The PCAP should simulate a malware tool's TLS handshake (non-standard cipher
order, uncommon extensions, self-signed or no SNI).

**Recommended event count:** minimum 20 SSL events per scenario file.

**How to generate:**
Zeek automatically generates `ssl.log` when processing PCAPs containing TLS traffic.
Run the existing Zeek processing pipeline on the JA4 PCAP and include the
normalised ssl.log output alongside the conn.log output.
Enable the Zeek JA3 package if not already active: `zkg install zeek/salesforce/ja3`

---

### REQ-3: Exfiltration — Non-Zero Byte Counts from Realistic Payload Traffic

**Blocking:** `outbound_inbound_ratio` = 0.0 → exfil detector score = 0.0 → not detected

**Current state:**
All 20 exfiltration scenario events have:
```
orig_bytes = 0
resp_bytes = 0
conn_state = OTH   (partial connection — no FIN/RST)
history    = D     (data seen but not quantified)
```

This means the PCAP captures **connection establishment or partial traffic** but
Zeek is not recording the application data payload bytes.

**What is needed:**
Exfiltration events must carry actual byte counts reflecting outbound data transfer:

```json
{
  "source": "zeek",
  "event_type": "connection",
  "label": "exfiltration",
  "orig_bytes": 524288,
  "resp_bytes": 1024,
  "conn_state": "SF",
  "history": "ShADdFf"
}
```

**Target ratios for exfiltration to trigger detection:**
- `orig_bytes / resp_bytes >= 5` (outbound >> inbound)
- Absolute `orig_bytes` should be large (e.g. 500 KB–50 MB per connection)
  to also trigger the volume baseline threshold

**Typical exfiltration patterns:**
- Large HTTP POST, FTP PUT, or DNS query payloads (DNS tunnelling)
- Asymmetric: high outbound, low inbound (query/ack pattern)
- Example: `orig_bytes = 500000`, `resp_bytes = 512`

**How to fix:**
1. Check that the exfil PCAP actually contains application layer payload data
   (not just TCP SYN/SYN-ACK without data segments)
2. Verify Zeek's `conn_size_limit` is not truncating byte counts
   (default limit: 1,000,000 bytes — increase if needed)
3. After regeneration, `conn_state` should be `SF` (fully established and closed)

---

### REQ-4: Exfiltration — Historical Volume Baseline

**Note:** This is an **architectural limitation**, not a simple pipeline fix.

**Current state:**
The adapter currently uses:
```python
baseline_volume = current_volume   # → ratio always 1.0
```

**What is needed for production-quality exfil baselining:**
A sliding-window baseline computed from historical traffic:
- Compute average outbound byte volume over a rolling window (e.g. 24 hours)
- Store as a baseline value accessible to the adapter
- The ratio `current_session_volume / baseline_volume` then detects spikes

**Recommended approach (Phase 2 work):**
1. Add a `baseline_volume` field to the standardised event format, computed
   by the pipeline from historical traffic statistics
2. Alternatively, pass a separate `baseline.json` file alongside scenario output
   containing per-source-IP baseline statistics

**This is not blocking for the current scenario test** — once REQ-3 is resolved
(non-zero bytes), the `outbound_inbound_ratio` alone is sufficient for detection.
The baseline ratio adds a second detection dimension.

---

### REQ-5: Normal Traffic — Realistic Inter-Request Timing

**Blocking:** `iat_variance ≈ 0` → C2 false positive on normal traffic

**Current state:**
The 20 normal scenario events span approximately **0.014 seconds** of real time.
This produces `iat_variance ≈ 0`, which triggers the C2 beaconing detector.

**What is needed:**
Normal HTTP/HTTPS traffic with realistic human-paced timing:

| Traffic pattern | Typical inter-request interval |
|----------------|-------------------------------|
| Web browsing | 0.5–5.0 seconds |
| Background app updates | 30–300 seconds |
| Mixed normal traffic | 0.1–60 seconds |
| IAT variance (normal) | 1.0–20.0 (model training range) |

**What to change:**
Regenerate the normal PCAP with events spread over at least **60 seconds**, with
random inter-request delays drawn from a realistic distribution (e.g. exponential
with mean ~2 seconds). This ensures `iat_variance` falls in the [1.0, 20.0]
training range and does not trigger the C2 false positive.

**Additionally:**
- Ensure `pps` stays below 500 (current synthetic value is ~7,000)
- Ensure at least 2–3 different source IPs are present (for non-zero entropy)
- Ensure connections complete (`conn_state=SF`) so `connection_failure_rate` stays low

---

### REQ-6: SYN/ACK TCP Flag Counts (Lower Priority)

**Current workaround:** The adapter uses the Zeek `history` field as a proxy.
- `'S'` in history → 1 SYN counted
- `'A'` / `'a'` in history → 1 ACK counted

**Limitation:** History is a *set*, not a count. `'S'` means "at least one SYN
was observed", not that exactly N SYNs were sent. For the DDoS scenario with
300 events each having `history='S'`, the proxy gives 300 SYNs and 0 ACKs —
which is coincidentally correct (SYN flood). But it is not exact packet-count data.

**Long-term fix:** If Zeek is run with the `weird.log` or custom script to record
per-packet flag counts, this can be added to the standardised event schema as:
```json
{ "syn_count": 300, "ack_count": 0, "rst_count": 0 }
```

**Priority:** Low — the history proxy is adequate for current DDoS detection.

---

## What Changes in the Pipeline

The minimum changes required are:

| Change | Files Affected | Scenarios Unblocked |
|--------|---------------|-------------------|
| Add `dns.log` events with `query`+`subdomain` | `dga.json`, `all_standardized_events.json` | dga |
| Add `ssl.log` events with `ja3`+`ja4`+bytes | `ja4_malware.json`, `all_standardized_events.json` | ja4_malware |
| Fix exfil PCAP to include payload bytes | `exfiltration.json`, `all_standardized_events.json` | exfiltration |
| Regenerate normal PCAP with realistic timing | `normal.json`, `all_standardized_events.json` | normal (FP fix) |

**No changes** are needed to:
- `ddos.json` (working correctly)
- `port_scan.json` (working correctly)
- `c2_beacon.json` (working — timing data is sufficient; byte data would
  increase confidence but is not blocking)

---

## What the AI Side Will Do When Data Is Available

When the above fields are present in the pipeline output, the AI adapter
(`ai_engine/adapters/zeek_adapter.py`) will **automatically use them**:

- `query`/`subdomain` fields → `prepare_dga_inputs()` picks them up without
  any code change (the stub is already implemented and checks for these fields)
- `ja3`/`ja4` fields → `prepare_ja4_inputs()` picks them up without any code
  change (the stub is already implemented and checks for these fields)
- `orig_bytes`/`resp_bytes` → already used by `prepare_exfil_inputs()` and
  `_approximate_packet_sizes()`

**No further AI code changes are required on Sarbottam's side** once the pipeline
data is enriched. The adapter stubs are forward-compatible.

---

## Verification After Changes

After Ruparna makes these changes, Sarbottam will re-run:

```powershell
# Seven-scenario pipeline test
.\.venv\Scripts\python.exe -m ai_engine.tests.test_scenario_pipeline

# Model validation + FP/FN report
.\.venv\Scripts\python.exe -m ai_engine.tests.validate_scenarios
```

Expected improvement after all four changes:
- `normal` → correct (threat_type=normal, no false positive)
- `dga` → correct (subdomain_entropy and ngram_probability populated)
- `ja4_malware` → correct (ja4 fingerprint + packet size features)
- `exfiltration` → correct (outbound_inbound_ratio >= 5)
- `c2_beacon` → higher confidence (byte data reduces ambiguity)

Target accuracy after data enrichment: **6/7 or 7/7** (the only remaining
uncertainty is whether the C2 scenario has sufficient byte variance to
disambiguate from other scenarios at the XGBoost confidence level).
