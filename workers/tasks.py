import asyncio
from core.storage.database import AsyncSessionLocal
from core.storage.models import ScanJob, JobStatus, Vulnerability, Target, Asset, Technology, CVE, Finding, Severity, ScanLog
from scanners.subfinder import SubfinderScanner
from scanners.nmap import NmapScanner
from scanners.nuclei import NucleiScanner
from modules.web_fetch import WebFetchEngine
from modules.tech_detector import TechDetector
from modules.cve_engine import CVEEngine
from modules.js_analyzer import JSAnalyzer
from analyzers.ai_analyzer import AIAnalyzer
from sqlalchemy import select, update
from datetime import datetime
import json

async def log_to_db(db, scan_job_id, level, message):
    new_log = ScanLog(scan_job_id=scan_job_id, level=level, message=message)
    db.add(new_log)
    await db.commit()
    print(f"[{level}] {message}")

async def run_full_recon_pipeline(scan_job_id, target_url, scan_plan):
    async with AsyncSessionLocal() as db:
        await db.execute(
            update(ScanJob)
            .where(ScanJob.id == scan_job_id)
            .values(status=JobStatus.RUNNING, start_time=datetime.utcnow())
        )
        await db.commit()
        
        target_domain = target_url.replace("https://", "").replace("http://", "").split("/")[0]

        try:
            await log_to_db(db, scan_job_id, "INFO", f"🚀 Starting AI-prioritized recon: {scan_plan['priority']} priority.")
            modules = scan_plan.get("modules", [])
            
            # 1. Asset Discovery
            if "subfinder" in modules:
                await log_to_db(db, scan_job_id, "INFO", "🔍 Discovering subdomains...")
                subfinder = SubfinderScanner(target_domain, scan_job_id)
                subdomains = await subfinder.run()
                for sub in subdomains:
                    new_asset = Asset(target_id=(await db.get(ScanJob, scan_job_id)).target_id, type="subdomain", value=sub)
                    db.add(new_asset)
                await db.commit()
            
            # 2. Port Scanning
            if "nmap" in modules:
                await log_to_db(db, scan_job_id, "INFO", f"🔌 Scanning ports...")
                nmap = NmapScanner(target_domain, scan_job_id)
                ports = await nmap.run()
            
            # 3. Vulnerability Scanning
            if "nuclei" in modules:
                await log_to_db(db, scan_job_id, "INFO", "🛡️  Running vulnerability scanners (Nuclei)...")
                nuclei = NucleiScanner(target_url, scan_job_id)
                nuclei_vulns = await nuclei.run()
            
            # 4. JS Analysis
            if "js_analysis" in modules:
                await log_to_db(db, scan_job_id, "INFO", "Analyzing JS files...")
                # ... (rest of the pipeline)
            
            # 8. AI Correlation & Reporting
            await log_to_db(db, scan_job_id, "INFO", "🤖 AI analyzing results and generating executive summary...")
            all_findings = {
                "subdomains": subdomains,
                "ports": ports,
                "web_data": web_data,
                "tech_stack": correlated_tech,
                "js_analysis": js_results,
                "nuclei_vulns": nuclei_vulns
            }
            
            analyzer = AIAnalyzer()
            ai_analysis = await analyzer.analyze_results(all_findings)
            
            # 9. Finalize
            await db.execute(
                update(ScanJob)
                .where(ScanJob.id == scan_job_id)
                .values(
                    status=JobStatus.COMPLETED, 
                    end_time=datetime.utcnow(),
                    results_summary=json.dumps(ai_analysis)
                )
            )
            await db.commit()
            await log_to_db(db, scan_job_id, "INFO", "✅ Full recon pipeline complete.")

        except Exception as e:
            await log_to_db(db, scan_job_id, "ERROR", f"❌ Pipeline failed: {str(e)}")
            await db.execute(
                update(ScanJob)
                .where(ScanJob.id == scan_job_id)
                .values(status=JobStatus.FAILED)
            )
            await db.commit()
