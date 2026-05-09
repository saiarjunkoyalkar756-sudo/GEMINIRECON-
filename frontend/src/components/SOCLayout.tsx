import React from 'react';
import { Shield, Search, Zap, Terminal, Database, Activity, Cpu, AlertTriangle, ChevronRight, Eye, Layers, Code, ExternalLink, Clock, Settings, Server, Bot } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// Assuming interfaces like Asset, Finding, Log, ChatMessage are defined globally or imported

// --- MOCK DATA ---
interface Asset { domain: string; ip: string; tech: string[]; status: 'LIVE' | 'DOWN'; }
interface Finding { id: number; severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW'; title: string; asset: string; url?: string; }
interface Log { time: string; tag: 'PLAN' | 'RECON' | 'ANALYSIS' | 'RISK' | 'REPORT' | 'TOOL' | 'ERROR' | 'INFO'; message: string; type?: string; }

const MOCK_ASSETS: Asset[] = [
  { domain: "api.example.in", ip: "103.69.39.1", tech: ["Node.js", "Express", "PostgreSQL"], status: "LIVE" },
  { domain: "admin.example.in", ip: "103.69.39.2", tech: ["PHP", "WordPress", "Apache"], status: "LIVE" },
  { domain: "mail.example.in", ip: "103.69.39.3", tech: ["Postfix", "Dovecot"], status: "LIVE" },
  { domain: "dev.example.in", ip: "103.69.39.4", tech: ["Python", "Django"], status: "DOWN" },
  { domain: "vpn.example.in", ip: "103.69.39.5", tech: ["OpenVPN"], status: "LIVE" },
];

const MOCK_FINDINGS: Finding[] = [
  { id: 1, severity: 'CRITICAL', title: 'SQL Injection on Login Page', asset: 'admin.example.in', url: '/login.php?id=1' },
  { id: 2, severity: 'HIGH', title: 'Exposed .env file with API keys', asset: 'dev.example.in', url: '/.env' },
  { id: 3, severity: 'MEDIUM', title: 'Missing Security Headers (CSP)', asset: 'api.example.in', url: '/' },
  { id: 4, severity: 'LOW', title: 'Outdated Apache Version (2.4.41)', asset: 'www.example.in', url: '/' },
  { id: 5, severity: 'CRITICAL', title: 'Remote Code Execution via File Upload', asset: 'vpn.example.in', url: '/upload' },
  { id: 6, severity: 'MEDIUM', title: 'Default CMS Admin Panel', asset: 'admin.example.in', url: '/admin' },
  { id: 7, severity: 'HIGH', title: 'Open Directory Listing', asset: 'www.example.in', url: '/files/' },
  { id: 8, severity: 'LOW', title: 'Missing SPF Record', asset: 'mail.example.in', url: '' },
];

const SOCLayout = ({ children }: any) => {
  const [assets, setAssets] = useState<Asset[]>(MOCK_ASSETS);
  const [findings, setFindings] = useState<Finding[]>(MOCK_FINDINGS);

  return (
    <div className="grid grid-cols-1 md:grid-cols-12 gap-6 h-[calc(100vh-180px)]">
      {/* Left Sidebar (Desktop) */}
      <aside className="hidden md:flex md:col-span-2 flex-col gap-6 p-6 glass border border-white/10 rounded-xl">
        <h2 className="text-xs tracking-widest text-green-500">// NEW_SCAN</h2>
        <div className="relative">
          <input 
            className="w-full bg-black/50 p-3 border border-green-500/40 text-green-400 text-lg focus:ring-2 ring-green-500/50 outline-none rounded-lg shadow-inner" 
            placeholder="❯ target_url"
            // Target input state managed by parent App component
          />
        </div>
        <NeonBorderButton className="text-black font-bold py-3 shadow-glow-primary">SCAN</NeonBorderButton>

        <h2 className="text-xs tracking-widest text-cyan-500 mt-6">// ACTIVE_OPS</h2>
        <div className="space-y-2">
          <div className="flex items-center gap-3 text-sm text-gray-400 hover:text-white transition-colors">
            <Zap className="w-4 h-4" /> <span className="flex-1">Recent Scans</span> <span className="text-xs text-primary">3</span>
          </div>
          <div className="flex items-center gap-3 text-sm text-gray-400 hover:text-white transition-colors">
            <History className="w-4 h-4" /> <span className="flex-1">Scan History</span> <span className="text-xs">12</span>
          </div>
        </div>

        <h2 className="text-xs tracking-widest text-yellow-500 mt-6">// TOOL_STATUS</h2>
        <div className="flex flex-wrap gap-2">
          {["subfinder", "httpx", "nuclei", "amass", "dnsx", "ffuf", "gowitness", "whatweb"].map(tool => (
            <span key={tool} className="px-2.5 py-1 bg-black/50 border border-green-500/20 rounded-xl text-xs text-green-400">
              {tool}
            </span>
          ))}
        </div>

        <h2 className="text-xs tracking-widest text-blue-500 mt-6">// SESSION_STATS</h2>
        <div className="grid grid-cols-2 gap-4">
          {[
            {title: "Targets", value: "150", color: "blue", icon: Database}, 
            {title: "Assets", value: "95", color: "green", icon: Server}, 
            {title: "Findings", value: "42", icon: AlertTriangle, color: "red"}, 
            {title: "Risk Score", value: "88%", icon: Cpu, color: "yellow"}
          ].map((s, i) => (
            <StatCard key={i} label={s.title} value={s.value} icon={s.icon || Activity} color={s.color} />
          ))}
        </div>
      </aside>

      {/* CENTER PANEL */}
      <main className="col-span-12 md:col-span-7 flex flex-col gap-6">
        {/* Dynamically render LogStream and AIChat passed as children */}
        {React.Children.map(children, child => child?.type?.name === 'LogStream' && child)}
        {React.Children.map(children, child => child?.type?.name === 'AIChat' && child)}
      </main>

      {/* RIGHT PANEL (Desktop) */}
      <aside className="hidden md:flex md:col-span-3 flex-col gap-6">
        <GlassCard className="p-6 flex-1">
          <h2 className="text-xs tracking-widest text-cyan-500 mb-4">// ASSET_INVENTORY</h2>
          <div className="space-y-3">
            {assets.length > 0 ? assets.map((a, i) => (
              <div key={i} className="flex justify-between items-center text-sm">
                <span>{a.domain}</span>
                <span className={`px-2 py-1 rounded-full text-[10px] font-bold uppercase ${a.status === 'LIVE' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                  {a.status}
                </span>
              </div>
            )) : <div className="text-center text-gray-500 italic py-8">No assets discovered yet.</div>}
          </div>
        </GlassCard>
        <GlassCard className="p-6 flex-1">
          <h2 className="text-xs tracking-widest text-red-500 mb-4">// FINDINGS</h2>
          <div className="space-y-2">
            {findings.length > 0 ? findings.map(f => <FindingRow key={f.id} finding={f} />) : <div className="text-center text-gray-500 italic py-8">No critical findings.</div>}
          </div>
        </GlassCard>
      </aside>
    </div>
  );
};

export default SOCLayout;
