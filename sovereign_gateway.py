from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
import os
import json
import logging

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [UCS-Gateway] %(message)s")
logger = logging.getLogger("GatewayEngine")

app = FastAPI(title="Sovereign UCS Enterprise Gateway", version="3.2.0")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Active mesh sockets: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"Client disconnected. Active mesh sockets: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Broadcast failure: {e}")

manager = ConnectionManager()

@app.get("/")
def read_root():
    return {
        "system": "Sovereign Omni-Universe Rig",
        "platform": "Universal Construction System",
        "status": "OPERATIONAL",
        "protocols": ["REST", "WebSocket"],
        "node": os.uname().nodename,
        "mesh": ["node-01", "node-02", "node-03"]
    }

@app.get("/health")
def health_check():
    return {"status": "HEALTHY", "conformance": "VERIFIED", "active_sockets": len(manager.active_connections)}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    try:
        await websocket.send_text(json.dumps({"system": "CONNECTED", "client_id": client_id}))
        while True:
            data = await websocket.receive_text()
            logger.info(f"Frame received from {client_id}: {data}")
            await manager.broadcast(json.dumps({"sender": client_id, "payload": data, "status": "RELAYED"}))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(json.dumps({"system": "DISCONNECTED", "client_id": client_id}))
