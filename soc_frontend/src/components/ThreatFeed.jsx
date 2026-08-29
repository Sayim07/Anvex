// ThreatFeed.jsx — Live real-time alert table
import { useState, useCallback, useRef } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import EvidenceDrawer from './EvidenceDrawer';

const MAX_ALERTS = 200;

function ThreatClassBadge({ cls }) {
  const colors = {
    DDOS:         { bg: '#7f1d1d', color: '#fca5a5', border: '#dc2626' },
    PORT_SCAN:    { bg: '#1e3a5f', color: '#93c5fd', border: '#3b82f6' },
    DGA_DOMAIN:   { bg: '#312e81', color: '#c4b5fd', border: '#7c3aed' },
    C2_BEACON:    { bg: '#4c1d95', color: '#ddd6fe', border: '#8b5cf6' },
    TLS_MALWARE:  { bg: '#1c1917', color: '#d6d3d1', border: '#78716c' },
    EXFILTRATION: { bg: '#422006', color: '#fde68a', border: '#d97706' },
  };
  const s = colors[cls] || { bg: '#1f2937', color: '#9ca3af', border: '#374151' };
  return (
    <span style={{
      background: s.bg,
      border: `1px solid ${s.border}`,
      color: s.color,
      borderRadius: '4px',
      padding: '2px 7px',
      fontSize: '0.68rem',
      fontWeight: 600,
      letterSpacing: '0.04em',
      whiteSpace: 'nowrap',
    }}>
      {cls}
    </span>
  );
}

function AlertRow({ alert, isExpanded, onToggle }) {
  const severity = alert.severity?.toUpperCase();
  const isCritical = severity === 'CRITICAL';
  const localTime = new Date(alert.timestamp).toLocaleTimeString();

  return (
    <>
      <tr
        className={`alert-row ${isCritical ? 'critical' : 'high'} animate-slide-in`}
        onClick={onToggle}
        title="Click to expand evidence"
      >
        {/* Time */}
        <td style={{ padding: '10px 12px', fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', whiteSpace: 'nowrap' }}>
          {localTime}
        </td>

        {/* Source → Dest */}
        <td style={{ padding: '10px 12px', fontSize: '0.75rem', fontFamily: 'var(--font-mono)' }}>
          <span style={{ color: '#7dd3fc' }}>{alert.source_ip}</span>
          <span style={{ color: 'var(--text-dim)', margin: '0 6px' }}>→</span>
          <span style={{ color: '#c4b5fd' }}>{alert.destination_ip}</span>
        </td>

        {/* Threat Class */}
        <td style={{ padding: '10px 12px' }}>
          <ThreatClassBadge cls={alert.threat_class} />
        </td>

        {/* Severity */}
        <td style={{ padding: '10px 12px' }}>
          <span className={isCritical ? 'badge-critical' : 'badge-high'}>
            {severity}
          </span>
        </td>

        {/* Confidence */}
        <td style={{ padding: '10px 12px' }}>
          <span className="badge-confidence">
            {(alert.confidence * 100).toFixed(2)}%
          </span>
        </td>

        {/* Tx Hash */}
        <td style={{ padding: '10px 12px' }}>
          {alert.tx_hash ? (
            <span className="badge-tx" title={alert.tx_hash}>
              ⛓ {alert.tx_hash.slice(0, 10)}…
            </span>
          ) : (
            <span style={{ color: 'var(--text-dim)', fontSize: '0.7rem' }}>pending</span>
          )}
        </td>

        {/* Expand toggle */}
        <td style={{ padding: '10px 12px', color: 'var(--text-dim)', fontSize: '0.8rem' }}>
          {isExpanded ? '▲' : '▼'}
        </td>
      </tr>

      {isExpanded && (
        <tr>
          <td colSpan={7} style={{ padding: 0 }}>
            <EvidenceDrawer alert={alert} />
          </td>
        </tr>
      )}
    </>
  );
}

export default function ThreatFeed() {
  const [alerts, setAlerts] = useState([]);
  const [expandedId, setExpandedId] = useState(null);
  const alertCountRef = useRef(0);

  const handleMessage = useCallback((data) => {
    alertCountRef.current += 1;
    setAlerts((prev) => {
      const next = [{ ...data, _key: alertCountRef.current }, ...prev];
      return next.slice(0, MAX_ALERTS);
    });
  }, []);

  const wsStatus = useWebSocket('/ws/alerts', handleMessage);

  const toggleRow = (id) => setExpandedId((prev) => (prev === id ? null : id));

  return (
    <div className="panel" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      {/* Panel header */}
      <div style={{ padding: '14px 20px', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: '10px' }}>
        <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#ef4444', boxShadow: '0 0 8px #ef4444' }} />
        <span style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--text-muted)' }}>
          Live Threat Feed
        </span>
        <span style={{
          marginLeft: '6px',
          background: 'rgba(239,68,68,0.15)',
          border: '1px solid rgba(239,68,68,0.4)',
          color: '#fca5a5',
          borderRadius: '12px',
          padding: '1px 8px',
          fontSize: '0.65rem',
          fontWeight: 600,
        }}>
          {alerts.length}
        </span>
        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span
            className={`status-dot ${wsStatus === 'connected' ? 'connected' : wsStatus === 'connecting' ? 'connecting' : 'disconnected'}`}
          />
          <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>
            {wsStatus === 'connected' ? 'Streaming' : wsStatus === 'connecting' ? 'Connecting…' : 'Offline'}
          </span>
        </div>
      </div>

      {/* Table */}
      <div style={{ overflow: 'auto', flex: 1 }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border)' }}>
              {['Time', 'Source → Destination', 'Threat', 'Severity', 'Confidence', 'On-Chain TX', ''].map((h) => (
                <th key={h} style={{
                  padding: '8px 12px',
                  fontSize: '0.6rem',
                  fontWeight: 600,
                  textTransform: 'uppercase',
                  letterSpacing: '0.08em',
                  color: 'var(--text-dim)',
                  textAlign: 'left',
                  position: 'sticky',
                  top: 0,
                  background: 'var(--bg-panel)',
                  zIndex: 1,
                }}>
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {alerts.length === 0 ? (
              <tr>
                <td colSpan={7} style={{ padding: '40px', textAlign: 'center', color: 'var(--text-dim)', fontSize: '0.85rem' }}>
                  {wsStatus === 'connected' ? 'Waiting for threat alerts…' : 'Connecting to alert stream…'}
                </td>
              </tr>
            ) : (
              alerts.map((alert) => (
                <AlertRow
                  key={alert._key}
                  alert={alert}
                  isExpanded={expandedId === alert._key}
                  onToggle={() => toggleRow(alert._key)}
                />
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
