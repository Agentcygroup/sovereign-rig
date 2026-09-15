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
def worker_vision_detection(config: Dict[str, Any]) -> Dict[str, Any]:
    import torch
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    t = torch.randn(1, 3, 640, 640, device=device)
    res = {"node": config.get("node_id"), "domain": "Vision", "device": str(device), "sum": float(t.sum().item())}
    GLOBAL_BUS.publish("vision", res)
    return res

@ray.remote
def worker_llm_reasoning(config: Dict[str, Any]) -> Dict[str, Any]:
    import torch
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    return {"node": config.get("node_id"), "domain": "LLM", "device": str(device), "status": "active"}

if __name__ == "__main__":
    if not ray.is_initialized():
        ray.init(ignore_reinit_error=True)
    f1 = worker_vision_detection.remote({"node_id": "node-01"})
    f2 = worker_llm_reasoning.remote({"node_id": "node-02"})
    print(json.dumps(ray.get([f1, f2]), indent=2))
