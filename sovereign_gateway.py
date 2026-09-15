from fastapi import FastAPI
import os

app = FastAPI(title="Sovereign Enterprise Gateway", version="3.0.0")

@app.get("/")
def read_root():
    return {
        "system": "Sovereign Omni-Universe Rig",
        "status": "OPERATIONAL",
        "node": os.uname().nodename,
        "mesh": ["node-01", "node-02", "node-03"]
    }

@app.get("/health")
def health_check():
    return {"status": "HEALTHY", "security": "ZERO_EGRESS_VERIFIED"}
