import copyreg
import sys
import time
import json
import threading
from typing import Dict, Any, List

try:
    import torch
    from torch.fx.graph_module import GenericModule
    copyreg.pickle(GenericModule, lambda m: (str, ("GenericModule_Stub",)))
except Exception:
    pass

import ray

class SafeEventBus:
    def __init__(self):
        self._lock = threading.Lock()
        self._store = {}

    def publish(self, channel: str, message: dict):
        with self._lock:
            if channel not in self._store:
                self._store[channel] = []
            self._store[channel].append(message)

GLOBAL_BUS = SafeEventBus()

@ray.remote
def worker_domain_task(config: Dict[str, Any]) -> Dict[str, Any]:
    import torch
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    cfg_id = config.get("config_id", 0)
    domain = config.get("domain", "General")
    
    return {
        "config_id": cfg_id,
        "node_id": config.get("node_id", "node-01"),
        "domain": domain,
        "status": "success",
        "device": str(device),
        "score": float(cfg_id * 1.5)
    }

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.responses import HTMLResponse
    import uvicorn

    app = FastAPI(title="Omni-Swarm 1000-Config Gateway")

    class ConnectionManager:
        def __init__(self):
            self.active_connections: list[WebSocket] = []

        async def connect(self, websocket: WebSocket):
            await websocket.accept()
            self.active_connections.append(websocket)

        def disconnect(self, websocket: WebSocket):
            self.active_connections.remove(websocket)

    manager = ConnectionManager()

    @app.get("/", response_class=HTMLResponse)
    async def dashboard():
        return """
        <!DOCTYPE html>
        <html>
            <head><title>Omni-Swarm 1K Telemetry</title></head>
            <body style="background:#0b0f19;color:#e6edf3;font-family:monospace;padding:20px;">
                <h2>Omni-Swarm 1,000 Config Telemetry Gateway</h2>
                <div id="log" style="background:#161b22;padding:15px;height:400px;overflow-y:scroll;"></div>
            </body>
        </html>
        """
except ImportError:
    app = None

def run_large_sweep(total_configs=1000, batch_size=100):
    if not ray.is_initialized():
        ray.init(ignore_reinit_error=True)

    print(f"==================================================")
    print(f"[info] Dispatching {total_configs} configurations in batches of {batch_size}...")
    print(f"==================================================")
    
    start_time = time.time()
    all_results = []
    domains = ["Vision", "LLM", "Multimodal", "Diffusion", "Audio", "Cybersecurity", "Time-Series", "RL"]

    for i in range(0, total_configs, batch_size):
        batch_configs = [
            {
                "config_id": idx,
                "node_id": f"node-0{(idx % 3) + 1}",
                "domain": domains[idx % len(domains)]
            }
            for idx in range(i, min(i + batch_size, total_configs))
        ]
        
        futures = [worker_domain_task.remote(cfg) for cfg in batch_configs]
        batch_results = ray.get(futures)
        all_results.extend(batch_results)
        print(f"Completed batch {i // batch_size + 1} / {total_configs // batch_size} ({len(all_results)}/{total_configs} processed)")

    duration = time.time() - start_time
    print(f"\n--- Completed {total_configs} configurations in {duration:.2f}s ---")
    return all_results

if __name__ == "__main__":
    results = run_large_sweep(1000, 100)
    print(f"Sample Result: {json.dumps(results[0], indent=2)}")
