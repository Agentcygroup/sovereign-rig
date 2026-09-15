import subprocess
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Sovereign Omni Gateway", version="1.0.0")

class SovereignRequest(BaseModel):
    prompt: str
    domain: str = "omni"

@app.get("/health")
def health_check():
    return {
        "status": "COMPLIANT",
        "cluster_nodes": ["node-01", "node-02", "node-03"],
        "hardware_backend": "Apple Silicon MLX / MPS",
        "zero_vendor_egress": True
    }

@app.post("/v1/omni/execute")
def execute_omni(req: SovereignRequest):
    try:
        result = subprocess.run(
            ["python3", "/Users/metadusa/usd-rig/pi_omni_universe_engine.py"],
            capture_output=True, text=True, check=True
        )
        output_data = json.loads(result.stdout) if result.stdout.strip().startswith("{") else {"raw": result.stdout}
        return {
            "status": "SUCCESS",
            "requested_domain": req.domain,
            "engine_output": output_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("[SovereignGateway] Starting local API server on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
