import os
import subprocess
import sys
import sqlite3
import json

WORKSPACE = os.path.expanduser("~/usd-rig")
os.makedirs(WORKSPACE, exist_ok=True)
os.chdir(WORKSPACE)

print("=== [LOCAL RIG: Initializing 100% Local Infrastructure] ===")

# 1. Local Database Initialization (SQLite)
DB_PATH = "local_sovereign.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS local_state (
        key TEXT PRIMARY KEY,
        value TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
cursor.execute("INSERT OR REPLACE INTO local_state (key, value) VALUES ('status', 'LOCAL_OPERATIONAL')")
conn.commit()
conn.close()
print(f"[OK] Local embedded database initialized at {os.path.abspath(DB_PATH)}")

# 2. Local Endpoints & Hooks Gateway (FastAPI + Local WebSockets)
with open("local_gateway.py", "w") as f:
    f.write('''from fastapi import FastAPI, WebSocket, WebSocketDisconnect
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
''')

# 3. Local Sentinel Server
with open("local_sentinel.py", "w") as f:
    f.write('''import time
import psutil
import logging

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [LocalSentinel] %(message)s")
logger = logging.getLogger("LocalSentinel")

if __name__ == "__main__":
    logger.info("Local Sentinel monitoring local resources...")
    while True:
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().percent
        logger.info(f"Local Metrics -> CPU: {cpu}% | RAM: {mem}%")
        time.sleep(20)
''')

print("=== [LOCAL RIG: Terminating Existing Daemons & Launching Local Servers] ===")
subprocess.run(["pkill", "-f", "local_gateway"], check=False)
subprocess.run(["pkill", "-f", "local_sentinel"], check=False)

# Launch Local Gateway Server on Loopback
subprocess.Popen(["python3", "-m", "uvicorn", "local_gateway:app", "--host", "127.0.0.1", "--port", "8000"])
# Launch Local Sentinel Server
subprocess.Popen(["python3", "local_sentinel.py"])

print("\n==============================================================================")
print(" 100% LOCAL SOVEREIGN RIG: FULLY OPERATIONAL")
print("------------------------------------------------------------------------------")
print(" * Local API Endpoints       : http://127.0.0.1:8000")
print(" * Local WebSocket Hook      : ws://127.0.0.1:8000/ws/hook")
print(" * Local Database            : SQLite (~/usd-rig/local_sovereign.db)")
print(" * Local Sentinel Server     : Active (Background Process)")
print("==============================================================================")
