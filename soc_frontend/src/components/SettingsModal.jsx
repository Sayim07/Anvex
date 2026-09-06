// SettingsModal.jsx — SOC Dashboard Settings Modal
import { motion, AnimatePresence } from 'framer-motion';
import { X, Volume2, Shield, Bell, Cpu, RefreshCw } from 'lucide-react';

export default function SettingsModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 10 }}
          className="w-full max-w-lg glass-panel p-6 border border-sky-500/30 text-slate-200 shadow-[0_0_30px_rgba(0,240,255,0.15)]"
        >
          {/* Header */}
          <div className="flex items-center justify-between pb-4 border-b border-sky-500/20 mb-5">
            <div className="flex items-center gap-2.5">
              <Shield className="w-5 h-5 text-cyan-400" />
              <h2 className="text-base font-bold text-slate-100 tracking-wide uppercase font-mono">
                SOC System Preferences
              </h2>
            </div>
            <button
              onClick={onClose}
              className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-100 transition-colors cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Settings Items */}
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900/60 border border-slate-800">
              <div className="flex items-center gap-3">
                <Volume2 className="w-4 h-4 text-cyan-400" />
                <div>
                  <div className="text-xs font-semibold text-slate-200">Acoustic Threat Alerts</div>
                  <div className="text-[10px] text-slate-400">Play subtle warning chime when CRITICAL threats arrive</div>
                </div>
              </div>
              <input type="checkbox" defaultChecked className="toggle-checkbox accent-cyan-400 cursor-pointer" />
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900/60 border border-slate-800">
              <div className="flex items-center gap-3">
                <Bell className="w-4 h-4 text-amber-400" />
                <div>
                  <div className="text-xs font-semibold text-slate-200">SHAP Explainability Auto-Expand</div>
                  <div className="text-[10px] text-slate-400">Automatically display AI feature attributions on drawer open</div>
                </div>
              </div>
              <input type="checkbox" defaultChecked className="toggle-checkbox accent-cyan-400 cursor-pointer" />
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900/60 border border-slate-800">
              <div className="flex items-center gap-3">
                <Cpu className="w-4 h-4 text-indigo-400" />
                <div>
                  <div className="text-xs font-semibold text-slate-200">Hardware Telemetry Rate</div>
                  <div className="text-[10px] text-slate-400">Polling frequency for CPU and RAM load meters</div>
                </div>
              </div>
              <span className="text-xs font-mono text-cyan-400 bg-cyan-950/60 px-2 py-1 rounded border border-cyan-500/30">
                1000ms
              </span>
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900/60 border border-slate-800">
              <div className="flex items-center gap-3">
                <RefreshCw className="w-4 h-4 text-emerald-400" />
                <div>
                  <div className="text-xs font-semibold text-slate-200">Local Hardhat RPC</div>
                  <div className="text-[10px] font-mono text-slate-400">http://127.0.0.1:8545</div>
                </div>
              </div>
              <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-500/30">
                ACTIVE
              </span>
            </div>
          </div>

          {/* Footer */}
          <div className="mt-6 pt-4 border-t border-sky-500/20 flex justify-end">
            <button
              onClick={onClose}
              className="cyber-btn cyber-btn-primary px-5 py-2 text-xs"
            >
              Done
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
