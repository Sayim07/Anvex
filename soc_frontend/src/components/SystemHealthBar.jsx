// SystemHealthBar.jsx — Real-time hardware + throughput metrics
import { useState, useCallback } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

function StatusDot({ status }) {
  return (
    <span
      className={`status-dot ${status === 'connected' ? 'connected' : status === 'connecting' ? 'connecting' : 'disconnected'}`}
    />
  );
}

function ProgressBar({ value, max = 100, danger = false }) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100));
  return (
    <div className="progress-bar-track" style={{ marginTop: '6px' }}>
      <div
        className={`progress-bar-fill ${pct > 80 ? 'danger' : ''}`}
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}

function GaugeTile({ value, label, unit = '', max, showBar = false, highlight = false }) {
  return (
    <div className="gauge-tile" style={{ borderColor: highlight ? 'var(--critical)' : undefined }}>
      <div className="gauge-value" style={{ color: highlight ? 'var(--critical)' : undefined }}>
        {value != null ? `${value}${unit}` : '—'}
      </div>
      <div className="gauge-label">{label}</div>
      {showBar && <ProgressBar value={value ?? 0} max={max} />}
    </div>
  );
}

export default function SystemHealthBar() {
  const [metrics, setMetrics] = useState(null);

  const handleMessage = useCallback((data) => {
    setMetrics(data);
  }, []);

  const wsStatus = useWebSocket('/ws/system-metrics', handleMessage);

  const cpuHigh = metrics?.cpu_percent > 80;

  return (
    <div
      className="panel"
      style={{ padding: '16px 24px', marginBottom: '16px' }}
    >
      {/* Header row */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '14px' }}>
        <div
          style={{
            width: '8px', height: '8px', borderRadius: '50%',
            background: 'var(--accent)', boxShadow: '0 0 8px var(--accent)',
          }}
        />
        <span style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--text-muted)' }}>
          System Health
        </span>
        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <StatusDot status={wsStatus} />
          <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>
            {wsStatus === 'connected' ? 'Live' : wsStatus === 'connecting' ? 'Connecting…' : 'Disconnected'}
          </span>
          {metrics?.ts && (
            <span style={{ fontSize: '0.6rem', color: 'var(--text-dim)', marginLeft: '8px' }}>
              {new Date(metrics.ts).toLocaleTimeString()}
            </span>
          )}
        </div>
      </div>

      {/* Gauge tiles */}
      <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
        <GaugeTile
          value={metrics?.cpu_percent}
          label="CPU Utilization"
          unit="%"
          max={100}
          showBar
          highlight={cpuHigh}
        />
        <GaugeTile
          value={metrics?.ram_used_mb != null ? Math.round(metrics.ram_used_mb) : null}
          label="RAM Used"
          unit=" MB"
        />
        <GaugeTile
          value={metrics?.ram_percent}
          label="RAM Utilization"
          unit="%"
          max={100}
          showBar
        />
        <GaugeTile
          value={metrics?.flows_per_sec}
          label="Flow Ingest Rate"
          unit=" f/s"
        />
        <GaugeTile
          value={metrics?.avg_latency_ms != null ? metrics.avg_latency_ms.toFixed(0) : null}
          label="Pipeline Latency"
          unit=" ms"
        />
      </div>
    </div>
  );
}
