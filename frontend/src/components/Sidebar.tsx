import React from 'react';
import { Shield, Search, LayoutDashboard, Globe, Zap, History, Settings, AlertTriangle, Database, Activity, ChevronRight, Terminal, Cpu, Eye, Layers, Code, ExternalLink, Clock } from 'lucide-react';

const Sidebar = ({ activeTab, setActiveTab }: any) => {
  const menuItems = [
    { id: 'dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { id: 'recon', icon: Shield, label: 'Recon Monitoring' },
    { id: 'findings', icon: AlertTriangle, label: 'Vulnerability Findings' },
    { id: 'assets', icon: Database, label: 'Asset Inventory' },
    { id: 'scan-history', icon: History, label: 'Live Scans' },
    { id: 'ai-analysis', icon: Cpu, label: 'AI Analysis' },
    { id: 'settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <aside className="w-[220px] border-r border-gray-800 p-6 flex flex-col gap-8 bg-[#0a0a0c]/80">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-green-400 to-blue-500 flex items-center justify-center animate-pulse">
          <Shield className="w-5 h-5 text-black" />
        </div>
        <h1 className="text-lg font-bold text-green-400">GEMINIRECON</h1>
      </div>
      
      <nav className="flex-1 flex flex-col gap-3">
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            className={`flex items-center gap-3 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === item.id 
                ? 'bg-purple-600 text-white shadow-md shadow-purple-500/30' 
                : 'text-gray-400 hover:bg-gray-800 hover:text-white'
            }`}
          >
            <item.icon className="w-4 h-4" />
            {item.label}
          </button>
        ))}
      </nav>
      
      <div className="border-t border-gray-800 pt-4 mt-auto">
        <h2 className="text-xs tracking-widest text-gray-500 mb-3">// TOOL STATUS</h2>
        <div className="flex flex-wrap gap-2">
          {["subfinder", "httpx", "nuclei", "amass", "dnsx", "ffuf", "gowitness", "whatweb"].map(tool => (
            <span key={tool} className="px-2.5 py-1 bg-black/50 border border-green-500/20 rounded-xl text-xs text-green-400">
              {tool}
            </span>
          ))}
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
