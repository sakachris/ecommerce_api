from datetime import timedelta

import redis
from django.conf import settings


class RedisTokenStore:
    """
    A tiny wrapper around Redis to store one-time JWT jtis with TTL.
    """
    def __init__(self):
        self.client = redis.StrictRedis.from_url(
            settings.REDIS_URL, decode_responses=True
        )

    def _key(self, token_type: str, jti: str) -> str:
        return f"jwt:{token_type}:{jti}"

    def store(self, token_type: str, jti: str, ttl: timedelta):
        # SET key value NX EX <seconds> – ensures no overwrite (optional)
        self.client.set(
            self._key(token_type, jti),
            "1",
            ex=int(ttl.total_seconds()),
            nx=True
        )

    def pop(self, token_type: str, jti: str) -> bool:
        """
        Atomically get & delete the key to prevent reuse.
        Use GETDEL if Redis >= 6.2, else a pipeline.
        """
        key = self._key(token_type, jti)
        try:
            # Try GETDEL (Redis 6.2+)
            val = self.client.execute_command("GETDEL", key)
            return val is not None
        except redis.ResponseError:
            # Fallback pipeline for older Redis versions
            pipe = self.client.pipeline()
            pipe.get(key)
            pipe.delete(key)
            val, _ = pipe.execute()
            return val is not None

    def exists(self, token_type: str, jti: str) -> bool:
        return self.client.exists(self._key(token_type, jti)) == 1
