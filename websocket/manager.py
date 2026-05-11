from fastapi import WebSocket
from typing import Dict, List
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, scan_job_id: int, websocket: WebSocket):
        await websocket.accept()
        if scan_job_id not in self.active_connections:
            self.active_connections[scan_job_id] = []
        self.active_connections[scan_job_id].append(websocket)

    def disconnect(self, scan_job_id: int, websocket: WebSocket):
        if scan_job_id in self.active_connections:
            self.active_connections[scan_job_id].remove(websocket)
            if not self.active_connections[scan_job_id]:
                del self.active_connections[scan_job_id]

    async def broadcast(self, scan_job_id: int, message: Dict):
        if scan_job_id in self.active_connections:
            for connection in self.active_connections[scan_job_id]:
                await connection.send_json(message)

manager = ConnectionManager()
