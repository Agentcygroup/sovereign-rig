import time
import psutil
import logging

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [LocalSentinel] %(message)s")
logger = logging.getLogger("LocalSentinel")

if __name__ == "__main__":
    logger.info("Local Sentinel monitoring local resources...")
    while True:
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().percent
        logger.info(f"Local Metrics -> CPU: {cpu}% | RAM: {mem}%")
        time.sleep(20)
