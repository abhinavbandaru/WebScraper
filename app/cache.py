import redis
import json

class Cache:
    def __init__(self):
        self.client = redis.StrictRedis(host='localhost', port=6379, db=0)

    def get(self, key: str):
        cached_value = self.client.get(key)
        if cached_value:
            return json.loads(cached_value)
        return None

    def set(self, key: str, value: dict):
        self.client.set(key, json.dumps(value), ex=60*60)
