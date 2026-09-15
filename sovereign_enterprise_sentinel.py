import time
import psutil
import logging

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [UCS-Sentinel] %(message)s")
logger = logging.getLogger("SovereignSentinel")

if __name__ == "__main__":
    logger.info("UCS Sentinel active. Monitoring Apple Silicon MLX cluster telemetry...")
    while True:
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().percent
        logger.info(f"Telemetry -> CPU: {cpu}% | RAM: {mem}%")
        time.sleep(15)
