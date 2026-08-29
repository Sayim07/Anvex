// App.jsx — Anvex SOC Dashboard root layout
import { useState, useCallback } from 'react';
import SystemHealthBar from './components/SystemHealthBar';
import ThreatFeed from './components/ThreatFeed';
import BlockchainVerifier from './components/BlockchainVerifier';

function Header() {
  return (
    <header style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '14px 28px',
      borderBottom: '1px solid var(--border)',
      background: 'var(--bg-panel)',
      flexShrink: 0,
    }}>
      {/* Brand */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        {/* Animated shield icon */}
        <div style={{
          width: '36px',
          height: '36px',
          borderRadius: '8px',
          background: 'linear-gradient(135deg, #1d4ed8, #7c3aed)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '18px',
          boxShadow: '0 4px 16px rgba(59,130,246,0.4)',
        }}>
          🛡
        </div>
        <div>
          <div style={{ fontWeight: 800, fontSize: '1.1rem', letterSpacing: '0.04em', color: '#e2e8f0' }}>
            ANVEX
          </div>
          <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)', letterSpacing: '0.12em', textTransform: 'uppercase' }}>
            AI Cyber Threat Intelligence Platform
          </div>
        </div>
      </div>

      {/* Right: system tags */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <span style={{
          background: 'rgba(34, 197, 94, 0.12)',
          border: '1px solid rgba(34, 197, 94, 0.3)',
          color: '#4ade80',
          borderRadius: '20px',
          padding: '3px 12px',
          fontSize: '0.65rem',
          fontWeight: 600,
          letterSpacing: '0.06em',
        }}>
          ● LIVE
        </span>
        <span style={{
          background: 'rgba(124, 58, 237, 0.12)',
          border: '1px solid rgba(124, 58, 237, 0.3)',
          color: '#c4b5fd',
          borderRadius: '20px',
          padding: '3px 12px',
          fontSize: '0.65rem',
          fontWeight: 600,
          letterSpacing: '0.06em',
        }}>
          ⛓ ON-CHAIN
        </span>
        <span style={{
          background: 'rgba(59, 130, 246, 0.12)',
          border: '1px solid rgba(59, 130, 246, 0.3)',
          color: '#93c5fd',
          borderRadius: '20px',
          padding: '3px 12px',
          fontSize: '0.65rem',
          fontWeight: 600,
          letterSpacing: '0.06em',
        }}>
          SIH PS 26145
        </span>
      </div>
    </header>
  );
}

export default function App() {
  // Lifted state: lets ThreatFeed push an alert_id into BlockchainVerifier
  const [pendingVerifyId, setPendingVerifyId] = useState(null);

  const handleVerifyRequest = useCallback((alertId) => {
    // Wrap in object so the same ID can be re-sent and force re-render
    setPendingVerifyId({ id: alertId, ts: Date.now() });
  }, []);

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      background: 'var(--bg-base)',
      overflow: 'hidden',
    }}>
      <Header />

      <main style={{
        flex: 1,
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
        padding: '16px 20px',
        gap: '16px',
      }}>
        {/* System Health Bar — top strip */}
        <SystemHealthBar />

        {/* Main content: Threat Feed + Verifier side-by-side */}
        <div style={{
          flex: 1,
          display: 'flex',
          gap: '16px',
          overflow: 'hidden',
          minHeight: 0,
        }}>
          <ThreatFeed onVerifyRequest={handleVerifyRequest} />
          <BlockchainVerifier externalRequest={pendingVerifyId} />
        </div>
      </main>
    </div>
  );
}
