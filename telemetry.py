import time, urllib.request, json, os

LOG_PATH = os.path.expanduser("~/.llama/observability.log")
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

while True:
    try:
        start = time.time()
        req = urllib.request.Request(
            "http://127.0.0.1:8080/health",
            headers={"User-Agent": "TelemetryAgent"}
        )
        with urllib.request.urlopen(req, timeout=2) as resp:
            status = resp.status
            latency = (time.time() - start) * 1000
            
        metric = f"ts={time.time()} status={status} latency_ms={latency:.2f}\n"
        with open(LOG_PATH, "a") as f:
            f.write(metric)
    except Exception as e:
        with open(LOG_PATH, "a") as f:
            f.write(f"ts={time.time()} error={str(e)}\n")
    time.sleep(5)
