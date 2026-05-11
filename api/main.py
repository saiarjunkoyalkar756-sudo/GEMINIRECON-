from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from api.routes import scans, targets, vulnerabilities, users, auth
from core.storage.database import init_db
from websocket.manager import manager
from core.events import event_bus
import asyncio
import json
import os

app = FastAPI(
    title="GEMINIRECON API",
    description="Enterprise-grade AI-assisted reconnaissance and vulnerability assessment platform",
    version="2.0.0"
)

# CORS configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(targets.router, prefix="/targets", tags=["Targets"])
app.include_router(scans.router, prefix="/scans", tags=["Scans"])
app.include_router(vulnerabilities.router, prefix="/vulnerabilities", tags=["Vulnerabilities"])

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/")
async def root():
    return {"message": "GEMINIRECON API is running", "version": "2.0.0"}

@app.websocket("/ws/scans/{scan_job_id}")
async def websocket_endpoint(websocket: WebSocket, scan_job_id: int):
    await manager.connect(scan_job_id, websocket)
    pubsub = await event_bus.subscribe_to_scan(scan_job_id)
    
    async def listen_to_redis():
        try:
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    await websocket.send_text(message['data'].decode())
        except Exception as e:
            print(f"Redis listen error: {e}")

    listen_task = asyncio.create_task(listen_to_redis())
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        listen_task.cancel()
        manager.disconnect(scan_job_id, websocket)
        await pubsub.unsubscribe(f"scan:{scan_job_id}")
