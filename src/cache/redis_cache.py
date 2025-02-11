import redis
import json

class RedisCache:
    """
    A simple Redis-based cache that serializes data to JSON.
    """
    def __init__(self, host="localhost", port=6379, db=0, expiry_seconds=86400):
        """
        expiry_seconds: cache expiration time in seconds (default = 86400 seconds = 1 day)
        """
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.expiry_seconds = expiry_seconds

    def get(self, key):
        value = self.client.get(key)
        if value is not None:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None

    def set(self, key, value):
        self.client.set(key, json.dumps(value), ex=self.expiry_seconds) 