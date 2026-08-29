// BlockchainVerifier.jsx — On-chain alert verification widget
import { useState, useEffect, useRef } from 'react';

function VerifiedResult({ data }) {
  const blockDate = data.block_datetime
    ? new Date(data.block_datetime).toLocaleString()
    : null;

  return (
    <div className="animate-fade-in" style={{
      background: 'rgba(34, 197, 94, 0.06)',
      border: '1px solid rgba(34, 197, 94, 0.35)',
      borderRadius: '8px',
      padding: '16px',
      marginTop: '14px',
    }}>
      {/* Status header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
        <span style={{ fontSize: '1.1rem' }}>🟢</span>
        <span style={{ color: '#22c55e', fontWeight: 700, fontSize: '0.95rem' }}>
          Verified Immutable
        </span>
      </div>

      {/* Fields */}
      <table style={{ borderCollapse: 'collapse', width: '100%' }}>
        <tbody>
          {[
            ['Alert ID', data.alert_id],
            ['Threat Class', data.threat_class],
            ['Confidence', `${(data.confidence * 100).toFixed(2)}%`],
            ['Alert Hash', data.alert_hash],
            ['Block Timestamp', blockDate ?? String(data.block_timestamp)],
          ].map(([label, value]) => (
            <tr key={label} style={{ borderBottom: '1px solid rgba(34, 197, 94, 0.10)' }}>
              <td style={{
                padding: '7px 0',
                fontSize: '0.7rem',
                color: '#4ade80',
                fontWeight: 600,
                textTransform: 'uppercase',
                letterSpacing: '0.06em',
                width: '140px',
                verticalAlign: 'top',
              }}>
                {label}
              </td>
              <td style={{
                padding: '7px 0',
                fontSize: '0.78rem',
                color: '#e2e8f0',
                fontFamily: 'var(--font-mono)',
                wordBreak: 'break-all',
              }}>
                {value}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ErrorResult({ message }) {
  return (
    <div className="animate-fade-in" style={{
      background: 'rgba(239, 68, 68, 0.06)',
      border: '1px solid rgba(239, 68, 68, 0.35)',
      borderRadius: '8px',
      padding: '14px 16px',
      marginTop: '14px',
    }}>
      <span style={{ fontSize: '1rem', marginRight: '8px' }}>🔴</span>
      <span style={{ color: '#fca5a5', fontSize: '0.85rem' }}>{message}</span>
    </div>
  );
}

export default function BlockchainVerifier({ externalRequest }) {
  const [alertId, setAlertId] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const panelRef = useRef(null);

  // Auto-populate and verify when an external request comes in (from ThreatFeed rows)
  useEffect(() => {
    if (externalRequest?.id) {
      setAlertId(externalRequest.id);
      setResult(null);
      setError(null);
      // Scroll the verifier panel into view
      panelRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      // Auto-trigger verification after a short delay to allow state to settle
      const timer = setTimeout(() => {
        _verify(externalRequest.id);
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [externalRequest]);

  const _verify = async (id) => {
    const trimmed = (id ?? alertId).trim();
    if (!trimmed) return;

    setLoading(true);
    setResult(null);
    setError(null);

    try {
      const res = await fetch(`/api/verify/${encodeURIComponent(trimmed)}`);
      if (res.ok) {
        const data = await res.json();
        setResult(data);
      } else if (res.status === 404) {
        setError(`Alert "${trimmed}" not found on-chain. It may not have been notarized yet.`);
      } else if (res.status === 503) {
        setError('Blockchain node unavailable. Ensure Hardhat node is running.');
      } else {
        const detail = await res.json().catch(() => ({ detail: 'Unknown error' }));
        setError(detail.detail || 'Verification failed.');
      }
    } catch {
      setError('Network error — cannot reach the backend.');
    } finally {
      setLoading(false);
    }
  };

  const verify = () => _verify(alertId);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') verify();
  };

  return (
    <div ref={panelRef} className="panel" style={{ padding: '18px 20px', minWidth: '320px', maxWidth: '440px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
        <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#22c55e', boxShadow: '0 0 8px #22c55e' }} />
        <span style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--text-muted)' }}>
          Blockchain Verifier
        </span>
      </div>

      <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '14px', lineHeight: 1.5 }}>
        Paste any <code style={{ color: '#7dd3fc', fontSize: '0.72rem' }}>alert_id</code> or{' '}
        <code style={{ color: '#7dd3fc', fontSize: '0.72rem' }}>flow_id</code> to verify its
        cryptographic record on the local blockchain.
      </p>

      {/* Input + button */}
      <div style={{ display: 'flex', gap: '8px' }}>
        <input
          className="verifier-input"
          type="text"
          placeholder="FL-a1b2c3d4e5f6…"
          value={alertId}
          onChange={(e) => setAlertId(e.target.value)}
          onKeyDown={handleKeyDown}
          spellCheck={false}
        />
        <button
          className="verifier-btn"
          onClick={verify}
          disabled={loading || !alertId.trim()}
        >
          {loading ? (
            <span className="animate-spin-slow" style={{ display: 'inline-block' }}>⟳</span>
          ) : 'Verify'}
        </button>
      </div>

      {/* Result / error */}
      {result && <VerifiedResult data={result} />}
      {error && <ErrorResult message={error} />}
    </div>
  );
}
