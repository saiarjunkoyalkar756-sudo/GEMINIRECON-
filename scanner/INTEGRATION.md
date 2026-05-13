# GEMINIRECON Scanner Integration Guide

Complete guide to integrate the Codespaces Scanner with Render Backend and Supabase.

## 🏗️ Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                    Vercel Frontend                           │
│              (GEMINIRECON Dashboard UI)                      │
└────────────────────────┬─────────────────────────────────────┘
                         │ HTTP/WebSocket
                         ↓
┌──────────────────────────────────────────────────────────────┐
│                   Render Backend                             │
│            (Mission orchestration & API)                     │
│  • /api/missions/create                                      │
│  • /api/missions/{id}/status                                 │
│  • /api/missions/{id}/findings                               │
└────────────────────────┬─────────────────────────────────────┘
                         │ HTTPS
                         ↓
┌──────────────────────────────────────────────────────────────┐
│          GitHub Codespaces Scanner API                       │
│              (This Scanner Service)                          │
│  • POST /scan/subdomains                                     │
│  • POST /scan/httpx                                          │
│  • POST /scan/nuclei                                         │
└────────────────────────┬─────────────────────────────────────┘
                    ┌────┼────┐
                    ↓    ↓    ↓
         ┌─────────────────────────────┐
         │  Reconnaissance Tools       │
         │  • subfinder   (subdomains) │
         │  • httpx       (probing)    │
         │  • nuclei      (vulns)      │
         │  • naabu       (ports)      │
         └────────────┬────────────────┘
                      ↓
         ┌─────────────────────────────┐
         │   JSON Structured Output    │
         │   (Evidence & Metadata)     │
         └────────────┬────────────────┘
                      ↓
┌──────────────────────────────────────────────────────────────┐
│                 Supabase PostgreSQL                          │
│            (Findings & AI Analysis Storage)                  │
│  • scan_results table                                        │
│  • findings table                                            │
│  • vectorized embeddings (pgvector)                          │
└──────────────────────────────────────────────────────────────┘
```

## 🔗 Integration Steps

### Step 1: Get Codespaces Scanner URL

After launching Codespaces, you get a unique URL:

```
https://your-username-codespace-xxxxx.github.dev
```

Access the scanner at:
```
https://your-username-codespace-xxxxx.github.dev:8001
```

### Step 2: Configure Render Backend

Add environment variables to your Render backend:

```bash
# Dashboard → Environment
CODESPACES_SCANNER_URL=https://your-codespace.github.dev:8001
SCANNER_API_KEY=your_scanner_api_key
```

### Step 3: Add Scanner Integration to Render Backend

In your Render backend (`backend/app.py` or similar):

```python
import httpx
from datetime import datetime
from sqlalchemy import insert

# Scanner configuration
SCANNER_URL = os.getenv("CODESPACES_SCANNER_URL", "http://localhost:8001")
SCANNER_API_KEY = os.getenv("SCANNER_API_KEY")

async def trigger_codespaces_scan(target: str, mission_id: str):
    """Trigger scan on Codespaces scanner"""
    try:
        async with httpx.AsyncClient(timeout=400) as client:
            
            # Step 1: Enumerate subdomains
            logger.info(f"Scanning subdomains for {target}")
            subdomain_response = await client.post(
                f"{SCANNER_URL}/scan/subdomains",
                json={"target": target},
                headers={"X-API-Key": SCANNER_API_KEY}
            )
            subdomain_result = subdomain_response.json()
            
            # Step 2: Probe HTTP services
            if subdomain_result["status"] == "success":
                subdomains = [f["value"] for f in subdomain_result["findings"]]
                urls = [f"http://{sub}" for sub in subdomains[:10]]  # Limit to 10
                
                logger.info(f"Probing {len(urls)} hosts")
                httpx_response = await client.post(
                    f"{SCANNER_URL}/scan/httpx",
                    json={"target": target, "urls": urls},
                    headers={"X-API-Key": SCANNER_API_KEY}
                )
                httpx_result = httpx_response.json()
            
            # Step 3: Detect vulnerabilities
            logger.info(f"Detecting vulnerabilities for {target}")
            nuclei_response = await client.post(
                f"{SCANNER_URL}/scan/nuclei",
                json={"target": f"https://{target}", "severity": "all"},
                headers={"X-API-Key": SCANNER_API_KEY},
                timeout=500
            )
            nuclei_result = nuclei_response.json()
            
            # Store results in Supabase
            findings = {
                "mission_id": mission_id,
                "target": target,
                "subdomains": subdomain_result.get("findings", []),
                "http_services": httpx_result.get("findings", []),
                "vulnerabilities": nuclei_result.get("findings", []),
                "scan_metadata": {
                    "subfinder_scan_id": subdomain_result.get("scan_id"),
                    "httpx_scan_id": httpx_result.get("scan_id"),
                    "nuclei_scan_id": nuclei_result.get("scan_id"),
                    "execution_time": (
                        subdomain_result.get("execution_time", 0) +
                        httpx_result.get("execution_time", 0) +
                        nuclei_result.get("execution_time", 0)
                    ),
                    "total_findings": (
                        len(subdomain_result.get("findings", [])) +
                        len(httpx_result.get("findings", [])) +
                        len(nuclei_result.get("findings", []))
                    )
                },
                "status": "completed",
                "completed_at": datetime.now().isoformat()
            }
            
            # Save to Supabase
            supabase.table("scan_results").insert(findings).execute()
            
            return findings
    
    except httpx.TimeoutException:
        logger.error(f"Scanner timeout for {target}")
        return {"status": "error", "error": "Scanner timeout"}
    
    except Exception as e:
        logger.error(f"Scanner error: {str(e)}")
        return {"status": "error", "error": str(e)}

# Create API endpoint
@app.post("/api/missions/{mission_id}/scan")
async def start_mission_scan(mission_id: str, request: ScanRequest):
    """Start autonomous reconnaissance mission"""
    
    # Get mission from database
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    # Trigger scanner
    try:
        results = await trigger_codespaces_scan(mission.target, mission_id)
        
        # Update mission status
        mission.status = "completed"
        mission.findings_count = results["scan_metadata"]["total_findings"]
        db.commit()
        
        return {
            "mission_id": mission_id,
            "status": "completed",
            "findings": results
        }
    
    except Exception as e:
        mission.status = "failed"
        mission.error = str(e)
        db.commit()
        
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")
```

### Step 4: Database Schema for Results

Create Supabase tables:

```sql
-- Scan Results Table
CREATE TABLE scan_results (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  mission_id uuid NOT NULL,
  target text NOT NULL,
  subdomains jsonb DEFAULT '[]'::jsonb,
  http_services jsonb DEFAULT '[]'::jsonb,
  vulnerabilities jsonb DEFAULT '[]'::jsonb,
  scan_metadata jsonb,
  status text DEFAULT 'pending',
  completed_at timestamp,
  created_at timestamp DEFAULT now(),
  
  FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE,
  INDEX scan_results_mission_id ON scan_results(mission_id),
  INDEX scan_results_target ON scan_results(target)
);

-- Findings Table (normalized for analysis)
CREATE TABLE findings (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  scan_result_id uuid NOT NULL,
  finding_type text,
  severity text,
  data jsonb,
  embedding vector(1536),
  created_at timestamp DEFAULT now(),
  
  FOREIGN KEY (scan_result_id) REFERENCES scan_results(id) ON DELETE CASCADE,
  INDEX findings_severity ON findings(severity),
  INDEX findings_type ON findings(finding_type)
);

-- Create vector index for similarity search
CREATE INDEX ON findings USING ivfflat (embedding vector_cosine_ops);
```

### Step 5: Frontend Integration (Vercel)

Display scanner results in dashboard:

```typescript
// frontend/src/pages/MissionDetails.tsx

import { useEffect, useState } from 'react';
import { getMissionFindings } from '@/api/missions';

export function MissionDetails({ missionId }: { missionId: string }) {
  const [findings, setFindings] = useState({
    subdomains: [],
    httpServices: [],
    vulnerabilities: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadFindings() {
      try {
        const result = await getMissionFindings(missionId);
        setFindings(result.data);
      } catch (error) {
        console.error('Failed to load findings:', error);
      } finally {
        setLoading(false);
      }
    }
    
    loadFindings();
  }, [missionId]);

  return (
    <div className="space-y-6">
      {/* Subdomains */}
      <div className="card">
        <h2 className="text-xl font-bold mb-4">
          Discovered Subdomains ({findings.subdomains.length})
        </h2>
        <div className="grid grid-cols-2 gap-2">
          {findings.subdomains.map((subdomain) => (
            <div key={subdomain.value} className="p-2 bg-gray-100 rounded">
              {subdomain.value}
            </div>
          ))}
        </div>
      </div>

      {/* HTTP Services */}
      <div className="card">
        <h2 className="text-xl font-bold mb-4">
          HTTP Services ({findings.httpServices.length})
        </h2>
        <table className="w-full">
          <thead>
            <tr>
              <th>URL</th>
              <th>Status</th>
              <th>Title</th>
            </tr>
          </thead>
          <tbody>
            {findings.httpServices.map((service) => (
              <tr key={service.url}>
                <td><a href={service.url} target="_blank">{service.url}</a></td>
                <td><span className={`badge status-${service.status_code}`}>
                  {service.status_code}
                </span></td>
                <td>{service.title}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Vulnerabilities */}
      <div className="card">
        <h2 className="text-xl font-bold mb-4">
          Vulnerabilities ({findings.vulnerabilities.length})
        </h2>
        <div className="space-y-2">
          {findings.vulnerabilities.map((vuln) => (
            <div key={vuln.id} className={`p-4 border-l-4 border-${vuln.severity}`}>
              <h3 className="font-bold">{vuln.template_name}</h3>
              <p className="text-sm text-gray-600">{vuln.severity}</p>
              <p className="text-xs mt-2">{vuln.url}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
```

## 🔄 Workflow Example

### Complete Reconnaissance Mission

```python
# backend/missions/autonomous_scan.py

from datetime import datetime
from celery import shared_task
import asyncio

@shared_task
def run_autonomous_mission(mission_id: str, target: str):
    """Complete autonomous reconnaissance mission"""
    
    try:
        # Update mission status
        mission = db.query(Mission).get(mission_id)
        mission.status = "scanning"
        db.commit()
        
        # Run async scanner integration
        results = asyncio.run(trigger_codespaces_scan(target, mission_id))
        
        # Analyze findings with AI
        analysis = analyze_with_gemini(results)
        
        # Generate report
        report = generate_report(target, results, analysis)
        
        # Update mission
        mission.status = "completed"
        mission.findings_count = results["scan_metadata"]["total_findings"]
        mission.report_url = upload_report(report)
        mission.completed_at = datetime.now()
        db.commit()
        
        # Send notifications
        notify_dashboard(mission_id, "completed")
        
        return {
            "status": "success",
            "mission_id": mission_id,
            "findings_count": results["scan_metadata"]["total_findings"],
            "report_url": mission.report_url
        }
    
    except Exception as e:
        mission.status = "failed"
        mission.error = str(e)
        db.commit()
        notify_dashboard(mission_id, "failed", error=str(e))
        raise
```

## 🔒 Security Considerations

### API Key Management
```bash
# NEVER commit API keys
# Use environment variables

# In Render environment:
SCANNER_API_KEY=<generated_secure_key>

# In Codespaces .env.local (never committed):
SCANNER_API_KEY=<same_key>
```

### Network Security
```python
# Use HTTPS only
SCANNER_URL = "https://your-codespace.github.dev:8001"

# Validate SSL certificates
client = httpx.AsyncClient(verify=True)

# Add timeout protection
timeout=httpx.Timeout(400, connect=10)
```

### Input Validation
```python
# All scanner inputs validated by FastAPI
# Additional backend validation

def validate_target(target: str) -> bool:
    """Validate target before scanning"""
    # Check against allowlist
    # Validate domain/IP format
    # Check for reserved ranges
    return is_valid_target(target)
```

## 📊 Monitoring & Logging

### Track Scanner Performance

```python
# Log all scanner calls
async def log_scanner_call(target: str, scan_type: str, result: dict):
    """Log scanner execution for monitoring"""
    
    log_entry = {
        "timestamp": datetime.now(),
        "target": target,
        "scan_type": scan_type,
        "status": result["status"],
        "execution_time": result["execution_time"],
        "findings_count": len(result["findings"]),
        "errors": result.get("errors", [])
    }
    
    # Store in database for analytics
    supabase.table("scanner_logs").insert(log_entry).execute()
    
    # Alert on failures
    if result["status"] == "error":
        alert_ops_team(log_entry)
```

## 🚀 Production Deployment

### Option 1: Keep Using Codespaces
```bash
# Pros: Always-on development
# Cons: Limited to 60 hours/month

# Set to never sleep
Settings → Codespaces → Retention → 30 days
```

### Option 2: Migrate to Render Container
```bash
# Build and push Docker image
docker build -f scanner/Dockerfile -t geminirecon-scanner .
docker tag geminirecon-scanner your-registry/geminirecon-scanner
docker push your-registry/geminirecon-scanner

# Deploy on Render
# New → Web Service → Docker
```

### Option 3: AWS Lambda
```python
# Serverless deployment with Chalice
pip install chalice
chalice new geminirecon-scanner
# Deploy scanner as Lambda functions
chalice deploy
```

## 📈 Scaling Considerations

### For High Volume:

1. **Queue System** (Celery + Redis)
   ```python
   @celery_app.task
   def scan_target_async(target: str):
       return asyncio.run(trigger_codespaces_scan(target))
   ```

2. **Multiple Scanner Instances**
   ```yaml
   # Docker Compose
   scanner-1:
     image: geminirecon-scanner:latest
     ports: ["8001:8001"]
   
   scanner-2:
     image: geminirecon-scanner:latest
     ports: ["8002:8001"]
   
   scanner-3:
     image: geminirecon-scanner:latest
     ports: ["8003:8001"]
   ```

3. **Load Balancing**
   ```python
   SCANNER_URLS = [
       "https://codespace1.github.dev:8001",
       "https://codespace2.github.dev:8001",
       "https://codespace3.github.dev:8001"
   ]
   
   selected_scanner = random.choice(SCANNER_URLS)
   ```

---

**Your GEMINIRECON system is now fully integrated! 🎉**
