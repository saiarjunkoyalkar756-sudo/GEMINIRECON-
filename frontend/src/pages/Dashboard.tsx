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
  Download
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  Tooltip, 
  ResponsiveContainer,
  Cell
} from 'recharts';
import LogStream from '../components/LogStream';

const API_BASE = "http://localhost:8000";

const Dashboard = () => {
  const [scans, setScans] = useState([]);
  const [selectedScan, setSelectedScan] = useState(null);
  const [isApiUp, setIsApiUp] = useState(true);
  const [error, setError] = useState(null);

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
        // Update selectedScan if already set (to get latest data)
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
    const interval = setInterval(fetchScans, 3000);
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
    const url = prompt("Enter target URL:");
    if (!url) return;
    try {
      const resp = await fetch(`${API_BASE}/scans/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target_url: url, options: { full_recon: true } })
      });
      if (!resp.ok) throw new Error("Failed to start scan");
      fetchScans();
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  const downloadReport = (scanId) => {
    window.open(`${API_BASE}/scans/${scanId}/report`, '_blank');
  };

  return (
    <div className="p-6 bg-[#0a0a0b] min-h-screen text-slate-200 font-sans">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent flex items-center gap-3">
            <Shield className="text-blue-500" /> GEMINIRECON
          </h1>
        </div>
        <button 
          onClick={startNewScan}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-lg font-semibold"
        >
          <Play size={18} fill="currentColor" /> Scan Target
        </button>
      </div>

      <div className="grid grid-cols-4 gap-6 mb-8">
        <StatCard title="Total Scans" value={stats.total} icon={<Globe />} />
        <StatCard title="Running" value={stats.running} icon={<Activity />} />
        <StatCard title="Completed" value={stats.completed} icon={<Shield />} />
        <StatCard title="Failed" value={stats.failed} icon={<AlertTriangle />} />
      </div>

      <div className="grid grid-cols-3 gap-8">
        <div className="col-span-2 space-y-6">
          {selectedScan ? (
            <>
              <LogStream scanId={selectedScan.id} />
              <div className="bg-[#131316] border border-slate-800 rounded-xl p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold flex items-center gap-2"><Code size={20}/> AI Report</h3>
                  {selectedScan.status === 'completed' && (
                    <button onClick={() => downloadReport(selectedScan.id)} className="text-xs flex items-center gap-2 bg-slate-800 px-3 py-1 rounded hover:bg-slate-700">
                      <Download size={14}/> PDF Report
                    </button>
                  )}
                </div>
                <div className="text-slate-400 text-sm p-4 rounded-lg bg-black/40 min-h-[100px] whitespace-pre-wrap font-mono">
                  {selectedScan.results_summary || "Waiting for analysis..."}
                </div>
              </div>
            </>
          ) : (
            <div className="h-[400px] flex items-center justify-center border border-dashed border-slate-800 rounded-xl text-slate-600">Select a scan</div>
          )}
        </div>

        <div className="bg-[#131316] border border-slate-800 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-slate-800 bg-[#1a1a1e] font-bold">Scan History</div>
          <div className="max-h-[600px] overflow-y-auto">
            {scans.map(scan => (
              <div 
                key={scan.id} 
                onClick={() => setSelectedScan(scan)}
                className={`p-4 border-b border-slate-800 cursor-pointer ${selectedScan?.id === scan.id ? 'bg-blue-900/20' : 'hover:bg-slate-800'}`}
              >
                <div className="font-medium">{scan.target_id}</div>
                <div className="text-xs text-slate-500">{scan.status} • {new Date(scan.start_time).toLocaleTimeString()}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

const StatCard = ({ title, value, icon }) => (
  <div className="bg-[#131316] border border-slate-800 p-6 rounded-xl">
    <div className="flex justify-between mb-2">
      <span className="text-slate-400 text-sm">{title}</span>
      {icon}
    </div>
    <div className="text-2xl font-bold">{value}</div>
  </div>
);

export default Dashboard;
