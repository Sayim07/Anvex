import { useState, useEffect, useRef, useCallback } from 'react';
import confetti from 'canvas-confetti';
import { Terminal, AlertTriangle, Search, CornerDownLeft } from 'lucide-react';

function AnimatedCheckmark() {
  return (
    <div className="relative flex items-center justify-center w-12 h-12 rounded-full bg-emerald-500/20 border border-emerald-500/40 shadow-[0_0_20px_rgba(16,185,129,0.3)]">
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" className="text-emerald-400">
        <path
          d="M5 13l4 4L19 7"
          stroke="currentColor"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
          style={{
            strokeDasharray: 30,
            strokeDashoffset: 0,
            animation: 'dash 0.6s ease-in-out forwards',
          }}
        />
      </svg>
    </div>
  );
}

function TerminalVerifiedResult({ data }) {
  const blockDate = data.block_datetime
    ? new Date(data.block_datetime).toLocaleString()
    : null;

  return (
    <div className="mt-4 p-4 rounded-xl bg-emerald-950/20 border border-emerald-500/40 shadow-[0_0_25px_rgba(16,185,129,0.15)] relative overflow-hidden animate-fade-in">
      {/* Top verified bar */}
      <div className="flex items-center gap-3 mb-4 pb-3 border-b border-emerald-500/20">
        <AnimatedCheckmark />
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono font-bold text-emerald-400 uppercase tracking-wider">
              CRYPTOGRAPHICALLY VERIFIED
            </span>
            <span className="text-[10px] font-mono bg-emerald-500/20 text-emerald-300 px-1.5 py-0.5 rounded border border-emerald-500/30">
              IMMUTABLE
            </span>
          </div>
          <div className="text-[11px] font-mono text-slate-400 mt-0.5">
            Verified against Smart Contract on local Hardhat EVM
          </div>
        </div>
      </div>

      {/* Terminal Receipt Table */}
      <div className="space-y-2 font-mono text-xs">
        {[
          ['ALERT ID', data.alert_id],
          ['THREAT CLASS', data.threat_class],
          ['CONFIDENCE', `${(data.confidence * 100).toFixed(2)}%`],
          ['ALERT HASH', data.alert_hash],
          ...(data.tx_hash ? [['TRANSACTION HASH', data.tx_hash]] : []),
          ['BLOCK TIME', blockDate ?? String(data.block_timestamp)],
        ].map(([label, value]) => (
          <div key={label} className="flex flex-col sm:flex-row sm:items-baseline justify-between py-1 border-b border-emerald-500/10">
            <span className="text-[10px] text-emerald-400/80 uppercase font-semibold shrink-0 w-28">
              {label}
            </span>
            <span className="text-slate-200 text-[11px] break-all text-left sm:text-right font-mono">
              {value}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

function TerminalErrorResult({ message }) {
  return (
    <div className="mt-4 p-4 rounded-xl bg-rose-950/20 border border-rose-500/40 shadow-[0_0_20px_rgba(239,68,68,0.15)] animate-fade-in">
      <div className="flex items-center gap-2.5 text-rose-400 mb-1">
        <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
        <span className="text-xs font-mono font-bold uppercase tracking-wider">
          VERIFICATION FAILURE
        </span>
      </div>
      <div className="text-xs font-mono text-slate-300 pl-6 leading-relaxed">
        {message}
      </div>
    </div>
  );
}

export default function BlockchainVerifier({ externalRequest }) {
  const [alertId, setAlertId] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const panelRef = useRef(null);

  const _verify = useCallback(async (id) => {
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
        confetti({
          particleCount: 40,
          spread: 60,
          origin: { y: 0.8 },
          colors: ['#00f0ff', '#10b981', '#38bdf8', '#c084fc'],
        });
      } else if (res.status === 404) {
        setError(`Alert "${trimmed}" not found on-chain. It may still be in the pipeline buffer or not yet mined.`);
      } else if (res.status === 503) {
        setError('Trust Layer EVM node is offline. Please ensure Hardhat node is running.');
      } else {
        const detail = await res.json().catch(() => ({ detail: 'Verification execution failed.' }));
        setError(detail.detail || 'Verification failed.');
      }
    } catch {
      setError('Network error — unable to establish connection with verification endpoint.');
    } finally {
      setLoading(false);
    }
  }, [alertId]);

  // Auto-populate and verify when an external request comes in (from ThreatFeed rows)
  useEffect(() => {
    if (externalRequest?.id) {
      setAlertId(externalRequest.id);
      panelRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      _verify(externalRequest.id);
    }
  }, [externalRequest, _verify]);

  const verify = () => _verify(alertId);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') verify();
  };

  return (
    <div
      ref={panelRef}
      className="cyber-terminal cyber-scanlines rounded-xl p-5 border border-sky-500/30 flex flex-col justify-between w-full lg:w-96 shrink-0"
    >
      <div>
        {/* Terminal Header */}
        <div className="flex items-center justify-between pb-3 mb-4 border-b border-sky-500/20">
          <div className="flex items-center gap-2.5">
            <Terminal className="w-4 h-4 text-cyan-400" />
            <span className="text-xs font-mono font-bold tracking-wider text-slate-100 uppercase">
              CRYPTOGRAPHIC TERMINAL
            </span>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_#10b981] animate-pulse" />
            <span className="text-[10px] font-mono text-emerald-400 font-semibold">ON-CHAIN</span>
          </div>
        </div>

        {/* Prompt description */}
        <p className="text-xs font-mono text-slate-400 mb-4 leading-relaxed">
          <span className="text-cyan-400">&gt;</span> Query the local EVM smart contract to verify mathematical tamper-resistance for any threat record:
        </p>

        {/* Input Bar */}
        <div className="relative flex items-center gap-2">
          <div className="relative flex-1">
            <input
              type="text"
              placeholder="Paste alert_id (e.g. FL-9a2c...)"
              value={alertId}
              onChange={(e) => setAlertId(e.target.value)}
              onKeyDown={handleKeyDown}
              spellCheck={false}
              className="cyber-input font-mono text-xs pl-8 pr-3 py-2.5 bg-slate-950/80 border-sky-500/30 focus:border-cyan-400"
            />
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-1/2 -translate-y-1/2" />
          </div>

          <button
            onClick={verify}
            disabled={loading || !alertId.trim()}
            className="cyber-btn cyber-btn-primary px-4 py-2.5 text-xs font-mono disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
          >
            {loading ? (
              <span className="animate-spin text-sm">⟳</span>
            ) : (
              <>
                <span>VERIFY</span>
                <CornerDownLeft className="w-3.5 h-3.5" />
              </>
            )}
          </button>
        </div>

        {/* Terminal Output */}
        {result && <TerminalVerifiedResult data={result} />}
        {error && <TerminalErrorResult message={error} />}
      </div>

      {/* Terminal Footer Telemetry */}
      <div className="mt-5 pt-3 border-t border-sky-500/15 flex items-center justify-between text-[10px] font-mono text-slate-500">
        <span>CONTRACT: CyberThreatRegistry.sol</span>
        <span className="text-cyan-500/60">SHA-256 / KECCAK</span>
      </div>
    </div>
  );
}
