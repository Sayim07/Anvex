import { motion } from 'framer-motion';
import { Canvas, useFrame } from '@react-three/fiber';
import { useRef } from 'react';
import { ShieldCheck, ArrowRight, Activity, Cpu, Layers, Lock } from 'lucide-react';

function WireframeRadar() {
  const groupRef = useRef();
  
  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y += 0.002;
      groupRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.5) * 0.1;
      groupRef.current.position.x = 2.0 + (state.mouse.x * 0.2);
      groupRef.current.position.y = (state.mouse.y * 0.2);
    }
  });

  return (
    <group ref={groupRef}>
      <mesh>
        <sphereGeometry args={[2.5, 32, 32]} />
        <meshBasicMaterial color="#00f0ff" wireframe transparent opacity={0.15} />
      </mesh>
      <mesh scale={0.8}>
        <sphereGeometry args={[2.5, 16, 16]} />
        <meshBasicMaterial color="#3b82f6" wireframe transparent opacity={0.2} />
      </mesh>
      <points>
        <sphereGeometry args={[2.55, 16, 16]} />
        <pointsMaterial color="#10b981" size={0.03} transparent opacity={0.8} />
      </points>
    </group>
  );
}

export default function HeroLanding({ onEnterDashboard }) {
  return (
    <motion.div 
      key="landing"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0, transition: { duration: 0.5 } }}
      className="relative w-full h-screen bg-[#0a0e17] text-slate-100 overflow-hidden font-sans flex flex-col"
    >
      {/* 3D Background */}
      <div className="absolute inset-0 z-0 pointer-events-auto">
         <Canvas camera={{ position: [0, 0, 7], fov: 45 }}>
            <ambientLight intensity={0.5} />
            <WireframeRadar />
         </Canvas>
      </div>

      {/* Grid overlay for texture */}
      <div className="absolute inset-0 z-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMCIgaGVpZ2h0PSIyMCI+PHJlY3Qgd2lkdGg9IjIwIiBoZWlnaHQ9IjIwIiBmaWxsPSJub25lIiBzdHJva2U9InJnYmEoMjU1LDI1NSwyNTUsMC4wNSkiIHN0cm9rZS13aWR0aD0iMSIvPjwvc3ZnPg==')] opacity-30 pointer-events-none" />

      {/* Content Layer */}
      <div className="relative z-10 flex flex-col h-full pointer-events-none">
        
        {/* Top Nav */}
        <header className="flex items-center justify-between p-6 pointer-events-auto shrink-0">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center text-white shadow-[0_0_15px_rgba(37,99,235,0.5)]">
              <ShieldCheck className="w-5 h-5 text-cyan-300" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-xl tracking-wider text-slate-100 font-mono">AVNEX</span>
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-500"></span>
                </span>
              </div>
              <div className="text-[10px] text-slate-400 tracking-wider uppercase font-mono mt-0.5">
                ENTERPRISE CYBER DEFENSE
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4 md:gap-6">
            <div className="hidden md:flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono font-bold shadow-[0_0_12px_rgba(16,185,129,0.2)]">
              NETWORK DIODE: SYNCHRONIZED
            </div>
            <button 
              onClick={onEnterDashboard}
              className="flex items-center gap-2 px-4 md:px-5 py-2 rounded-lg bg-sky-500/10 border border-sky-500/40 text-cyan-300 font-mono text-sm hover:bg-sky-500/20 hover:shadow-[0_0_20px_rgba(56,189,248,0.4)] transition-all cursor-pointer pointer-events-auto"
            >
              <span className="hidden sm:inline">ENTER SOC CONSOLE</span>
              <span className="sm:hidden">SOC</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </header>

        {/* Main Hero Center */}
        <main className="flex-1 flex flex-col justify-center px-6 md:px-16 lg:px-24 pointer-events-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.1 }}
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-mono font-semibold mb-6 shadow-[0_0_10px_rgba(99,102,241,0.2)]">
              ZERO-TRUST SURVEILLANCE FOR AIR-GAPPED INFRASTRUCTURE
            </div>
            
            <h1 className="text-4xl md:text-5xl lg:text-7xl font-extrabold tracking-tight leading-[1.1] mb-6 drop-shadow-lg">
              Passive AI Surveillance Radar <br className="hidden md:block" />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">
                for Unidirectional IP Traffic
              </span>
            </h1>

            <p className="text-base md:text-xl text-slate-400 max-w-3xl leading-relaxed mb-10">
              Continuous behavioral telemetry analysis and immutable EVM forensic notarization without touching encrypted payloads.
            </p>

            <div className="flex flex-wrap gap-4">
              <button 
                onClick={onEnterDashboard}
                className="flex items-center gap-3 px-6 md:px-8 py-3 md:py-4 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-bold tracking-wide shadow-[0_0_30px_rgba(6,182,212,0.4)] transition-all cursor-pointer transform hover:scale-[1.02]"
              >
                INITIALIZE SOC HUD
              </button>
              <button className="flex items-center gap-3 px-6 md:px-8 py-3 md:py-4 rounded-xl bg-slate-800/50 hover:bg-slate-800 border border-slate-700 text-slate-300 font-bold tracking-wide transition-all cursor-pointer transform hover:scale-[1.02]">
                VIEW CORE ARCHITECTURE
              </button>
            </div>
          </motion.div>
        </main>

        {/* Telemetry Bottom Banner */}
        <footer className="grid grid-cols-2 lg:grid-cols-4 border-t border-slate-800/50 bg-[#0a0e17]/80 backdrop-blur-md pointer-events-auto shrink-0">
          <StatCard icon={Activity} title="0.0% Network Overhead" subtitle="100% Passive SPAN Mirroring" />
          <StatCard icon={Cpu} title="< 25ms Pipeline Latency" subtitle="Sub-millisecond Feature Inference" />
          <StatCard icon={Layers} title="Dual-Engine AI Core" subtitle="XGBoost Classifier + Isolation Forest" />
          <StatCard icon={Lock} title="Forensic Immutability" subtitle="EVM SHA-256 Chain-of-Custody" />
        </footer>
      </div>
    </motion.div>
  );
}

function StatCard({ icon: Icon, title, subtitle }) {
  return (
    <div className="flex flex-col p-4 md:p-6 border-r border-b lg:border-b-0 border-slate-800/50 hover:bg-slate-800/30 transition-colors">
      <Icon className="w-5 h-5 md:w-6 md:h-6 text-cyan-400 mb-2 md:mb-3" />
      <div className="font-mono text-xs md:text-sm font-bold text-slate-200 mb-1">{title}</div>
      <div className="text-[10px] md:text-xs text-slate-500 leading-tight">{subtitle}</div>
    </div>
  );
}
