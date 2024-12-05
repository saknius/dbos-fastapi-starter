import uuid
import redis
import time


class RedisLockManager:
    def __init__(self, redis_db):
        self.redis_db = redis_db

    def acquire_lock(
        self,
        key,
    ):
        lock_value = str(uuid.uuid4())
        while True:

            if self.redis_db.set(key, lock_value, nx=True):
                return lock_value
            time.sleep(0.01)

    def release_lock(self, key, lock_value):
        release_script = """
        if redis.call('get', KEYS[1]) == ARGV[1] then
            return redis.call('del', KEYS[1])
        else
            return 0
        end
        """
        self.redis_db.eval(release_script, 1, key, lock_value)

    def read_and_update(self, key, page_size, cluster_count):
        lock_key = f"{key}_lock"
        lock_value = self.acquire_lock(lock_key)

        try:

            value = self.redis_db.get(key)
            if value is None:
                value = 0
            else:
                value = int(value)

            print(f"Current value for {key}: {value}")

            new_value = value + 1

            if new_value * page_size >= cluster_count:
                new_value = 0

            self.redis_db.set(key, str(new_value))
            print(f"Updated value for {key}: {new_value}")
        finally:

            self.release_lock(lock_key, lock_value)

        return value
