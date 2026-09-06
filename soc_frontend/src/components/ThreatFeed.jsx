import { useState, useCallback, useRef } from 'react';
import { AnimatePresence } from 'framer-motion';
import { useWebSocket } from '../hooks/useWebSocket';
import EvidenceDrawer from './EvidenceDrawer';
import ThreatSkeleton from './ThreatSkeleton';
import DecryptText from './DecryptText';
import {
  Play,
  Pause,
  Trash2,
  Search,
  ChevronDown,
  ChevronUp,
  ShieldCheck,
  Radio,
} from 'lucide-react';

const MAX_ALERTS = 200;

function ThreatClassBadge({ cls }) {
  const styles = {
    DDOS:         'bg-rose-950/70 border-rose-500/60 text-rose-300',
    PORT_SCAN:    'bg-sky-950/70 border-sky-500/60 text-sky-300',
    DGA_DOMAIN:   'bg-purple-950/70 border-purple-500/60 text-purple-300',
    C2_BEACON:    'bg-violet-950/70 border-violet-500/60 text-violet-300',
    TLS_MALWARE:  'bg-stone-900 border-stone-600 text-stone-300',
    EXFILTRATION: 'bg-amber-950/70 border-amber-500/60 text-amber-300',
  };
  const clsStyle = styles[cls] || 'bg-slate-900 border-slate-700 text-slate-300';

  return (
    <span className={`px-2.5 py-0.5 rounded text-[11px] font-mono font-bold tracking-wide border whitespace-nowrap ${clsStyle}`}>
      {cls}
    </span>
  );
}

function AlertRow({ alert, isExpanded, onToggle, onVerify, isRecent }) {
  const severity = alert.severity?.toUpperCase();
  const isCritical = severity === 'CRITICAL';
  const isHigh = severity === 'HIGH';
  const localTime = new Date(alert.timestamp).toLocaleTimeString();

  return (
    <>
      <tr
        onClick={onToggle}
        className={`cyber-table-row ${isCritical ? 'critical' : isHigh ? 'high' : ''} ${
          isExpanded ? 'active-row' : ''
        }`}
        title="Click to view full forensic telemetry and SHAP explanations"
      >
        {/* Time */}
        <td className="p-3 text-xs font-mono text-slate-400 whitespace-nowrap">
          {localTime}
        </td>

        {/* Source -> Dest */}
        <td className="p-3 text-xs font-mono whitespace-nowrap">
          <span className="text-cyan-300 font-semibold">
            {isRecent && isCritical ? (
              <DecryptText text={alert.source_ip} speed={18} />
            ) : (
              alert.source_ip
            )}
          </span>
          <span className="text-slate-500 mx-2">→</span>
          <span className="text-purple-300 font-semibold">
            {isRecent && isCritical ? (
              <DecryptText text={alert.destination_ip} speed={22} />
            ) : (
              alert.destination_ip
            )}
          </span>
        </td>

        {/* Threat Class */}
        <td className="p-3">
          <ThreatClassBadge cls={alert.threat_class} />
        </td>

        {/* Severity */}
        <td className="p-3">
          <span
            className={
              isCritical
                ? 'badge-critical pulse-critical'
                : isHigh
                ? 'badge-high pulse-high'
                : 'badge-high'
            }
          >
            {severity}
          </span>
        </td>

        {/* Confidence */}
        <td className="p-3">
          <span className="badge-confidence">
            {(alert.confidence * 100).toFixed(1)}%
          </span>
        </td>

        {/* Tx Hash */}
        <td className="p-3">
          {alert.tx_hash ? (
            <span className="badge-tx" title={alert.tx_hash}>
              ⛓ {alert.tx_hash.slice(0, 10)}…
            </span>
          ) : (
            <span className="text-[11px] font-mono text-slate-500">pending</span>
          )}
        </td>

        {/* Verify Quick Action */}
        <td className="p-3" onClick={(e) => e.stopPropagation()}>
          <button
            onClick={() => onVerify(alert.alert_id)}
            className="cyber-btn cyber-btn-verify text-[11px] py-1 px-2.5 cursor-pointer"
            title="Send alert_id directly to Blockchain Verifier"
          >
            <ShieldCheck className="w-3 h-3 text-emerald-400" />
            Verify
          </button>
        </td>

        {/* Expand Arrow */}
        <td className="p-3 text-slate-500 text-xs">
          {isExpanded ? <ChevronUp className="w-4 h-4 text-cyan-400" /> : <ChevronDown className="w-4 h-4" />}
        </td>
      </tr>

      {/* Expandable Drawer inside AnimatePresence */}
      {isExpanded && (
        <tr>
          <td colSpan={8} className="p-0 border-b border-sky-500/20">
            <AnimatePresence>
              <EvidenceDrawer alert={alert} onVerify={onVerify} />
            </AnimatePresence>
          </td>
        </tr>
      )}
    </>
  );
}

export default function ThreatFeed({ onVerifyRequest }) {
  const [alerts, setAlerts] = useState([]);
  const [expandedId, setExpandedId] = useState(null);
  const [paused, setPaused] = useState(false);
  const [pendingCount, setPendingCount] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const alertCountRef = useRef(0);
  const pendingBufferRef = useRef([]);
  const pausedRef = useRef(false);

  const handleMessage = useCallback((data) => {
    if (pausedRef.current) {
      if (!data.alert_id || !pendingBufferRef.current.some((a) => a.alert_id === data.alert_id)) {
        pendingBufferRef.current.push(data);
        setPendingCount(pendingBufferRef.current.length);
      }
      setPaused(true);
    } else {
      setAlerts((prev) => {
        if (data.alert_id && prev.some((a) => a.alert_id === data.alert_id)) {
          return prev;
        }
        alertCountRef.current += 1;
        const next = [{ ...data, _key: alertCountRef.current, _isNew: true }, ...prev];
        return next.slice(0, MAX_ALERTS);
      });
    }
  }, []);

  const wsStatus = useWebSocket('/ws/alerts', handleMessage);

  const toggleRow = (id) => setExpandedId((prev) => (prev === id ? null : id));

  const togglePause = () => {
    const willPause = !pausedRef.current;
    pausedRef.current = willPause;

    if (!willPause) {
      const buffered = pendingBufferRef.current.splice(0);
      setPendingCount(0);
      if (buffered.length > 0) {
        setAlerts((prev) => {
          const newAlerts = [...buffered].reverse().map((d) => {
            alertCountRef.current += 1;
            return { ...d, _key: alertCountRef.current };
          });
          return [...newAlerts, ...prev].slice(0, MAX_ALERTS);
        });
      }
    }
    setPaused(willPause);
  };

  const filteredAlerts = alerts.filter((a) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      a.source_ip?.toLowerCase().includes(q) ||
      a.destination_ip?.toLowerCase().includes(q) ||
      a.threat_class?.toLowerCase().includes(q) ||
      a.severity?.toLowerCase().includes(q) ||
      a.alert_id?.toLowerCase().includes(q)
    );
  });

  return (
    <div className="glass-panel flex-1 flex flex-col overflow-hidden border border-sky-500/20">
      {/* Panel Top Action Bar */}
      <div className="p-3.5 border-b border-sky-500/15 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <div className="relative flex">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500 shadow-[0_0_10px_#ef4444]" />
            <span className="absolute -inset-0.5 rounded-full bg-rose-500 animate-ping opacity-75" />
          </div>
          <span className="text-xs font-mono font-bold tracking-wider text-slate-100 uppercase">
            Live Threat Stream
          </span>
          <span className="text-xs font-mono bg-rose-500/15 text-rose-300 border border-rose-500/30 px-2 py-0.5 rounded-full font-bold">
            {alerts.length} DETECTIONS
          </span>
        </div>

        {/* Search Filter Bar */}
        <div className="relative flex-1 max-w-xs">
          <input
            type="text"
            placeholder="Filter IP, class, severity..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="cyber-input text-xs py-1.5 pl-8 pr-3 bg-slate-900/60 border-slate-700 focus:border-cyan-400"
          />
          <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-1/2 -translate-y-1/2" />
        </div>

        {/* Stream Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={togglePause}
            className={`cyber-btn text-xs py-1.5 px-3 border cursor-pointer ${
              paused
                ? 'bg-amber-500/20 border-amber-500/50 text-amber-300 hover:bg-amber-500/30'
                : 'bg-sky-500/15 border-sky-500/35 text-sky-300 hover:bg-sky-500/25'
            }`}
            title={paused ? 'Resume live feed' : 'Pause live feed'}
          >
            {paused ? <Play className="w-3.5 h-3.5" /> : <Pause className="w-3.5 h-3.5" />}
            {paused ? (
              <span>Resume {pendingCount > 0 && `(+${pendingCount})`}</span>
            ) : (
              <span>Pause</span>
            )}
          </button>

          {alerts.length > 0 && (
            <button
              onClick={() => {
                setAlerts([]);
                fetch('/api/alerts/clear', { method: 'POST' }).catch(() => {});
              }}
              className="cyber-btn bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-slate-300 text-xs py-1.5 px-2.5 cursor-pointer"
              title="Reset feed back to System Armed"
            >
              <Trash2 className="w-3.5 h-3.5" />
              Clear
            </button>
          )}

          <div className="flex items-center gap-1.5 pl-2 border-l border-slate-700">
            <Radio className={`w-3.5 h-3.5 ${wsStatus === 'connected' ? 'text-emerald-400 animate-pulse' : 'text-slate-500'}`} />
            <span className="text-[11px] font-mono text-slate-400">
              {paused ? 'PAUSED' : wsStatus === 'connected' ? 'STREAMING' : 'OFFLINE'}
            </span>
          </div>
        </div>
      </div>

      {/* Table Container */}
      <div className="flex-1 overflow-auto">
        <table className="w-full border-collapse text-left">
          <thead>
            <tr className="border-b border-sky-500/20 bg-slate-950/60 sticky top-0 z-10 backdrop-blur-md">
              {['Timestamp', 'Source → Destination', 'Threat Category', 'Severity', 'Confidence', 'Blockchain Hash', 'Action', ''].map((col, idx) => (
                <th
                  key={idx}
                  className="p-3 text-[10px] font-mono uppercase tracking-wider text-slate-400 font-semibold"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {wsStatus !== 'connected' && alerts.length === 0 ? (
              <ThreatSkeleton rows={5} />
            ) : filteredAlerts.length === 0 ? (
              <tr>
                <td colSpan={8} className="p-12 text-center">
                  <div className="flex flex-col items-center gap-3">
                    <div className="w-14 h-14 rounded-full bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shadow-[0_0_20px_rgba(16,185,129,0.15)]">
                      <ShieldCheck className="w-7 h-7 text-emerald-400" />
                    </div>
                    <div className="text-sm font-bold font-mono text-emerald-400 tracking-wider uppercase">
                      Cyber Perimeter Armed // No Active Intrusions
                    </div>
                    <p className="text-xs text-slate-400 max-w-sm leading-relaxed">
                      All neural detection models are scanning ingress and egress packets. High-severity threats will appear here in real-time.
                    </p>
                  </div>
                </td>
              </tr>
            ) : (
              filteredAlerts.map((alert) => (
                <AlertRow
                  key={alert._key}
                  alert={alert}
                  isExpanded={expandedId === alert._key}
                  onToggle={() => toggleRow(alert._key)}
                  onVerify={onVerifyRequest}
                  isRecent={alert._isNew}
                />
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
