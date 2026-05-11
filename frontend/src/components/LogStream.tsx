import React, { useState, useEffect, useRef } from 'react';
import { Terminal, Shield, AlertCircle, Clock } from 'lucide-react';

const LogStream = ({ scanId }) => {
  const [logs, setLogs] = useState([]);
  const ws = useRef(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    if (!scanId) return;

    const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
    const WS_BASE = API_BASE.replace(/^http/, "ws");
    ws.current = new WebSocket(`${WS_BASE}/ws/scans/${scanId}`);

    ws.current.onmessage = (event) => {
      try {
        const log = JSON.parse(event.data);
        if (log.type === "log") {
          setLogs((prev) => [...prev, {
            timestamp: new Date().toISOString(),
            level: log.level,
            message: log.message
          }]);
        }
      } catch (e) {
        console.error("Failed to parse log", e);
      }
    };

    return () => {
      if (ws.current) ws.current.close();
    };
  }, [scanId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  return (
    <div className="bg-[#0f0f12] border border-slate-800 rounded-xl overflow-hidden flex flex-col h-[400px]">
      <div className="bg-[#1a1a1e] px-4 py-2 border-b border-slate-800 flex items-center justify-between">
        <h3 className="text-sm font-semibold flex items-center gap-2 text-slate-300">
          <Terminal size={16} className="text-blue-500" /> Live Scan Engine Logs
        </h3>
        <span className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">Scanning in progress...</span>
      </div>
      <div className="flex-1 overflow-y-auto p-4 font-mono text-xs space-y-1.5 custom-scrollbar">
        {logs.map((log, i) => (
          <div key={i} className="flex gap-3 animate-in fade-in slide-in-from-left-2 duration-300">
            <span className="text-slate-600">[{new Date(log.timestamp).toLocaleTimeString()}]</span>
            <span className={`font-bold ${
              log.level === 'ERROR' ? 'text-red-500' : 
              log.level === 'WARNING' ? 'text-yellow-500' : 
              'text-blue-400'
            }`}>
              {log.level}
            </span>
            <span className="text-slate-300">{log.message}</span>
          </div>
        ))}
        {logs.length === 0 && (
          <div className="text-slate-600 italic">Waiting for logs...</div>
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
};

export default LogStream;
