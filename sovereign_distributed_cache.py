import os
import ray
import redis
import logging

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [UCS-Cache] %(message)s")
logger = logging.getLogger("SovereignCacheEngine")

class SovereignMemoryGrid:
    def __init__(self):
        try:
            self.redis = redis.Redis(host="localhost", port=6379, decode_responses=True)
            self.redis.ping()
            logger.info("Connected to Redis metadata bus.")
        except:
            self.redis = None
            logger.info("Redis offline; routing via Ray distributed object substrate.")
            
        if not ray.is_initialized():
            ray.init(ignore_reinit_error=True, include_dashboard=False)

    def execute(self, key: str, payload: dict):
        if self.redis and self.redis.get(f"cache:{key}"):
            return self.redis.get(f"cache:{key}")
        res = {"node": os.uname().nodename, "payload": payload, "status": "COMPUTED"}
        if self.redis:
            self.redis.setex(f"cache:{key}", 60, str(res))
        return res

if __name__ == "__main__":
    grid = SovereignMemoryGrid()
    print(grid.execute("ucs_test", {"mesh_nodes": 3}))
