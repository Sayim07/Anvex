// EvidenceDrawer.jsx — Expandable Evidence, Blockchain Record & SHAP Attribution with Framer Motion
import { useState, Fragment } from 'react';
import { motion } from 'framer-motion';
import {
  Copy,
  Check,
  ShieldCheck,
  BrainCircuit,
  Info,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

const EVIDENCE_EXPLANATIONS = {
  pps: 'Packets per second. Extremely high values indicate a volumetric flood overwhelming the target server.',
  syn_ack_ratio: 'Ratio of SYN packets to ACK replies. A high ratio means the server is being flooded with half-open TCP connections (SYN flood).',
  source_ip_entropy: 'Randomness in the source IPs. High entropy means the attack uses many spoofed or botnet IPs to avoid blocking.',
  dest_port_fanout: 'Number of unique destination ports probed. Hundreds of ports in seconds indicates an automated port scanner.',
  connection_failure_rate: 'Fraction of connections that were refused or dropped. Near 1.0 means the scanner is hitting closed ports rapidly.',
  scan_rate_pps: 'Scanning speed in packets per second. High values indicate an automated, aggressive scanner.',
  subdomain_entropy: 'Shannon entropy of the domain name. High entropy (>3.5) means machine-generated gibberish (DGA).',
  ngram_anomaly_score: 'Abnormal character patterns compared to legitimate language words.',
  query_frequency_hz: 'Repetitive domain querying frequency indicative of malware C2 check-in.',
  iat_variance_ms: 'Variance in inter-arrival packet time. Near zero = robotic, clock-like beaconing.',
  fft_periodicity_score: 'Fourier spectral analysis score. Close to 1.0 means periodic beacon signals.',
  beacon_interval_sec: 'Estimated duration between C2 command-and-control heartbeats.',
  ja4_fingerprint: 'JA4 TLS client fingerprint matching known offensive cyber tooling.',
  ja3_hash: 'JA3 TLS fingerprint hash correlated with threat actors.',
  splt_anomaly_score: 'Sequence Packet Length & Timing anomaly indicating encrypted malware tunnel.',
  outbound_inbound_ratio: 'Ratio of uploaded to downloaded data (>10x indicates heavy exfiltration).',
  bytes_transferred_mb: 'Megabytes transferred unexpectedly outside network perimeter.',
  baseline_deviation_sigma: 'Standard deviations away from historical behavioral baseline (>3σ is anomalous).',
};

export default function EvidenceDrawer({ alert, onVerify }) {
  const [copied, setCopied] = useState(false);
  const [showExplanations, setShowExplanations] = useState(false);

  if (!alert) return null;

  const {
    evidence = {},
    alert_hash,
    tx_hash,
    block_number,
    pipeline_latency_ms,
    alert_id,
    explanation = {},
  } = alert;

  const handleCopy = () => {
    if (alert_id) {
      navigator.clipboard.writeText(alert_id).then(() => {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      });
    }
  };

  const shapEntries = Object.entries(explanation);
  const maxShapScore = shapEntries.reduce((max, [, val]) => Math.max(max, Math.abs(val || 0)), 1);

  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: 'auto' }}
      exit={{ opacity: 0, height: 0 }}
      transition={{ duration: 0.35, ease: [0.04, 0.62, 0.23, 0.98] }}
      className="overflow-hidden bg-[#070b16] border-t border-sky-500/20 text-slate-200"
    >
      <div className="p-4 sm:p-5 space-y-4">
        {/* Prominent Alert Header Bar */}
        <div className="flex flex-wrap items-center justify-between gap-3 p-3 rounded-xl bg-sky-950/40 border border-sky-500/25">
          <div className="flex items-center gap-2.5 min-w-0">
            <span className="text-[11px] font-mono font-bold tracking-wider text-sky-400 uppercase">
              ALERT SIGNATURE:
            </span>
            <code className="text-xs font-mono text-cyan-300 truncate max-w-xs sm:max-w-md bg-slate-900/80 px-2 py-1 rounded border border-slate-700">
              {alert_id}
            </code>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              className="cyber-btn bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-slate-300 text-xs py-1.5 px-3"
              title="Copy Alert ID"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              {copied ? 'Copied' : 'Copy ID'}
            </button>

            <button
              onClick={() => onVerify && onVerify(alert_id)}
              className="cyber-btn cyber-btn-verify text-xs py-1.5 px-3"
              title="Verify on Blockchain"
            >
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              Verify On-Chain
            </button>
          </div>
        </div>

        {/* 3-Column Inspection Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* 1. Evidence Telemetry */}
          <div className="p-3.5 rounded-xl bg-slate-900/50 border border-slate-800">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-1.5 text-xs font-mono font-bold uppercase tracking-wider text-slate-400">
                <Info className="w-3.5 h-3.5 text-sky-400" />
                Evidence Parameters
              </div>
              <button
                onClick={() => setShowExplanations((prev) => !prev)}
                className="text-[10px] text-cyan-400 hover:text-cyan-300 font-mono flex items-center gap-1"
              >
                {showExplanations ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                {showExplanations ? 'Hide Guide' : 'Explain'}
              </button>
            </div>

            <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
              {Object.entries(evidence).length > 0 ? (
                Object.entries(evidence).map(([k, v]) => (
                  <Fragment key={k}>
                    <div className="flex items-center justify-between text-xs py-1 border-b border-slate-800/60 font-mono">
                      <span className="text-cyan-400 truncate pr-2">{k}</span>
                      <span className="text-slate-200 font-semibold shrink-0">
                        {typeof v === 'number' ? (v.toFixed ? v.toFixed(4) : v) : String(v)}
                      </span>
                    </div>
                    {showExplanations && EVIDENCE_EXPLANATIONS[k] && (
                      <div className="text-[10px] text-slate-400 bg-slate-950/60 p-1.5 rounded border border-slate-800 mb-1 leading-relaxed">
                        {EVIDENCE_EXPLANATIONS[k]}
                      </div>
                    )}
                  </Fragment>
                ))
              ) : (
                <div className="text-xs text-slate-500 font-mono py-2">No evidence metrics available</div>
              )}
            </div>
          </div>

          {/* 2. Blockchain Immutability Record */}
          <div className="p-3.5 rounded-xl bg-slate-900/50 border border-slate-800">
            <div className="flex items-center gap-1.5 text-xs font-mono font-bold uppercase tracking-wider text-emerald-400 mb-3">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              On-Chain Cryptography
            </div>

            <div className="space-y-2 text-xs font-mono">
              <div className="py-1 border-b border-slate-800/60">
                <div className="text-[10px] text-slate-400 uppercase">Alert SHA-256 Hash</div>
                <div className="text-emerald-300 truncate font-mono text-[11px] mt-0.5" title={alert_hash}>
                  {alert_hash || 'pending notarization'}
                </div>
              </div>

              <div className="py-1 border-b border-slate-800/60">
                <div className="text-[10px] text-slate-400 uppercase">Transaction Hash</div>
                <div className="text-slate-200 truncate font-mono text-[11px] mt-0.5" title={tx_hash}>
                  {tx_hash ? `⛓ ${tx_hash}` : 'pending mining'}
                </div>
              </div>

              <div className="flex items-center justify-between py-1 border-b border-slate-800/60">
                <span className="text-[10px] text-slate-400 uppercase">Block Height</span>
                <span className="text-slate-200 font-bold">{block_number ?? 'N/A'}</span>
              </div>

              <div className="flex items-center justify-between py-1">
                <span className="text-[10px] text-slate-400 uppercase">Pipeline Latency</span>
                <span className="text-cyan-300">{pipeline_latency_ms != null ? `${pipeline_latency_ms} ms` : 'N/A'}</span>
              </div>
            </div>
          </div>

          {/* 3. AI SHAP Feature Attribution */}
          <div className="p-3.5 rounded-xl bg-slate-900/50 border border-slate-800">
            <div className="flex items-center gap-1.5 text-xs font-mono font-bold uppercase tracking-wider text-purple-400 mb-3">
              <BrainCircuit className="w-3.5 h-3.5 text-purple-400" />
              AI Explainability (SHAP)
            </div>

            <div className="space-y-2.5 max-h-56 overflow-y-auto pr-1">
              {shapEntries.length > 0 ? (
                shapEntries.slice(0, 5).map(([feat, score]) => {
                  const numScore = typeof score === 'number' ? score : parseFloat(score) || 0;
                  const pct = Math.min(100, Math.max(10, (Math.abs(numScore) / maxShapScore) * 100));

                  return (
                    <div key={feat} className="space-y-1">
                      <div className="flex justify-between text-[11px] font-mono">
                        <span className="text-purple-300 truncate pr-2">{feat}</span>
                        <span className="text-cyan-400 font-semibold">{numScore.toFixed(4)}</span>
                      </div>
                      <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-purple-500 to-cyan-400 rounded-full"
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </div>
                  );
                })
              ) : (
                <div className="text-xs text-slate-500 font-mono py-2">
                  No SHAP features generated for this payload.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
