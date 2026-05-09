'use client'

import { useState, useEffect, useRef } from 'react'
import { useStore } from '@/store'
import { Search, ShieldAlert, Terminal, Loader2, Globe, Activity, Database, Server } from 'lucide-react'

export function ReconArea() {
  const {
    reconActiveTarget,
    reconLogs,
    reconResults,
    isReconLoading,
    setReconActiveTarget,
    addReconLog,
    setReconResults,
    setIsReconLoading,
    clearRecon,
    ultraplinianApiUrl,
    ultraplinianApiKey
  } = useStore()

  const [targetInput, setTargetInput] = useState('')
  const logEndRef = useRef<HTMLDivElement>(null)

  // Scroll to bottom of logs
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [reconLogs])

  const startRecon = async () => {
    if (!targetInput) return
    
    clearRecon()
    setReconActiveTarget(targetInput)
    setIsReconLoading(true)
    addReconLog(`[SYSTEM] Initializing reconnaissance mission for ${targetInput}...`)

    try {
      // Connect to the unified G0DM0D3 API which proxies to GEMINIRECON
      const response = await fetch(`${ultraplinianApiUrl}/v1/recon/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${ultraplinianApiKey}`
        },
        body: JSON.stringify({ target: targetInput })
      })

      if (!response.ok) {
        throw new Error('Failed to start recon')
      }

      addReconLog(`[SYSTEM] Mission started. Listening for live intelligence...`)
      
      // Setup WebSocket for real-time logs (connecting to GEMINIRECON directly for speed)
      // In a production setup, G0DM0D3 API would proxy this WebSocket too.
      const ws = new WebSocket(`ws://${new URL(ultraplinianApiUrl).hostname}:8000/ws`)
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        if (data.type === 'log') {
          addReconLog(`[RECON] ${data.data}`)
        } else if (data.type === 'complete') {
          addReconLog(`[SYSTEM] Mission complete. Analysis synchronized.`)
          setReconResults(data.data)
          setIsReconLoading(false)
          ws.close()
        } else if (data.type === 'error') {
          addReconLog(`[ERROR] ${data.data}`)
          setIsReconLoading(false)
          ws.close()
        }
      }

      ws.onerror = () => {
        addReconLog(`[ERROR] Intelligence stream interrupted.`)
        setIsReconLoading(false)
      }

    } catch (err: any) {
      addReconLog(`[ERROR] Connection failed: ${err.message}`)
      setIsReconLoading(false)
    }
  }

  return (
    <div className="flex-1 flex flex-col h-full bg-theme-bg overflow-hidden p-6 gap-6">
      {/* Target Input Area */}
      <div className="theme-dim border border-theme-primary rounded-xl p-6 shadow-glow">
        <div className="flex items-center gap-4 mb-4">
          <ShieldAlert className="w-8 h-8 theme-primary animate-pulse" />
          <div>
            <h2 className="text-xl font-bold theme-primary tracking-wider uppercase">Attack Surface Intelligence</h2>
            <p className="text-xs theme-secondary opacity-70">Powered by GEMINIRECON & G0DM0D3</p>
          </div>
        </div>

        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 theme-secondary" />
            <input
              type="text"
              value={targetInput}
              onChange={(e) => setTargetInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && startRecon()}
              placeholder="Enter target domain (e.g., example.com)"
              className="w-full bg-theme-accent/30 border border-theme-primary/50 rounded-lg py-3 pl-10 pr-4
                focus:border-theme-primary focus:glow-box outline-none transition-all font-mono text-sm"
              disabled={isReconLoading}
            />
          </div>
          <button
            onClick={startRecon}
            disabled={isReconLoading || !targetInput}
            className={`
              px-8 py-3 rounded-lg font-bold uppercase tracking-widest text-sm transition-all
              ${isReconLoading || !targetInput
                ? 'bg-theme-accent/20 border border-theme-primary/20 text-theme-secondary cursor-not-allowed'
                : 'bg-theme-primary text-black hover:glow-box'
              }
            `}
          >
            {isReconLoading ? (
              <div className="flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Scanning</span>
              </div>
            ) : (
              'Initialize'
            )}
          </button>
        </div>
      </div>

      <div className="flex-1 flex gap-6 overflow-hidden">
        {/* Terminal Logs */}
        <div className="flex-[2] flex flex-col bg-black border border-theme-primary/30 rounded-xl overflow-hidden shadow-inner">
          <div className="bg-theme-accent/30 border-b border-theme-primary/30 px-4 py-2 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Terminal className="w-4 h-4 theme-primary" />
              <span className="text-xs font-mono uppercase tracking-widest opacity-80">Intelligence Stream</span>
            </div>
            {reconActiveTarget && (
              <div className="flex items-center gap-2">
                <Activity className="w-3 h-3 text-green-500 animate-ping" />
                <span className="text-[10px] font-mono theme-primary">{reconActiveTarget}</span>
              </div>
            )}
          </div>
          <div className="flex-1 overflow-y-auto p-4 font-mono text-xs space-y-1 custom-scrollbar">
            {reconLogs.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center opacity-30 text-center px-10">
                <Skull className="w-12 h-12 mb-4" />
                <p>Awaiting Target Initialization...</p>
                <p className="text-[10px] mt-2">No active reconnaissance missions detected in this sector.</p>
              </div>
            ) : (
              reconLogs.map((log, i) => (
                <div key={i} className={`
                  ${log.startsWith('[SYSTEM]') ? 'theme-primary' : ''}
                  ${log.startsWith('[ERROR]') ? 'text-red-500' : ''}
                  ${log.startsWith('[RECON]') ? 'theme-secondary' : ''}
                  opacity-90 leading-relaxed
                `}>
                  <span className="opacity-50 mr-2">[{new Date().toLocaleTimeString()}]</span>
                  {log}
                </div>
              ))
            )}
            <div ref={logEndRef} />
          </div>
        </div>

        {/* Results Panel */}
        <div className="flex-1 flex flex-col gap-6 overflow-hidden">
          {/* Asset List */}
          <div className="flex-1 theme-dim border border-theme-primary/30 rounded-xl overflow-hidden flex flex-col">
            <div className="bg-theme-accent/20 border-b border-theme-primary/30 px-4 py-3 flex items-center gap-2">
              <Database className="w-4 h-4 theme-primary" />
              <span className="text-xs font-bold uppercase tracking-widest">Discovered Assets</span>
            </div>
            <div className="flex-1 overflow-y-auto p-2 custom-scrollbar">
              {!reconResults?.assets || reconResults.assets.length === 0 ? (
                <div className="h-full flex items-center justify-center opacity-30 text-[10px] text-center p-4">
                  No assets identified yet
                </div>
              ) : (
                <div className="space-y-2">
                  {reconResults.assets.map((asset: any, i: number) => (
                    <div key={i} className="bg-theme-accent/10 border border-theme-primary/10 rounded p-2 hover:bg-theme-accent/20 transition-all">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-bold theme-primary truncate max-w-[150px]">{asset.domain || asset.ip}</span>
                        <span className={`text-[10px] px-1 rounded ${asset.status === 'Live' ? 'bg-green-900/50 text-green-400' : 'bg-red-900/50 text-red-400'}`}>
                          {asset.status}
                        </span>
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {asset.tech?.map((t: string, j: number) => (
                          <span key={j} className="text-[8px] bg-theme-primary/10 theme-secondary px-1 border border-theme-primary/20">
                            {t}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Analysis Summary */}
          <div className="flex-1 theme-dim border border-theme-primary/30 rounded-xl overflow-hidden flex flex-col">
            <div className="bg-theme-accent/20 border-b border-theme-primary/30 px-4 py-3 flex items-center gap-2">
              <Server className="w-4 h-4 theme-primary" />
              <span className="text-xs font-bold uppercase tracking-widest">Model Analysis</span>
            </div>
            <div className="flex-1 overflow-y-auto p-4 custom-scrollbar text-[11px] leading-relaxed theme-secondary">
              {!reconResults?.analysis ? (
                <div className="h-full flex items-center justify-center opacity-30 text-[10px] text-center p-4">
                  Synthesis pending complete intelligence gathering
                </div>
              ) : (
                <div className="whitespace-pre-wrap font-mono">
                  {reconResults.analysis}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
