import ray
import time
import json

@ray.remote
def evaluate_config(config_id: int, params: dict):
    return {"config_id": config_id, "status": "success", "score": params.get("lr", 0.01) * config_id}

def run_large_sweep(total_configs=1000, batch_size=100):
    if not ray.is_initialized():
        ray.init(ignore_reinit_error=True)
    configs = [{"lr": 0.001 * ((i % 10) + 1)} for i in range(total_configs)]
    all_results = []
    for i in range(0, total_configs, batch_size):
        batch = configs[i:i + batch_size]
        futures = [evaluate_config.remote(i + idx, cfg) for idx, cfg in enumerate(batch)]
        all_results.extend(ray.get(futures))
    return all_results

if __name__ == "__main__":
    results = run_large_sweep(1000, 100)
    print(f"Processed 1000 configs. Sample: {json.dumps(results[0], indent=2)}")
