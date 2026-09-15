import asyncio
import json
import ray
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI(title="Omni-Swarm Telemetry & WebSocket Gateway")

CONNECTED_CLIENTS = set()

@app.on_event("startup")
async def startup_event():
    if not ray.is_initialized():
        ray.init(ignore_reinit_error=True)

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.get("/")
async def get_dashboard():
    html_content = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Omni-Swarm Telemetry</title>
            <style>
                body { background: #0d1117; color: #c9d1d9; font-family: monospace; padding: 20px; }
                h2 { color: #58a6ff; }
                #log { background: #161b22; border: 1px solid #30363d; padding: 15px; height: 400px; overflow-y: scroll; }
            </style>
        </head>
        <body>
            <h2>Omni-Swarm Real-Time Telemetry Stream</h2>
            <div id="log"></div>
            <script>
                const ws = new WebSocket("ws://" + window.location.host + "/ws");
                ws.onmessage = function(event) {
                    const logDiv = document.getElementById("log");
                    const data = JSON.parse(event.data);
                    logDiv.innerHTML += "<pre>" + JSON.stringify(data, null, 2) + "</pre>";
                    logDiv.scrollTop = logDiv.scrollHeight;
                };
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Simulate real-time cluster telemetry ping
            telemetry_packet = {
                "timestamp": asyncio.get_event_loop().time(),
                "cluster_status": "active",
                "active_nodes": ["node-01", "node-02", "node-03"],
                "mps_utilization_pct": 42.5
            }
            await websocket.send_text(json.dumps(telemetry_packet))
            await asyncio.sleep(2.0)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/healthz")
async def healthz():
    return {"status": "healthy", "ray_initialized": ray.is_initialized()}

@app.get("/metrics")
async def metrics():
    return {
        "cluster_nodes": 3,
        "domains_operational": 14,
        "serialization_fallback": "active"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
