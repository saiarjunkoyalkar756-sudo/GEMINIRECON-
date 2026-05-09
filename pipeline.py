import asyncio
from agents.recon_agents import SubdomainAgent, PortScanAgent, VulnerabilityAgent, ReportAgent

async def run_pipeline(target):
    print(f"[*] Starting Pipeline for {target}")
    
    # Initialize Agents
    sub_agent = SubdomainAgent()
    port_agent = PortScanAgent()
    vuln_agent = VulnerabilityAgent()
    rep_agent = ReportAgent()
    
    # Execute Pipeline
    subs = await sub_agent.run(target)
    ports = await port_agent.run(target)
    vulns = await vuln_agent.run(target)
    
    # Final Report
    report = await rep_agent.generate(target, [subs, ports, vulns])
    print(f"[+] {report}")

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "example.com"
    asyncio.run(run_pipeline(target))
