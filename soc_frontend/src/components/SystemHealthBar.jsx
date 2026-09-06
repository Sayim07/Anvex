import { useState, useCallback, useRef } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { Cpu, HardDrive, Zap, Clock, Activity } from 'lucide-react';

function CircularRing({ percentage, size = 64, strokeWidth = 5, color = '#38bdf8' }) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - ((percentage ?? 0) / 100) * circumference;

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="rgba(255, 255, 255, 0.08)"
          strokeWidth={strokeWidth}
          fill="transparent"
        />
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          fill="transparent"
          style={{ transition: 'stroke-dashoffset 0.6s ease, stroke 0.3s ease' }}
        />
      </svg>
      <div className="absolute text-xs font-mono font-bold text-slate-100">
        {percentage != null ? `${Math.round(percentage)}%` : '—'}
      </div>
    </div>
  );
}

function MiniSparkline({ data = [], width = 80, height = 30, color = '#38bdf8' }) {
  if (data.length < 2) {
    return (
      <div className="flex items-center justify-center font-mono text-[10px] text-slate-500" style={{ width, height }}>
        Awaiting data…
      </div>
    );
  }

  const min = Math.min(...data);
  const max = Math.max(...data) || 1;
  const range = max - min || 1;

  const points = data
    .map((val, idx) => {
      const x = (idx / (data.length - 1)) * (width - 4) + 2;
      const y = height - 4 - ((val - min) / range) * (height - 8);
      return `${x},${y}`;
    })
    .join(' ');

  return (
    <svg width={width} height={height} className="overflow-visible">
      <polyline
        fill="none"
        stroke={color}
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
        points={points}
      />
    </svg>
  );
}

export default function SystemHealthBar() {
  const [metrics, setMetrics] = useState(null);
  const [flowHistory, setFlowHistory] = useState([10, 15, 22, 18, 30, 25]);
  const [latencyHistory, setLatencyHistory] = useState([8, 12, 10, 14, 11, 9]);
  const lastUpdateRef = useRef(0);

  const handleMessage = useCallback((data) => {
    setMetrics(data);
    if (data.flows_per_sec != null) {
      setFlowHistory((prev) => [...prev.slice(-14), data.flows_per_sec]);
    }
    if (data.avg_latency_ms != null) {
      setLatencyHistory((prev) => [...prev.slice(-14), data.avg_latency_ms]);
    }
    lastUpdateRef.current = Date.now();
  }, []);

  const wsStatus = useWebSocket('/ws/system-metrics', handleMessage);

  const cpu = metrics?.cpu_percent ?? 0;
  const ram = metrics?.ram_percent ?? 0;
  const cpuColor = cpu > 80 ? '#ef4444' : cpu > 60 ? '#f59e0b' : '#38bdf8';
  const ramColor = ram > 80 ? '#ef4444' : ram > 60 ? '#f59e0b' : '#10b981';

  return (
    <div className="glass-panel p-4 border border-sky-500/20">
      {/* Top Header Strip */}
      <div className="flex items-center justify-between pb-3 mb-3 border-b border-sky-500/15">
        <div className="flex items-center gap-2.5">
          <div className="w-2.5 h-2.5 rounded-full bg-cyan-400 shadow-[0_0_8px_#00f0ff] animate-pulse" />
          <span className="text-xs font-mono font-bold tracking-wider text-slate-300 uppercase">
            Hardware & Throughput Telemetry
          </span>
          <span className="text-[10px] font-mono bg-sky-500/15 text-sky-400 px-2 py-0.5 rounded border border-sky-500/25">
            NODE #01
          </span>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <span
              className={`w-2 h-2 rounded-full ${
                wsStatus === 'connected'
                  ? 'bg-emerald-400 shadow-[0_0_8px_#10b981]'
                  : wsStatus === 'connecting'
                  ? 'bg-amber-400 animate-ping'
                  : 'bg-rose-500'
              }`}
            />
            <span className="text-[11px] font-mono text-slate-400">
              {wsStatus === 'connected' ? 'STREAMING 60Hz' : wsStatus === 'connecting' ? 'CONNECTING…' : 'OFFLINE'}
            </span>
          </div>

          {metrics?.ts && (
            <div className="text-[10px] font-mono text-slate-500 flex items-center gap-1 border-l border-slate-700 pl-3">
              <Clock className="w-3 h-3 text-slate-500" />
              {new Date(metrics.ts).toLocaleTimeString()}
            </div>
          )}
        </div>
      </div>

      {/* Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {/* 1. CPU Utilization */}
        <div className="glass-card p-3 flex items-center justify-between border-sky-500/20">
          <div className="flex flex-col">
            <div className="flex items-center gap-1.5 text-xs text-slate-400 mb-1">
              <Cpu className="w-3.5 h-3.5 text-sky-400" />
              <span className="font-semibold uppercase text-[11px] tracking-wider">CPU Load</span>
            </div>
            <div className="text-xl font-bold font-mono text-slate-100" style={{ color: cpuColor }}>
              {metrics?.cpu_percent != null ? `${metrics.cpu_percent.toFixed(1)}%` : '—'}
            </div>
            <span className="text-[10px] font-mono text-slate-500 mt-1">
              {cpu > 80 ? 'CRITICAL SPIKE' : 'NORMAL RANGE'}
            </span>
          </div>
          <CircularRing percentage={metrics?.cpu_percent} color={cpuColor} size={56} strokeWidth={4} />
        </div>

        {/* 2. RAM Utilization */}
        <div className="glass-card p-3 flex items-center justify-between border-sky-500/20">
          <div className="flex flex-col">
            <div className="flex items-center gap-1.5 text-xs text-slate-400 mb-1">
              <HardDrive className="w-3.5 h-3.5 text-emerald-400" />
              <span className="font-semibold uppercase text-[11px] tracking-wider">RAM Memory</span>
            </div>
            <div className="text-xl font-bold font-mono text-slate-100" style={{ color: ramColor }}>
              {metrics?.ram_used_mb != null ? `${Math.round(metrics.ram_used_mb)} MB` : '—'}
            </div>
            <span className="text-[10px] font-mono text-slate-500 mt-1">
              {metrics?.ram_percent != null ? `${metrics.ram_percent.toFixed(1)}% utilized` : 'Memory idle'}
            </span>
          </div>
          <CircularRing percentage={metrics?.ram_percent} color={ramColor} size={56} strokeWidth={4} />
        </div>

        {/* 3. Ingest Flow Rate */}
        <div className="glass-card p-3 flex items-center justify-between border-sky-500/20">
          <div className="flex flex-col">
            <div className="flex items-center gap-1.5 text-xs text-slate-400 mb-1">
              <Zap className="w-3.5 h-3.5 text-cyan-400" />
              <span className="font-semibold uppercase text-[11px] tracking-wider">Flow Ingest</span>
            </div>
            <div className="text-xl font-bold font-mono text-cyan-400">
              {metrics?.flows_per_sec != null ? metrics.flows_per_sec : '0'}
              <span className="text-xs font-normal text-slate-400 ml-1">f/s</span>
            </div>
            <span className="text-[10px] font-mono text-slate-500 mt-1">AI Tensor Ingestion</span>
          </div>
          <div className="flex flex-col items-end">
            <MiniSparkline data={flowHistory} color="#00f0ff" />
            <span className="text-[9px] font-mono text-cyan-400/70 mt-1">real-time</span>
          </div>
        </div>

        {/* 4. Pipeline Latency */}
        <div className="glass-card p-3 flex items-center justify-between border-sky-500/20">
          <div className="flex flex-col">
            <div className="flex items-center gap-1.5 text-xs text-slate-400 mb-1">
              <Activity className="w-3.5 h-3.5 text-indigo-400" />
              <span className="font-semibold uppercase text-[11px] tracking-wider">Inference Latency</span>
            </div>
            <div className="text-xl font-bold font-mono text-indigo-300">
              {metrics?.avg_latency_ms != null ? metrics.avg_latency_ms.toFixed(0) : '—'}
              <span className="text-xs font-normal text-slate-400 ml-1">ms</span>
            </div>
            <span className="text-[10px] font-mono text-slate-500 mt-1">End-to-End Pipeline</span>
          </div>
          <div className="flex flex-col items-end">
            <MiniSparkline data={latencyHistory} color="#818cf8" />
            <span className="text-[9px] font-mono text-indigo-400/70 mt-1">&lt; 15ms SLA</span>
          </div>
        </div>
      </div>
    </div>
  );
}
