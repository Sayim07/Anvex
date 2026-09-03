// EvidenceDrawer.jsx — Expandable evidence JSON viewer with confidence explanations
import { useState, Fragment } from 'react';

// Plain-English explanations for each evidence field
const EVIDENCE_EXPLANATIONS = {
  // DDOS
  pps: 'Packets per second. Extremely high values indicate a volumetric flood overwhelming the target server.',
  syn_ack_ratio: 'Ratio of SYN packets to ACK replies. A high ratio means the server is being flooded with half-open TCP connections (SYN flood).',
  source_ip_entropy: 'Randomness in the source IPs. High entropy means the attack uses many spoofed or botnet IPs to avoid blocking.',

  // PORT_SCAN
  dest_port_fanout: 'Number of unique destination ports probed. Hundreds of ports in seconds = an automated port scanner mapping the target.',
  connection_failure_rate: 'Fraction of connections that were refused or dropped. Near 1.0 means the scanner is hitting closed ports rapidly.',
  scan_rate_pps: 'Scanning speed in packets per second. High values indicate an automated, aggressive scanner.',

  // DGA_DOMAIN
  subdomain_entropy: 'Shannon entropy of the domain name. High entropy (>3.5) means the domain looks like random gibberish — a hallmark of malware-generated domains.',
  ngram_anomaly_score: 'How abnormal the character patterns are compared to real English/language words. High score = machine-generated domain.',
  query_frequency_hz: 'How often the malware queries this domain. Regular, rapid querying is a sign of a Command & Control (C2) check-in.',

  // C2_BEACON
  iat_variance_ms: 'Variance in the time between network packets (inter-arrival time). Very low variance = machine-precise, clock-like beaconing.',
  fft_periodicity_score: 'Periodicity detected using Fourier analysis. A score near 1.0 means traffic repeats at a very regular interval — a beacon.',
  beacon_interval_sec: 'Estimated interval (in seconds) between C2 check-ins. Regular, predictable intervals are a strong C2 indicator.',

  // TLS_MALWARE
  ja4_fingerprint: 'JA4 TLS client fingerprint. This hash uniquely identifies the TLS library used — matched against known malware families.',
  ja3_hash: 'JA3 TLS fingerprint hash. An older but widely used method to identify the TLS client — often matches known malware toolkits.',
  splt_anomaly_score: 'Anomaly score from analyzing the sequence, payload length, and timing of TLS packets. High = unusual pattern consistent with malware.',

  // EXFILTRATION
  outbound_inbound_ratio: 'Ratio of bytes sent out vs. bytes received. Normal browsing is roughly 1:1. A ratio of 10+ means data is being uploaded/stolen.',
  bytes_transferred_mb: 'Total megabytes of data transferred. A large unexpected transfer is a key exfiltration indicator.',
  baseline_deviation_sigma: 'How many standard deviations this transfer is from the normal baseline. >3σ is statistically anomalous; >6σ is critical.',
};

export default function EvidenceDrawer({ alert, onVerify }) {
  const [copied, setCopied] = useState(false);
  const [showExplanations, setShowExplanations] = useState(false);

  if (!alert) return null;

  const { evidence = {}, alert_hash, tx_hash, block_number, pipeline_latency_ms, alert_id } = alert;

  const metaEntries = [
    ['alert_id', alert_id],
    ['alert_hash', alert_hash],
    ['tx_hash', tx_hash || 'pending / not notarized'],
    ['block_number', block_number ?? 'N/A'],
    ['pipeline_latency_ms', pipeline_latency_ms != null ? `${pipeline_latency_ms} ms` : 'N/A'],
  ];

  const handleCopy = () => {
    if (alert_id) {
      navigator.clipboard.writeText(alert_id).then(() => {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      });
    }
  };

  const handleVerify = () => {
    if (onVerify && alert_id) {
      onVerify(alert_id);
    }
  };

  return (
    <div className="evidence-drawer animate-fade-in" style={{ padding: '12px 20px 16px' }}>

      {/* Alert ID row — prominent, with action buttons */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        marginBottom: '14px',
        padding: '10px 14px',
        background: 'rgba(59,130,246,0.06)',
        border: '1px solid rgba(59,130,246,0.2)',
        borderRadius: '8px',
      }}>
        <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', whiteSpace: 'nowrap' }}>
          Alert ID
        </span>
        <code style={{ color: '#7dd3fc', fontSize: '0.8rem', flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {alert_id}
        </code>
        <button className="copy-btn" onClick={handleCopy} title="Copy alert_id to clipboard">
          {copied ? '✓ Copied' : '📋 Copy'}
        </button>
        <button className="verify-chain-btn" onClick={handleVerify} title="Send to Blockchain Verifier and auto-verify">
          ⛓ Verify On-Chain
        </button>
      </div>

      <div style={{ display: 'flex', gap: '32px', flexWrap: 'wrap' }}>
        {/* Evidence metrics */}
        <div style={{ flex: 1, minWidth: '200px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
            <div style={{ fontSize: '0.6rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              Evidence
            </div>
            <button
              className="explain-toggle-btn"
              onClick={() => setShowExplanations(v => !v)}
              title="Toggle confidence explanations"
            >
              {showExplanations ? '▲ Hide Explanations' : '💡 Why this confidence?'}
            </button>
          </div>
          <table style={{ borderCollapse: 'collapse', width: '100%' }}>
            <tbody>
              {Object.entries(evidence).map(([k, v]) => (
                <Fragment key={k}>
                  <tr>
                    <td style={{ color: '#7dd3fc', paddingRight: '16px', paddingBottom: showExplanations ? '2px' : '4px', fontSize: '0.78rem', verticalAlign: 'top' }}>
                      {k}
                    </td>
                    <td style={{ color: '#e2e8f0', paddingBottom: showExplanations ? '2px' : '4px', fontSize: '0.78rem' }}>
                      {typeof v === 'number' ? (v.toFixed ? v.toFixed(4) : v) : String(v)}
                    </td>
                  </tr>
                  {showExplanations && EVIDENCE_EXPLANATIONS[k] && (
                    <tr>
                      <td colSpan={2} style={{
                        paddingBottom: '10px',
                        paddingLeft: '2px',
                        fontSize: '0.7rem',
                        color: '#94a3b8',
                        lineHeight: 1.5,
                        borderBottom: '1px solid rgba(59,130,246,0.08)',
                      }}>
                        ℹ️ {EVIDENCE_EXPLANATIONS[k]}
                      </td>
                    </tr>
                  )}
                </Fragment>
              ))}
              {Object.keys(evidence).length === 0 && (
                <tr>
                  <td style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>No evidence data</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Blockchain metadata */}
        <div style={{ minWidth: '200px' }}>
          <div style={{ fontSize: '0.6rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '8px' }}>
            Blockchain Record
          </div>
          <table style={{ borderCollapse: 'collapse' }}>
            <tbody>
              {metaEntries.map(([k, v]) => (
                <tr key={k}>
                  <td style={{ color: '#86efac', paddingRight: '16px', paddingBottom: '4px', fontSize: '0.78rem' }}>
                    {k}
                  </td>
                  <td style={{ color: '#e2e8f0', paddingBottom: '4px', fontSize: '0.78rem', maxWidth: '280px', wordBreak: 'break-all' }}>
                    {v != null ? String(v) : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* AI SHAP Feature Attribution */}
        {alert.explanation && Object.keys(alert.explanation).length > 0 && (
          <div style={{ minWidth: '220px', flex: 1 }}>
            <div style={{ fontSize: '0.6rem', color: '#c084fc', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '8px' }}>
              🧠 AI Explainability (SHAP Values)
            </div>
            <table style={{ borderCollapse: 'collapse', width: '100%' }}>
              <tbody>
                {Object.entries(alert.explanation).slice(0, 5).map(([feat, score]) => (
                  <tr key={feat}>
                    <td style={{ color: '#e9d5ff', paddingRight: '12px', paddingBottom: '4px', fontSize: '0.75rem' }}>
                      {feat}
                    </td>
                    <td style={{ color: '#38bdf8', paddingBottom: '4px', fontSize: '0.75rem', fontWeight: 600, textAlign: 'right' }}>
                      {typeof score === 'number' ? score.toFixed(4) : score}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
