import time
import json
import ray
from fastapi import FastAPI, HTTPException
import uvicorn

app = FastAPI(
    title="Omni-Rig Telemetry Gateway",
    description="Distributed Ray Cluster & Vision Microservice Control Plane",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    if not ray.is_initialized():
        ray.init(ignore_reinit_error=True)

@app.on_event("shutdown")
async def shutdown_event():
    if ray.is_initialized():
        ray.shutdown()

@ray.remote
def fetch_node_telemetry(node_id: int) -> dict:
    import time
    return {
        "node_id": f"node-0{node_id}",
        "status": "HEALTHY",
        "load_avg": [0.12, 0.18, 0.22],
        "backend": "Apple Silicon MPS / Ray",
        "timestamp": time.time()
    }

@app.get("/health")
async def cluster_health():
    try:
        futures = [fetch_node_telemetry.remote(i + 1) for i in range(3)]
        cluster_metrics = ray.get(futures)
        return {
            "gateway_status": "ONLINE",
            "cluster_nodes": 3,
            "nodes": cluster_metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trigger-sweep")
async def trigger_sweep(cycles: int = 1):
    return {
        "status": "SWEEP_DISPATCHED",
        "cycles_requested": cycles,
        "timestamp": time.time()
    }

if __name__ == "__main__":
    uvicorn.run("omni_fastapi_gateway:app", host="0.0.0.0", port=8000, reload=False)
