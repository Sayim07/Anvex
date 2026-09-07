// ExportLogsModal.jsx — Export threat telemetry logs as JSON / CSV
import { motion, AnimatePresence } from 'framer-motion';
import { X, FileDown, FileJson, FileSpreadsheet } from 'lucide-react';

export default function ExportLogsModal({ isOpen, onClose, alerts = [] }) {
  if (!isOpen) return null;

  const downloadJSON = () => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(alerts, null, 2));
    const dlAnchor = document.createElement('a');
    dlAnchor.setAttribute('href', dataStr);
    dlAnchor.setAttribute('download', `anvex_threat_feed_${new Date().toISOString().slice(0, 19)}.json`);
    dlAnchor.click();
    onClose();
  };

  const downloadCSV = () => {
    if (alerts.length === 0) {
      alert('No alerts to export.');
      return;
    }
    const headers = ['alert_id', 'timestamp', 'source_ip', 'destination_ip', 'threat_class', 'severity', 'confidence', 'tx_hash'];
    const rows = alerts.map((a) => [
      a.alert_id || '',
      a.timestamp || '',
      a.source_ip || '',
      a.destination_ip || '',
      a.threat_class || '',
      a.severity || '',
      a.confidence || '',
      a.tx_hash || '',
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `anvex_threat_feed_${new Date().toISOString().slice(0, 19)}.csv`);
    link.click();
    onClose();
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 10 }}
          className="w-full max-w-md glass-panel p-6 border border-sky-500/30 text-slate-200 shadow-[0_0_30px_rgba(0,240,255,0.15)]"
        >
          <div className="flex items-center justify-between pb-4 border-b border-sky-500/20 mb-5">
            <div className="flex items-center gap-2.5">
              <FileDown className="w-5 h-5 text-cyan-400" />
              <h2 className="text-base font-bold text-slate-100 tracking-wide uppercase font-mono">
                Export Security Logs
              </h2>
            </div>
            <button
              onClick={onClose}
              className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-100 transition-colors cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <p className="text-xs text-slate-400 mb-5 leading-relaxed">
            Download the active live security log buffer ({alerts.length} records) for offline forensic analysis or SIEM compliance ingestion.
          </p>

          <div className="grid grid-cols-2 gap-4 mb-6">
            <button
              onClick={downloadJSON}
              className="flex flex-col items-center justify-center p-4 rounded-xl bg-slate-900/60 border border-sky-500/25 hover:border-cyan-400 hover:bg-sky-500/10 transition-all cursor-pointer group"
            >
              <FileJson className="w-8 h-8 text-cyan-400 mb-2 group-hover:scale-110 transition-transform" />
              <span className="text-xs font-bold text-slate-100">JSON Archive</span>
              <span className="text-[10px] text-slate-400 mt-1">Full Raw Payload</span>
            </button>

            <button
              onClick={downloadCSV}
              className="flex flex-col items-center justify-center p-4 rounded-xl bg-slate-900/60 border border-sky-500/25 hover:border-emerald-400 hover:bg-emerald-500/10 transition-all cursor-pointer group"
            >
              <FileSpreadsheet className="w-8 h-8 text-emerald-400 mb-2 group-hover:scale-110 transition-transform" />
              <span className="text-xs font-bold text-slate-100">CSV Spreadsheet</span>
              <span className="text-[10px] text-slate-400 mt-1">Structured Table</span>
            </button>
          </div>

          <div className="flex justify-end">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-300 transition-colors cursor-pointer"
            >
              Cancel
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
