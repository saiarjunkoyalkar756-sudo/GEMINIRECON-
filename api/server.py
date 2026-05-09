from fastapi import FastAPI, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import asyncio
from agents.orchestrator import ReconOrchestrator
from core.storage.database import init_db, get_session
from sqlalchemy.future import select
from core.storage.models import Scan, Target
from core.utils.tool_executor import set_tool_callback

app = FastAPI(title="GEMINIRECON API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()
orchestrator = ReconOrchestrator()

class ReconRequest(BaseModel):
    target: str

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/")
def read_root():
    return {"status": "online", "version": "2.0.0"}

@app.post("/api/recon")
async def start_recon(request: ReconRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_orchestrator, request.target)
    return {"status": "started", "target": request.target}

async def run_orchestrator(target: str):
    async def ws_callback(msg: str):
        await manager.broadcast({
            "type": "log",
            "data": msg,
            "target": target
        })
    
    # Set the global tool callback so each shell command execution is reported
    set_tool_callback(ws_callback)
    
    try:
        results = await orchestrator.run_recon_workflow(target, callback=ws_callback)
        await manager.broadcast({
            "type": "complete",
            "data": results,
            "target": target
        })
    except Exception as e:
        await manager.broadcast({
            "type": "error",
            "data": str(e),
            "target": target
        })
    finally:
        set_tool_callback(None)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
