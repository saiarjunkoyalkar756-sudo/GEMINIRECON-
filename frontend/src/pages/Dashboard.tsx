import React, { useEffect, useState, useMemo } from 'react';
import { 
  Shield, 
  Target, 
  Activity, 
  AlertTriangle, 
  Clock, 
  Play,
  Globe,
  Database,
  Code,
  WifiOff,
  Download,
  Search,
  Zap
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis,
  Tooltip, 
  ResponsiveContainer,
  Cell
} from 'recharts';
import LogStream from '../components/LogStream';

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
const WS_BASE = API_BASE.replace(/^http/, "ws");

const Dashboard = () => {
  const [scans, setScans] = useState([]);
  const [selectedScan, setSelectedScan] = useState(null);
  const [isApiUp, setIsApiUp] = useState(true);
  const [error, setError] = useState(null);
  const [selectedSkill, setSelectedSkill] = useState("subdomain_enumeration");

  const skills = [
    { id: "subdomain_enumeration", name: "Asset Discovery", icon: <Globe size={14}/> },
    { id: "bug_bounty_workflow", name: "Bug Bounty", icon: <Zap size={14}/> },
    { id: "vulnerability_scan", name: "Vuln Scan", icon: <Shield size={14}/> }
  ];

  const fetchScans = async () => {
    try {
      const response = await fetch(`${API_BASE}/scans/`);
      if (!response.ok) throw new Error(`API Error: ${response.status}`);
      const data = await response.json();
      
      if (Array.isArray(data)) {
        setScans(data);
        setIsApiUp(true);
        setError(null);
        if (!selectedScan && data.length > 0) setSelectedScan(data[0]);
        if (selectedScan) {
          const updated = data.find(s => s.id === selectedScan.id);
          if (updated) setSelectedScan(updated);
        }
      }
    } catch (err) {
      setIsApiUp(false);
      setError(err.message);
    }
  };

  useEffect(() => {
    fetchScans();
    const interval = setInterval(fetchScans, 5000);
    return () => clearInterval(interval);
  }, []);

  const stats = useMemo(() => {
    const s = { total: scans.length, running: 0, completed: 0, failed: 0 };
    scans.forEach(scan => {
      const status = (scan.status || 'pending').toLowerCase();
      if (s.hasOwnProperty(status)) s[status]++;
    });
    return s;
  }, [scans]);

  const startNewScan = async () => {
    const url = prompt("Enter target URL (e.g., example.com):");
    if (!url) return;
    try {
      const resp = await fetch(`${API_BASE}/scans/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          target_url: url, 
          workflow_type: selectedSkill,
          options: { full_recon: true } 
        })
      });
      if (!resp.ok) throw new Error("Failed to start scan");
      fetchScans();
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  const vulnData = [
    { name: 'Critical', value: 4, color: '#ef4444' },
    { name: 'High', value: 7, color: '#f97316' },
    { name: 'Medium', value: 12, color: '#facc15' },
    { name: 'Low', value: 20, color: '#3b82f6' },
  ];

  return (
    <div className="p-6 bg-[#0a0a0b] min-h-screen text-slate-200 font-sans selection:bg-blue-500/30">
      {/* Header */}
      <div className="flex justify-between items-center mb-8 bg-[#131316] p-4 rounded-xl border border-slate-800/50">
        <div>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent flex items-center gap-3">
            <Shield className="text-blue-500" /> GEMINI-RECON
          </h1>
          <p className="text-[10px] text-slate-500 uppercase tracking-[0.2em] font-bold mt-1">Autonomous Reconnaissance Platform v2.0</p>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="flex bg-black/40 p-1 rounded-lg border border-slate-800">
            {skills.map(skill => (
              <button
                key={skill.id}
                onClick={() => setSelectedSkill(skill.id)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                  selectedSkill === skill.id ? 'bg-blue-600 text-white shadow-lg' : 'text-slate-500 hover:text-slate-300'
                }`}
              >
                {skill.icon} {skill.name}
              </button>
            ))}
          </div>
          <button 
            onClick={startNewScan}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-lg font-bold text-sm shadow-lg shadow-blue-900/20 transition-all active:scale-95"
          >
            <Play size={16} fill="currentColor" /> INITIATE SCAN
          </button>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-6 mb-8">
        <StatCard title="Total Assets" value={stats.total} icon={<Globe className="text-blue-500" />} />
        <StatCard title="Active Jobs" value={stats.running} icon={<Activity className="text-green-500" />} />
        <StatCard title="Vulnerabilities" value="43" icon={<AlertTriangle className="text-red-500" />} />
        <StatCard title="System Health" value={isApiUp ? "Online" : "Offline"} icon={<Shield className={isApiUp ? "text-blue-500" : "text-red-500"} />} />
      </div>

      <div className="grid grid-cols-12 gap-8">
        <div className="col-span-8 space-y-6">
          {selectedScan ? (
            <>
              <div className="grid grid-cols-2 gap-6">
                <LogStream scanId={selectedScan.id} />
                <div className="bg-[#131316] border border-slate-800 rounded-xl p-6 flex flex-col">
                  <h3 className="text-sm font-semibold mb-4 text-slate-400 uppercase tracking-wider flex items-center gap-2">
                    <AlertTriangle size={16} className="text-yellow-500" /> Vulnerability Distribution
                  </h3>
                  <div className="flex-1 min-h-[200px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={vulnData}>
                        <XAxis dataKey="name" stroke="#475569" fontSize={10} tickLine={false} axisLine={false} />
                        <Tooltip 
                          contentStyle={{ backgroundColor: '#1a1a1e', border: '1px solid #334155', borderRadius: '8px', fontSize: '12px' }}
                          itemStyle={{ color: '#f8fafc' }}
                        />
                        <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                          {vulnData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>

              <div className="bg-[#131316] border border-slate-800 rounded-xl p-6 shadow-xl">
                <div className="flex justify-between items-center mb-6">
                  <h3 className="text-lg font-semibold flex items-center gap-2">
                    <Code size={20} className="text-blue-400"/> AI ANALYTICS & INSIGHTS
                  </h3>
                  <button className="text-[10px] font-bold uppercase tracking-widest flex items-center gap-2 bg-slate-800 px-3 py-1.5 rounded hover:bg-slate-700 transition-colors">
                    <Download size={12}/> Export Intelligence
                  </button>
                </div>
                <div className="text-slate-300 text-sm leading-relaxed p-5 rounded-lg bg-black/40 border border-slate-800/50 min-h-[150px] whitespace-pre-wrap font-mono">
                  {selectedScan.results_summary || (
                    <div className="flex flex-col items-center justify-center py-12 text-slate-600">
                      <Search size={32} className="mb-4 opacity-20" />
                      <p>Awaiting engine analysis results...</p>
                    </div>
                  )}
                </div>
              </div>
            </>
          ) : (
            <div className="h-[600px] flex flex-col items-center justify-center border border-dashed border-slate-800 rounded-2xl text-slate-600 bg-black/20">
              <Shield size={48} className="mb-4 opacity-10" />
              <p className="font-medium">No Scan Selected</p>
              <p className="text-sm opacity-50">Select a job from the history or start a new reconnaissance mission.</p>
            </div>
          )}
        </div>

        <div className="col-span-4 bg-[#131316] border border-slate-800 rounded-xl overflow-hidden shadow-2xl">
          <div className="p-4 border-b border-slate-800 bg-[#1a1a1e] flex items-center justify-between">
            <h2 className="font-bold text-sm tracking-tight flex items-center gap-2">
              <Clock size={16} className="text-blue-500" /> MISSION HISTORY
            </h2>
            <span className="text-[10px] bg-blue-500/10 text-blue-400 px-2 py-0.5 rounded border border-blue-500/20">{scans.length} Total</span>
          </div>
          <div className="max-h-[750px] overflow-y-auto custom-scrollbar">
            {scans.length === 0 ? (
              <div className="p-12 text-center text-slate-600 text-sm italic">No history available.</div>
            ) : scans.map(scan => (
              <div 
                key={scan.id} 
                onClick={() => setSelectedScan(scan)}
                className={`p-4 border-b border-slate-800/50 cursor-pointer transition-all ${
                  selectedScan?.id === scan.id ? 'bg-blue-900/20 border-l-4 border-l-blue-500' : 'hover:bg-slate-800/50'
                }`}
              >
                <div className="flex justify-between items-start mb-1">
                  <div className="font-bold text-sm truncate max-w-[180px]">{scan.target_id || "Target Domain"}</div>
                  <StatusBadge status={scan.status} />
                </div>
                <div className="flex justify-between items-center text-[10px] text-slate-500 uppercase font-bold tracking-tighter">
                  <span>{scan.skill || "Full Recon"}</span>
                  <span>{new Date(scan.start_time).toLocaleTimeString()}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

const StatCard = ({ title, value, icon }) => (
  <div className="bg-[#131316] border border-slate-800 p-5 rounded-xl hover:border-slate-700 transition-colors group">
    <div className="flex justify-between mb-3">
      <span className="text-slate-500 text-[10px] uppercase font-bold tracking-widest">{title}</span>
      <div className="p-2 bg-black/40 rounded-lg group-hover:scale-110 transition-transform">
        {icon}
      </div>
    </div>
    <div className="text-2xl font-black text-slate-100">{value}</div>
  </div>
);

const StatusBadge = ({ status }) => {
  const styles = {
    completed: "bg-green-500/10 text-green-500 border-green-500/20",
    running: "bg-blue-500/10 text-blue-500 border-blue-500/20 animate-pulse",
    failed: "bg-red-500/10 text-red-500 border-red-500/20",
    pending: "bg-slate-500/10 text-slate-500 border-slate-500/20"
  };
  const current = styles[status?.toLowerCase()] || styles.pending;
  return (
    <span className={`text-[9px] font-black uppercase tracking-tighter px-2 py-0.5 rounded border ${current}`}>
      {status}
    </span>
  );
};

export default Dashboard;
