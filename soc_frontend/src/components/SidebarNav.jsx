// SidebarNav.jsx — Sleek Collapsible Hamburger Sidebar using Framer Motion
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard,
  ShieldAlert,
  Blocks,
  Activity,
  Settings,
  FileDown,
  Menu,
  ChevronLeft,
  ShieldCheck,
} from 'lucide-react';

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'threats', label: 'Live Threat Feed', icon: ShieldAlert, badge: 'LIVE' },
  { id: 'blockchain', label: 'Blockchain Audit', icon: Blocks, badge: 'ON-CHAIN' },
  { id: 'health', label: 'System Health', icon: Activity },
  { id: 'settings', label: 'Settings', icon: Settings },
  { id: 'export', label: 'Export Logs', icon: FileDown },
];

export default function SidebarNav({
  isExpanded,
  onToggle,
  activeTab,
  onSelectTab,
  threatCount = 0,
}) {
  const sidebarVariants = {
    expanded: { width: 250, transition: { type: 'spring', damping: 20, stiffness: 200 } },
    collapsed: { width: 72, transition: { type: 'spring', damping: 20, stiffness: 200 } },
  };

  return (
    <motion.aside
      initial={false}
      animate={isExpanded ? 'expanded' : 'collapsed'}
      variants={sidebarVariants}
      className="relative z-30 flex flex-col h-full bg-[#090e1c]/90 backdrop-blur-xl border-r border-sky-500/20 shadow-[4px_0_24px_rgba(0,0,0,0.5)] select-none shrink-0"
    >
      {/* Top Brand & Hamburger Toggle */}
      <div className="flex items-center justify-between p-4 border-b border-sky-500/15 h-16">
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center text-white shadow-[0_0_15px_rgba(37,99,235,0.5)] shrink-0">
            <ShieldCheck className="w-5 h-5 text-cyan-300" />
          </div>

          <AnimatePresence>
            {isExpanded && (
              <motion.div
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                transition={{ duration: 0.15 }}
                className="whitespace-nowrap"
              >
                <div className="font-extrabold text-base tracking-wider text-slate-100 flex items-center gap-1.5">
                  ANVEX
                  <span className="text-[10px] bg-cyan-500/20 text-cyan-400 px-1.5 py-0.5 rounded border border-cyan-500/30">
                    SOC
                  </span>
                </div>
                <div className="text-[10px] text-slate-400 tracking-wider uppercase font-mono">
                  Cyber Defense Grid
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <button
          onClick={onToggle}
          className="p-1.5 rounded-lg hover:bg-sky-500/15 text-slate-400 hover:text-cyan-300 transition-colors cursor-pointer"
          title={isExpanded ? 'Collapse Menu' : 'Expand Menu'}
        >
          {isExpanded ? <ChevronLeft className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </div>

      {/* Nav List */}
      <nav className="flex-1 py-4 px-2 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;

          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-3 rounded-xl transition-all duration-200 group relative cursor-pointer ${
                isActive
                  ? 'bg-gradient-to-r from-sky-500/20 to-indigo-500/10 text-cyan-300 border border-sky-500/40 shadow-[0_0_15px_rgba(56,189,248,0.2)]'
                  : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/40'
              }`}
              title={!isExpanded ? item.label : undefined}
            >
              <div className="relative shrink-0">
                <Icon
                  className={`w-5 h-5 transition-transform duration-200 ${
                    isActive
                      ? 'text-cyan-400 scale-110'
                      : 'text-slate-400 group-hover:text-cyan-300 group-hover:scale-105'
                  }`}
                />
                {/* Active Indicator dot */}
                {isActive && (
                  <motion.div
                    layoutId="activeDot"
                    className="absolute -left-3 top-1/2 -translate-y-1/2 w-1.5 h-6 bg-cyan-400 rounded-r shadow-[0_0_8px_#00f0ff]"
                  />
                )}
              </div>

              <AnimatePresence>
                {isExpanded && (
                  <motion.div
                    initial={{ opacity: 0, x: -6 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -6 }}
                    transition={{ duration: 0.15 }}
                    className="flex items-center justify-between flex-1 overflow-hidden whitespace-nowrap"
                  >
                    <span className="text-xs font-semibold tracking-wide">
                      {item.label}
                    </span>

                    {/* Threat Count or Badge */}
                    {item.id === 'threats' && threatCount > 0 ? (
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/40 font-bold animate-pulse">
                        {threatCount}
                      </span>
                    ) : item.badge ? (
                      <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-sky-500/15 text-sky-400 border border-sky-500/25">
                        {item.badge}
                      </span>
                    ) : null}
                  </motion.div>
                )}
              </AnimatePresence>
            </button>
          );
        })}
      </nav>

      {/* Bottom Node Health Status */}
      <div className="p-3 border-t border-sky-500/15">
        <div className="flex items-center gap-3 px-2 py-2 rounded-lg bg-slate-900/60 border border-slate-800">
          <div className="relative flex shrink-0">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 shadow-[0_0_8px_#10b981]" />
            <span className="absolute -inset-0.5 rounded-full bg-emerald-400 animate-ping opacity-75" />
          </div>
          <AnimatePresence>
            {isExpanded && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="overflow-hidden whitespace-nowrap"
              >
                <div className="text-[11px] font-mono text-emerald-400 font-bold">
                  SENSORS ONLINE
                </div>
                <div className="text-[9px] font-mono text-slate-500">
                  BLOCKCHAIN NODE #31337
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </motion.aside>
  );
}
