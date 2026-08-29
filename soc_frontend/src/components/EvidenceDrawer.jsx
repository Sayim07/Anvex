// EvidenceDrawer.jsx — Expandable evidence JSON viewer
export default function EvidenceDrawer({ alert }) {
  if (!alert) return null;

  const { evidence = {}, alert_hash, tx_hash, block_number, pipeline_latency_ms } = alert;

  const metaEntries = [
    ['alert_hash', alert_hash],
    ['tx_hash', tx_hash || 'pending / not notarized'],
    ['block_number', block_number ?? 'N/A'],
    ['pipeline_latency_ms', pipeline_latency_ms != null ? `${pipeline_latency_ms} ms` : 'N/A'],
  ];

  return (
    <div className="evidence-drawer animate-fade-in" style={{ padding: '12px 20px 16px' }}>
      <div style={{ display: 'flex', gap: '32px', flexWrap: 'wrap' }}>
        {/* Evidence metrics */}
        <div>
          <div style={{ fontSize: '0.6rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '8px' }}>
            Evidence
          </div>
          <table style={{ borderCollapse: 'collapse' }}>
            <tbody>
              {Object.entries(evidence).map(([k, v]) => (
                <tr key={k}>
                  <td style={{ color: '#7dd3fc', paddingRight: '16px', paddingBottom: '4px', fontSize: '0.78rem' }}>
                    {k}
                  </td>
                  <td style={{ color: '#e2e8f0', paddingBottom: '4px', fontSize: '0.78rem' }}>
                    {typeof v === 'number' ? v.toFixed ? v.toFixed(4) : v : String(v)}
                  </td>
                </tr>
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
        <div>
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
      </div>
    </div>
  );
}
