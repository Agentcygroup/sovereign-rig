import time
import psutil
import logging

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [SymmetricSentinel] %(message)s")
logger = logging.getLogger("SymmetricSentinel")

if __name__ == "__main__":
    logger.info("Symmetric Sentinel active. Monitoring Apple Silicon MLX mesh...")
    while True:
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().percent
        logger.info(f"Cluster Telemetry -> CPU: {cpu}% | RAM: {mem}%")
        time.sleep(15)
