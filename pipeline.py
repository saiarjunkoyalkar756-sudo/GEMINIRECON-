import asyncio
from agents.recon_agents import SubdomainAgent, ScreenshotAgent, VulnerabilityAgent

async def run_pro_pipeline(target):
    print(f"[*] Starting PRO Pipeline for {target}")
    
    # 1. Subdomains
    sub_agent = SubdomainAgent()
    await sub_agent.run(target)
    
    # 2. Screenshots (Visual Recon)
    shot_agent = ScreenshotAgent()
    await shot_agent.run(target)
    
    # 3. Vuln Scan & Fuzzing
    vuln_agent = VulnerabilityAgent()
    await vuln_agent.run(target)
    
    print(f"[+] PRO Recon Complete. Results in results/{target}/")

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "example.in"
    asyncio.run(run_pro_pipeline(target))
