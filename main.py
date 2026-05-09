import sys
import asyncio
import argparse
from dashboard.tui import ReconApp
from core.storage.database import init_db
from agents.orchestrator import ReconOrchestrator
from core.utils.tool_executor import set_tool_callback

async def run_cli(target):
    print(f"[*] Initializing GEMINIRECON CLI for target: {target}")
    
    async def callback(msg):
        print(f"[-] {msg}")

    # Set tool execution callback to see real-time tool logs
    set_tool_callback(callback)
    
    # Initialize database
    await init_db()
    
    orchestrator = ReconOrchestrator()
    
    try:
        results = await orchestrator.run_recon_workflow(target, callback=callback)
        print("\n" + "="*50)
        print(f"RECON REPORT: {target}")
        print("="*50)
        print(f"\n[ANALYSIS]\n{results['analysis']}")
        print(f"\n[RISK ASSESSMENT]\n{results['risk']}")
        print(f"\n[ASSETS]")
        for asset in results['assets']:
            val = asset.get('value') or asset.get('domain')
            print(f"- {val} ({asset.get('type', 'unknown')})")
    except Exception as e:
        print(f"[!] Error: {e}")

async def run_tui():
    await init_db()
    app = ReconApp()
    await app.run_async()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GEMINIRECON - AI-Powered Recon Framework")
    parser.add_argument("--target", help="Target domain or instruction for recon")
    parser.add_argument("--tui", action="store_true", help="Launch TUI (default)")
    
    args = parser.parse_args()
    
    if args.target:
        asyncio.run(run_cli(args.target))
    else:
        asyncio.run(run_tui())
