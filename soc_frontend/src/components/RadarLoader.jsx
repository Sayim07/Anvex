// RadarLoader.jsx — Futuristic Cyber Tactical Radar Loading Screen
import { useState, useEffect } from 'react';

export default function RadarLoader({ onComplete }) {
  const [progress, setProgress] = useState(15);
  const [logText, setLogText] = useState('CALIBRATING AI NEURAL SENSORS...');

  useEffect(() => {
    const logs = [
      'CALIBRATING AI NEURAL SENSORS...',
      'CONNECTING TO TRUST LAYER HARDHAT NODE...',
      'ESTABLISHING WEBSOCKET TELEMETRY PIPELINE...',
      'ARMING REAL-TIME CYBER DEFENSE GRID...',
      'SYSTEM READY: ALL SENSORS GREEN.',
    ];

    let currentLog = 0;
    const interval = setInterval(() => {
      setProgress((prev) => {
        const next = prev + Math.floor(Math.random() * 22) + 12;
        if (next >= 100) {
          clearInterval(interval);
          if (onComplete) setTimeout(onComplete, 350);
          return 100;
        }
        currentLog = Math.min(logs.length - 1, Math.floor((next / 100) * logs.length));
        setLogText(logs[currentLog]);
        return next;
      });
    }, 280);

    return () => clearInterval(interval);
  }, [onComplete]);

  return (
    <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-[#050811] text-slate-100 cyber-scanlines">
      {/* Background glow */}
      <div className="absolute w-96 h-96 rounded-full bg-cyan-500/10 blur-3xl pointer-events-none" />

      {/* Radar Container */}
      <div className="relative w-64 h-64 md:w-80 md:h-80 flex items-center justify-center">
        {/* Concentric Circles */}
        <div className="absolute inset-0 rounded-full border border-cyan-500/20 shadow-[0_0_20px_rgba(0,240,255,0.15)]" />
        <div className="absolute inset-8 rounded-full border border-cyan-500/25" />
        <div className="absolute inset-16 rounded-full border border-cyan-500/30" />
        <div className="absolute inset-24 rounded-full border border-cyan-500/40" />

        {/* Crosshairs */}
        <div className="absolute inset-x-0 top-1/2 h-[1px] bg-cyan-500/30" />
        <div className="absolute inset-y-0 left-1/2 w-[1px] bg-cyan-500/30" />

        {/* Angle markers */}
        <div className="absolute top-2 text-[9px] font-mono text-cyan-400/60 font-semibold tracking-widest">000° NORTH</div>
        <div className="absolute right-2 text-[9px] font-mono text-cyan-400/60 font-semibold tracking-widest">090°</div>
        <div className="absolute bottom-2 text-[9px] font-mono text-cyan-400/60 font-semibold tracking-widest">180° SOUTH</div>
        <div className="absolute left-2 text-[9px] font-mono text-cyan-400/60 font-semibold tracking-widest">270°</div>

        {/* Radar Sweeping Beam */}
        <div className="absolute inset-0 rounded-full overflow-hidden pointer-events-none">
          <div 
            className="w-full h-full origin-center radar-spinner"
            style={{
              background: 'conic-gradient(from 0deg, transparent 0deg, transparent 270deg, rgba(0, 240, 255, 0.45) 360deg)',
            }}
          />
        </div>

        {/* Threat Blips */}
        <div className="absolute top-1/4 left-1/3 w-2.5 h-2.5 bg-rose-500 rounded-full animate-ping" />
        <div className="absolute top-1/4 left-1/3 w-2 h-2 bg-rose-400 rounded-full shadow-[0_0_8px_#ef4444]" />

        <div className="absolute bottom-1/3 right-1/4 w-2 h-2 bg-emerald-400 rounded-full shadow-[0_0_8px_#10b981]" />

        {/* Center Target Dot */}
        <div className="relative w-3 h-3 bg-cyan-400 rounded-full shadow-[0_0_12px_#00f0ff] z-10">
          <div className="absolute -inset-1 rounded-full border border-cyan-300 animate-ping opacity-75" />
        </div>
      </div>

      {/* Telemetry Status Readout */}
      <div className="mt-8 flex flex-col items-center gap-3 max-w-md text-center px-4">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse shadow-[0_0_8px_#00f0ff]" />
          <span className="text-xs font-mono tracking-widest text-cyan-400 uppercase font-bold">
            AVNEX SOC DEFENSE MATRIX
          </span>
        </div>

        <div className="font-mono text-xs text-slate-300 h-5">
          {logText}
        </div>

        {/* Progress bar */}
        <div className="w-64 h-1.5 bg-slate-800/80 rounded-full overflow-hidden border border-cyan-500/30 p-[1px]">
          <div 
            className="h-full bg-gradient-to-r from-sky-500 to-cyan-400 rounded-full transition-all duration-300 shadow-[0_0_8px_#00f0ff]"
            style={{ width: `${progress}%` }}
          />
        </div>

        <div className="text-[11px] font-mono text-slate-500">
          INITIALIZING TELEMETRY // {progress}%
        </div>
      </div>
    </div>
  );
}
