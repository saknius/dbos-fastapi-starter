# app/utils/locks.py

import redis
from configs.config import settings
import uuid
import time

redis_client = redis.Redis.from_url(settings.REDIS_URL)

class RedisLock:
    def __init__(self, name, timeout=10):
        self.name = f"lock:{name}"
        self.timeout = timeout
        self.identifier = str(uuid.uuid4())

    def acquire(self):
        end = time.time() + self.timeout
        while time.time() < end:
            if redis_client.set(self.name, self.identifier, nx=True, ex=self.timeout):
                return True
            time.sleep(0.01)
        return False

    def release(self):
        pipe = redis_client.pipeline(True)
        while True:
            try:
                pipe.watch(self.name)
                if redis_client.get(self.name).decode('utf-8') == self.identifier:
                    pipe.multi()
                    pipe.delete(self.name)
                    pipe.execute()
                else:
                    pipe.unwatch()
                break
            except redis.WatchError:
                continue
