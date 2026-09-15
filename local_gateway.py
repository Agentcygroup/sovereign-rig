from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
import sqlite3
import json
import logging

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [LocalGateway] %(message)s")
logger = logging.getLogger("LocalGateway")

app = FastAPI(title="Local Sovereign Gateway", version="4.1.0")

class LocalConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Local hook connected. Active local sockets: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"Local hook disconnected. Active local sockets: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Local broadcast error: {e}")

manager = LocalConnectionManager()

@app.get("/")
def read_root():
    conn = sqlite3.connect("local_sovereign.db")
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM local_state WHERE key='status'")
    val = cursor.fetchone()[0]
    conn.close()
    return {
        "system": "100% Local Sovereign Rig",
        "database": "SQLite Embedded",
        "db_status": val,
        "endpoints": "Localhost Only",
        "hooks": "Active"
    }

@app.get("/db/read/{key}")
def read_db(key: str):
    conn = sqlite3.connect("local_sovereign.db")
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM local_state WHERE key=?", (key,))
    row = cursor.fetchone()
    conn.close()
    return {"key": key, "value": row[0] if row else None}

@app.post("/db/write/{key}/{value}")
def write_db(key: str, value: str):
    conn = sqlite3.connect("local_sovereign.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO local_state (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()
    return {"status": "SUCCESS", "key": key, "value": value}

@app.websocket("/ws/hook")
async def local_websocket_hook(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await websocket.send_text(json.dumps({"event": "HOOK_CONNECTED", "scope": "local"}))
        while True:
            data = await websocket.receive_text()
            logger.info(f"Local hook payload received: {data}")
            await manager.broadcast(json.dumps({"received": data, "status": "PROCESSED_LOCALLY"}))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
