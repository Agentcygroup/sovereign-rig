import time
import json
import logging
import ray

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

@ray.remote
def autonomous_worker_task(node_id: int, cycle_id: int, tensor_data: list) -> dict:
    import torch
    
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    
    class PureLocalModel(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.linear = torch.nn.Linear(3, 16)
            self.act = torch.nn.ReLU()

        def forward(self, x):
            return self.act(self.linear(x))

    model = PureLocalModel().to(device).eval()
    input_tensor = torch.tensor(tensor_data, dtype=torch.float32, device=device)
    
    with torch.inference_mode():
        output_tensor = model(input_tensor)
        
    return {
        "node_id": f"node-0{node_id}",
        "cycle_id": cycle_id,
        "device": str(device),
        "output_checksum": float(output_tensor.sum().item()),
        "status": "AUTOMATION_CYCLE_SUCCESS",
        "timestamp": time.time()
    }

def run_automation_daemon(max_cycles: int = 3, interval_seconds: float = 1.5):
    if not ray.is_initialized():
        ray.init(ignore_reinit_error=True)

    logging.info("Initializing Autonomous Worker Tasks (3 Nodes)...")
    payload = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]

    try:
        for cycle in range(1, max_cycles + 1):
            cycle_start = time.time()
            logging.info(f"Starting Automation Cycle {cycle}/{max_cycles}...")

            futures = [autonomous_worker_task.remote(i + 1, cycle, payload) for i in range(3)]
            results = ray.get(futures)

            duration = time.time() - cycle_start
            report = {
                "cycle": cycle,
                "duration_seconds": duration,
                "cluster_nodes": ["node-01", "node-02", "node-03"],
                "telemetry": results
            }
            
            logging.info(f"Cycle {cycle} Completed Successfully in {duration:.4f}s")
            print(json.dumps(report, indent=2))

            if cycle < max_cycles:
                time.sleep(interval_seconds)

    except KeyboardInterrupt:
        logging.info("Automation daemon terminated gracefully by user.")
    finally:
        ray.shutdown()
        logging.info("Ray cluster shutdown complete.")

if __name__ == "__main__":
    run_automation_daemon(max_cycles=3, interval_seconds=1.5)
