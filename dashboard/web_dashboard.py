from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import json
import glob
import os

app = FastAPI(title="GEMINIRECON Vulnerability Dashboard")

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    html_content = """
    <html>
        <head>
            <title>GEMINIRECON Dashboard</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body { background-color: #121212; color: #e0e0e0; }
                .card { background-color: #1e1e1e; border: none; }
                table { color: #e0e0e0; }
                thead { background-color: #333; }
            </style>
        </head>
        <body class="p-5">
            <h1 class="mb-4 text-primary">GEMINIRECON Vulnerabilities</h1>
            <div class="card p-4">
                <table class="table table-dark table-hover">
                    <thead>
                        <tr>
                            <th>Target</th>
                            <th>Template</th>
                            <th>Severity</th>
                            <th>URL</th>
                            <th>Timestamp</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    # Aggregating data
    for vuln_file in glob.glob("results/*/vulnerabilities.json"):
        target = vuln_file.split("/")[1]
        try:
            with open(vuln_file, 'r') as f:
                for line in f:
                    if not line.strip(): continue
                    data = json.loads(line)
                    html_content += f"""
                        <tr>
                            <td>{target}</td>
                            <td>{data.get("template-id", "N/A")}</td>
                            <td><span class="badge bg-{'danger' if data.get('info', {}).get('severity') == 'high' else 'warning'}">{data.get('info', {}).get('severity', 'N/A')}</span></td>
                            <td>{data.get('matched-at', 'N/A')}</td>
                            <td>{data.get('timestamp', 'N/A')}</td>
                        </tr>
                    """
        except Exception:
            continue
            
    html_content += """
                    </tbody>
                </table>
            </div>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
