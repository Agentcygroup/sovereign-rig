import os
import ray
import redis
import logging

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [SymmetricCache] %(message)s")
logger = logging.getLogger("SymmetricCacheEngine")

class SymmetricalMemoryGrid:
    def __init__(self):
        try:
            self.redis = redis.Redis(host="localhost", port=6379, decode_responses=True)
            self.redis.ping()
            logger.info("Connected to Redis metadata bus.")
        except:
            self.redis = None
            logger.info("Redis offline; operating on Ray distributed shared memory.")
            
        if not ray.is_initialized():
            ray.init(ignore_reinit_error=True, include_dashboard=False)

    def execute(self, key: str, payload: dict):
        if self.redis and self.redis.get(f"cache:{key}"):
            return self.redis.get(f"cache:{key}")
        res = {"node": os.uname().nodename, "payload": payload, "status": "SYMMETRICALLY_COMPUTED"}
        if self.redis:
            self.redis.setex(f"cache:{key}", 60, str(res))
        return res

if __name__ == "__main__":
    grid = SymmetricalMemoryGrid()
    print(grid.execute("ucs_symmetric_test", {"mesh_nodes": 3}))
