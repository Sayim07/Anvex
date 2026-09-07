// App.jsx — Anvex Futuristic Enterprise Cyber Operations Center Layout
import { useState, useCallback } from 'react';
import SidebarNav from './components/SidebarNav';
import SystemHealthBar from './components/SystemHealthBar';
import ThreatFeed from './components/ThreatFeed';
import BlockchainVerifier from './components/BlockchainVerifier';
import CyberGlobe3D from './components/CyberGlobe3D';
import RadarLoader from './components/RadarLoader';
import SettingsModal from './components/SettingsModal';
import ExportLogsModal from './components/ExportLogsModal';
import HeroLanding from './components/HeroLanding';
import { Terminal, Activity } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

function Header() {
  return (
    <header className="h-16 px-6 bg-[#090e1c]/80 backdrop-blur-xl border-b border-sky-500/20 flex items-center justify-between z-20 shrink-0 select-none">
      {/* Brand & 3D Interactive Cyber Globe */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-3">
          <CyberGlobe3D size={44} />
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-lg tracking-wider text-slate-100 font-mono">
                ANVEX
              </span>
              <span className="text-[10px] font-mono font-bold bg-sky-500/20 text-cyan-300 border border-sky-500/40 px-2 py-0.5 rounded-full">
                ENTERPRISE SOC v2.0
              </span>
            </div>
            <div className="text-[10px] text-slate-400 font-mono tracking-wider uppercase">
              AI Cyber Threat Intelligence & Immutable Trust Layer
            </div>
          </div>
        </div>
      </div>

      {/* Center Tactical Status */}
      <div className="hidden md:flex items-center gap-6 text-xs font-mono">
        <div className="flex items-center gap-2">
          <span className="text-slate-400">AI MODEL:</span>
          <span className="text-cyan-300 font-bold bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-500/30">
            XGB-NEURAL-V3
          </span>
        </div>
      </div>

      {/* Right: Status Pills */}
      <div className="flex items-center gap-2.5">
        <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono font-semibold shadow-[0_0_12px_rgba(16,185,129,0.2)]">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>LIVE STREAM</span>
        </div>
      </div>
    </header>
  );
}

export default function App() {
  const [currentView, setCurrentView] = useState('landing');
  const [sidebarExpanded, setSidebarExpanded] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [pendingVerifyId, setPendingVerifyId] = useState(null);
  const [initialLoading, setInitialLoading] = useState(true);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isExportOpen, setIsExportOpen] = useState(false);

  // Handle Tab Selection
  const handleSelectTab = (tabId) => {
    if (tabId === 'settings') {
      setIsSettingsOpen(true);
      return;
    }
    if (tabId === 'export') {
      setIsExportOpen(true);
      return;
    }
    setActiveTab(tabId);
  };

  const handleVerifyRequest = useCallback((alertId) => {
    setPendingVerifyId({ id: alertId, ts: Date.now() });
    // If user is on threats-only tab, switch to dashboard or keep current
  }, []);

  return (
    <div className="flex h-screen w-screen bg-[#050811] text-slate-100 overflow-hidden font-sans relative">
      <AnimatePresence mode="wait">
        {currentView === 'landing' ? (
          <HeroLanding key="landing" onEnterDashboard={() => setCurrentView('dashboard')} />
        ) : (
          <motion.div 
            key="dashboard"
            initial={{ opacity: 0, scale: 0.98, y: 15 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 1.02, y: -15 }}
            transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
            className="flex h-full w-full cyber-grid-bg relative"
          >
            {/* Radar Initial Thematic Loader */}
            {initialLoading && (
              <RadarLoader onComplete={() => setInitialLoading(false)} />
            )}

            {/* Collapsible Hamburger Sidebar */}
            <SidebarNav
              isExpanded={sidebarExpanded}
              onToggle={() => setSidebarExpanded((prev) => !prev)}
              activeTab={activeTab}
              onSelectTab={handleSelectTab}
              onReturnToLanding={() => setCurrentView('landing')}
            />

            {/* Main Dashboard Workspace */}
            <div className="flex-1 flex flex-col h-full min-w-0 overflow-hidden relative z-10">
              <Header />

              <main className="flex-1 overflow-hidden p-4 sm:p-5 flex flex-col gap-4">
          {/* Top System Health Bar */}
          <SystemHealthBar />

          {/* Active View Routing */}
          {activeTab === 'dashboard' && (
            <div className="flex-1 flex flex-col lg:flex-row gap-4 overflow-hidden min-h-0">
              <ThreatFeed onVerifyRequest={handleVerifyRequest} />
              <BlockchainVerifier externalRequest={pendingVerifyId} />
            </div>
          )}

          {activeTab === 'threats' && (
            <div className="flex-1 flex flex-col overflow-hidden min-h-0">
              <ThreatFeed onVerifyRequest={handleVerifyRequest} />
            </div>
          )}

          {activeTab === 'blockchain' && (
            <div className="flex-1 flex flex-col lg:flex-row gap-4 overflow-hidden min-h-0">
              <BlockchainVerifier externalRequest={pendingVerifyId} />
              <div className="flex-1 glass-panel p-6 border border-sky-500/20 overflow-y-auto space-y-4">
                <div className="flex items-center gap-2 text-cyan-400 font-mono text-sm font-bold">
                  <Terminal className="w-4 h-4" />
                  IMMUTABLE AUDIT TRAIL // LOCAL HARDHAT NODE
                </div>
                <p className="text-xs text-slate-400 leading-relaxed font-mono">
                  Every high-severity detection is computed into a deterministic SHA-256 hash incorporating the flow metadata, ML confidence, and timestamp. The hash is subsequently notarized into the Ethereum smart contract <code className="text-cyan-300">CyberThreatRegistry</code> for cryptographic non-repudiation.
                </p>
                <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2 font-mono text-xs">
                  <div className="text-slate-500 uppercase text-[10px]">Smart Contract Method</div>
                  <code className="text-emerald-300 block bg-slate-950 p-2.5 rounded border border-slate-800">
                    function recordThreat(string calldata alertId, bytes32 alertHash, string calldata threatClass, uint256 confidence) external
                  </code>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'health' && (
            <div className="flex-1 glass-panel p-6 border border-sky-500/20 overflow-y-auto space-y-6">
              <div className="flex items-center gap-2 text-cyan-400 font-mono text-sm font-bold">
                <Activity className="w-4 h-4" />
                EXTENDED HARDWARE & INGESTION TELEMETRY
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="glass-card p-4 border-sky-500/20">
                  <div className="text-xs text-slate-400 font-mono uppercase mb-2">Ingress Network Adapter</div>
                  <div className="text-lg font-mono text-cyan-400 font-bold">eth0 / promiscuous</div>
                  <div className="text-xs text-slate-500 mt-1">Zero-copy packet ring buffer active</div>
                </div>
                <div className="glass-card p-4 border-sky-500/20">
                  <div className="text-xs text-slate-400 font-mono uppercase mb-2">Inference Acceleration</div>
                  <div className="text-lg font-mono text-emerald-400 font-bold">ONNX Runtime / AVX2</div>
                  <div className="text-xs text-slate-500 mt-1">Batch size: 64 flows / inference</div>
                </div>
                <div className="glass-card p-4 border-sky-500/20">
                  <div className="text-xs text-slate-400 font-mono uppercase mb-2">Block Gas Utilization</div>
                  <div className="text-lg font-mono text-purple-400 font-bold">64,281 gas / tx</div>
                  <div className="text-xs text-slate-500 mt-1">Constant O(1) storage overhead</div>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>

      {/* Settings & Export Modals */}
      <SettingsModal isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
      <ExportLogsModal isOpen={isExportOpen} onClose={() => setIsExportOpen(false)} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
