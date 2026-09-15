import time
import psutil
import logging

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [Sentinel] %(message)s")
logger = logging.getLogger("SovereignSentinel")

if __name__ == "__main__":
    logger.info("Enterprise Sentinel active. Monitoring Apple Silicon MLX cluster nodes...")
    while True:
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().percent
        logger.info(f"Node telemetry -> CPU: {cpu}% | RAM Utilization: {mem}%")
        time.sleep(15)
