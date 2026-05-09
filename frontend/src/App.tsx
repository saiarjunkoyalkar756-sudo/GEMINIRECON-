import React, { useState, useEffect, useRef } from 'react';
import { 
  Shield, 
  Search, 
  LayoutDashboard, 
  Globe, 
  Zap, 
  History, 
  Settings, 
  AlertTriangle, 
  Database, 
  Activity,
  ChevronRight,
  Terminal,
  Cpu,
  Eye,
  Server,
  Layers,
  Code,
  Lock,
  ExternalLink
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const Sidebar = ({ activeTab, setActiveTab }: any) => {
  const menuItems = [
    { id: 'dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { id: 'recon', icon: Globe, label: 'Active Recon' },
    { id: 'assets', icon: Database, label: 'Asset Inventory' },
    { id: 'history', icon: History, label: 'Scan History' },
    { id: 'settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <div className="w-64 h-screen border-r border-border bg-card/50 flex flex-col">
      <div className="p-6 flex items-center gap-3">
        <div className="p-2 rounded-lg recon-gradient">
          <Shield className="w-6 h-6 text-white" />
        </div>
        <span className="font-bold text-xl tracking-tight">GEMINIRECON</span>
      </div>
      
      <nav className="flex-1 px-4 space-y-2 mt-4">
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
              activeTab === item.id 
                ? 'bg-primary text-white shadow-lg shadow-primary/20' 
                : 'text-muted-foreground hover:bg-muted hover:text-foreground'
            }`}
          >
            <item.icon className="w-5 h-5" />
            <span className="font-medium">{item.label}</span>
          </button>
        ))}
      </nav>
      
      <div className="p-4 border-t border-border">
        <div className="bg-muted/50 rounded-xl p-4 flex items-center gap-3">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          <span className="text-xs font-medium text-muted-foreground">API CONNECTED</span>
        </div>
      </div>
    </div>
  );
};

const StatCard = ({ label, value, icon: Icon, color }: any) => (
  <motion.div 
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    className="glass p-6 rounded-2xl flex flex-col gap-4 hover:border-primary/50 transition-colors"
  >
    <div className="flex items-center justify-between">
      <span className="text-sm font-medium text-muted-foreground">{label}</span>
      <div className={`p-2 rounded-lg ${color}`}>
        <Icon className="w-5 h-5 text-white" />
      </div>
    </div>
    <div className="text-3xl font-bold tracking-tight">{value}</div>
  </motion.div>
);

const AssetRow = ({ asset }: any) => (
  <tr className="border-b border-border hover:bg-muted/30 transition-colors group">
    <td className="py-4 px-6">
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-lg bg-muted text-primary group-hover:bg-primary/10 transition-colors">
          <Globe className="w-4 h-4" />
        </div>
        <span className="font-medium">{asset.domain}</span>
      </div>
    </td>
    <td className="py-4 px-6 text-muted-foreground">{asset.ip || 'N/A'}</td>
    <td className="py-4 px-6">
      <div className="flex gap-2 flex-wrap">
        {asset.tech && asset.tech.map((t: string) => (
          <span key={t} className="px-2 py-1 rounded-md bg-primary/10 text-primary text-[10px] font-bold uppercase tracking-wider">
            {t}
          </span>
        ))}
      </div>
    </td>
    <td className="py-4 px-6">
      <span className={`px-2 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${
        asset.status === 'Live' ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'
      }`}>
        {asset.status || 'Unknown'}
      </span>
    </td>
    <td className="py-4 px-6 text-right">
      <ExternalLink className="w-4 h-4 text-muted-foreground hover:text-primary transition-colors cursor-pointer" />
    </td>
  </tr>
);

const App = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [target, setTarget] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  const [logs, setLogs] = useState<any[]>([]);
  const [assets, setAssets] = useState<any[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [chatMessages, setChatMessages] = useState<any[]>([]);
  const [stats, setStats] = useState({
    assets: 0,
    risks: 0,
    services: 0,
    insights: 0
  });
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws.current = new WebSocket(`${protocol}//${window.location.host}/ws`);
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'log') {
        setLogs(prev => [...prev, { time: new Date().toLocaleTimeString(), message: data.data }]);
      } else if (data.type === 'complete') {
        setIsScanning(false);
        setLogs(prev => [...prev, { time: new Date().toLocaleTimeString(), message: "RECON COMPLETED SUCCESSFULLY", type: 'success' }]);
        
        const discoveredAssets = data.data.assets || [];
        if (discoveredAssets.length > 0) {
          setAssets(discoveredAssets);
          setStats(prev => ({
            ...prev,
            assets: discoveredAssets.length,
            services: discoveredAssets.reduce((acc: number, curr: any) => acc + (curr.tech ? curr.tech.length : 0), 0)
          }));
        }
        
        const riskText = (data.data.risk || "").toLowerCase();
        const riskCount = (riskText.match(/high|critical|medium/g) || []).length;
        setStats(prev => ({ ...prev, risks: riskCount, insights: 5 }));
        
        setChatMessages(prev => [...prev, { role: 'assistant', content: "Reconnaissance complete. I've updated the dashboard with my findings. What would you like to analyze further?" }]);
      } else if (data.type === 'error') {
        setIsScanning(false);
        setLogs(prev => [...prev, { time: new Date().toLocaleTimeString(), message: `ERROR: ${data.data}`, type: 'error' }]);
      }
    };
    return () => ws.current?.close();
  }, []);

  const handleStartRecon = async (customTarget?: string) => {
    const targetToUse = customTarget || target;
    if (!targetToUse) return;
    
    setIsScanning(true);
    setAssets([]); 
    setLogs([{ time: new Date().toLocaleTimeString(), message: `Initializing recon workflow for ${targetToUse}...` }]);
    setStats({ assets: 0, risks: 0, services: 0, insights: 0 });
    
    setChatMessages(prev => [...prev, { role: 'user', content: `Start recon for ${targetToUse}` }]);
    
    try {
      await fetch('/api/recon', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target: targetToUse })
      });
    } catch (error) {
      setIsScanning(false);
      setLogs(prev => [...prev, { time: new Date().toLocaleTimeString(), message: `Error starting recon: ${error}`, type: 'error' }]);
    }
  };

  const handleChatSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim()) return;
    
    const input = chatInput.trim();
    setChatInput('');
    setChatMessages(prev => [...prev, { role: 'user', content: input }]);
    
    // Send command to backend via API for recon or via WS for chat
    if (input.toLowerCase().startsWith('scan ')) {
      const newTarget = input.split(' ')[1];
      setTarget(newTarget);
      handleStartRecon(newTarget);
    } else {
      // Send as chat message to websocket if connected
      if (ws.current && ws.current.readyState === WebSocket.OPEN) {
        ws.current.send(JSON.stringify({ type: 'chat', content: input }));
      } else {
        setTimeout(() => {
          setChatMessages(prev => [...prev, { role: 'assistant', content: "Backend disconnected. Commands not relayed." }]);
        }, 500);
      }
    }
  };

  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <main className="flex-1 flex flex-col overflow-auto font-sans">
        <header className="h-20 border-b border-border flex items-center justify-between px-8 bg-background/50 backdrop-blur-md sticky top-0 z-50">
          <div className="flex items-center gap-4 bg-muted/30 px-4 py-2.5 rounded-2xl border border-border w-[400px] focus-within:border-primary/50 transition-colors">
            <Search className="w-4 h-4 text-muted-foreground" />
            <input 
              type="text" 
              placeholder="Enter target domain or IP..." 
              value={target}
              onChange={(e) => setTarget(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleStartRecon()}
              className="bg-transparent border-none outline-none text-sm w-full"
            />
          </div>
          
          <button 
            onClick={() => handleStartRecon()}
            disabled={isScanning || !target}
            className={`flex items-center gap-2 px-8 py-2.5 rounded-2xl font-bold transition-all ${
              isScanning || !target 
                ? 'bg-muted text-muted-foreground cursor-not-allowed' 
                : 'recon-gradient text-white hover:opacity-90 shadow-lg shadow-primary/30 active:scale-95'
            }`}
          >
            {isScanning ? (
              <Zap className="w-4 h-4 animate-spin" />
            ) : (
              <Zap className="w-4 h-4" />
            )}
            {isScanning ? 'SCANNING...' : 'START RECON'}
          </button>
        </header>

        <div className="p-8 space-y-8 max-w-[1600px] mx-auto w-full">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatCard label="Discovered Assets" value={stats.assets} icon={Database} color="bg-blue-500" />
            <StatCard label="Critical Risks" value={stats.risks} icon={AlertTriangle} color="bg-red-500" />
            <StatCard label="Active Services" value={stats.services} icon={Activity} color="bg-green-500" />
            <StatCard label="AI Insights" value={stats.insights} icon={Cpu} color="bg-purple-500" />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            <div className="lg:col-span-8 space-y-8">
              <div className="glass rounded-3xl overflow-hidden shadow-2xl">
                <div className="p-6 border-b border-border flex items-center justify-between">
                  <h2 className="font-bold text-lg flex items-center gap-2">
                    <Layers className="w-5 h-5 text-primary" />
                    Asset Inventory
                  </h2>
                  <div className="text-xs text-muted-foreground uppercase tracking-widest font-bold">{assets.length} assets</div>
                </div>
                <div className="overflow-x-auto min-h-[300px]">
                  {assets.length > 0 ? (
                    <table className="w-full text-left">
                      <thead>
                        <tr className="bg-muted/50 text-[10px] font-bold uppercase tracking-widest text-muted-foreground border-b border-border">
                          <th className="py-4 px-6">Domain</th>
                          <th className="py-4 px-6">IP Address</th>
                          <th className="py-4 px-6">Technology</th>
                          <th className="py-4 px-6">Status</th>
                          <th className="py-4 px-6 text-right">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {assets.map((asset, i) => <AssetRow key={i} asset={asset} />)}
                      </tbody>
                    </table>
                  ) : (
                    <div className="py-32 text-center text-muted-foreground flex flex-col items-center gap-4">
                      <Database className="w-16 h-16 opacity-5" />
                      <p className="opacity-40 font-medium">No assets discovered yet.</p>
                    </div>
                  )}
                </div>
              </div>

              <div className="glass rounded-3xl overflow-hidden shadow-xl">
                <div className="border-b border-border p-6 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Terminal className="w-5 h-5 text-primary" />
                    <h2 className="font-bold text-lg">Live Recon Stream</h2>
                  </div>
                  <div className="flex gap-2">
                    <div className="w-3 h-3 rounded-full bg-red-500/20" />
                    <div className="w-3 h-3 rounded-full bg-yellow-500/20" />
                    <div className="w-3 h-3 rounded-full bg-green-500/20" />
                  </div>
                </div>
                <div className="p-6 font-mono text-xs space-y-1.5 h-[400px] overflow-y-auto bg-black/60 scrollbar-hide">
                  {logs.length === 0 ? (
                    <div className="text-muted-foreground italic flex flex-col items-center justify-center h-full gap-4">
                      <Eye className="w-12 h-12 opacity-5" />
                      <p className="opacity-40 font-medium tracking-tight">System idle. Initiate target scan.</p>
                    </div>
                  ) : (
                    logs.map((log, i) => (
                      <div key={i} className="flex gap-4 animate-in fade-in slide-in-from-left-1 duration-200">
                        <span className="text-muted-foreground opacity-30 select-none">[{log.time}]</span>
                        <span className={
                          log.type === 'success' ? 'text-green-400 font-bold' : 
                          log.type === 'error' ? 'text-red-400' : 'text-primary/90'
                        }>
                          {log.message}
                        </span>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>

            <div className="lg:col-span-4 space-y-8 flex flex-col h-full">
              <div className="glass rounded-3xl flex flex-col flex-1 min-h-[600px] overflow-hidden shadow-2xl">
                <div className="p-6 border-b border-border bg-card/50">
                  <h3 className="font-bold flex items-center gap-2">
                    <Cpu className="w-5 h-5 text-purple-500" />
                    AI Operator
                  </h3>
                </div>
                
                <div className="flex-1 p-6 overflow-y-auto space-y-4 text-sm scrollbar-hide">
                  {chatMessages.length === 0 && (
                    <div className="text-center py-20 space-y-4">
                      <div className="w-16 h-16 rounded-3xl bg-purple-500/10 flex items-center justify-center mx-auto text-purple-500 border border-purple-500/20 rotate-3">
                        <Cpu className="w-8 h-8" />
                      </div>
                      <p className="text-muted-foreground text-xs leading-relaxed max-w-[200px] mx-auto">
                        I am Gemini, your expert OSINT operator.<br/>
                        <span className="font-bold text-foreground">Command me:</span> "scan apple.com"
                      </p>
                    </div>
                  )}
                  {chatMessages.map((msg, i) => (
                    <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-[90%] p-4 rounded-2xl shadow-sm ${
                        msg.role === 'user' 
                          ? 'bg-primary text-white rounded-br-none' 
                          : 'bg-muted/80 border border-border text-foreground rounded-bl-none'
                      }`}>
                        {msg.content}
                      </div>
                    </div>
                  ))}
                </div>

                <form onSubmit={handleChatSubmit} className="p-4 border-t border-border bg-card/50">
                  <div className="relative group">
                    <input 
                      type="text" 
                      placeholder="Type a command..." 
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      className="w-full bg-background border border-border rounded-2xl px-5 py-4 pr-14 text-sm focus:border-primary/50 outline-none transition-all shadow-inner"
                    />
                    <button type="submit" className="absolute right-2 top-1/2 -translate-y-1/2 p-2.5 text-primary hover:bg-primary/10 rounded-xl transition-all">
                      <ChevronRight className="w-6 h-6" />
                    </button>
                  </div>
                </form>
              </div>

              <div className="glass rounded-3xl p-6 shadow-lg">
                <h3 className="font-bold mb-6 flex items-center gap-2">
                  <Code className="w-5 h-5 text-orange-500" />
                  Detected Stack
                </h3>
                <div className="flex flex-wrap gap-2">
                  {assets.length > 0 ? (
                    Array.from(new Set(assets.flatMap(a => a.tech || []))).map(tech => (
                      <span key={tech} className="px-3 py-1.5 rounded-xl bg-primary/5 text-primary text-[11px] font-bold border border-primary/10 hover:border-primary/40 transition-colors cursor-default">
                        {tech}
                      </span>
                    ))
                  ) : (
                    <div className="w-full text-center py-4 border border-dashed border-border rounded-2xl">
                      <span className="text-[10px] text-muted-foreground font-bold uppercase tracking-widest opacity-50">Stack empty</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default App;
