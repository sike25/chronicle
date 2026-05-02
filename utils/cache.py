import json
import os
import redis

from log import setup_logging

logger = setup_logging()

TTL_SECONDS = 7 * 24 * 60 * 60  # one week
KEY_PREFIX  = "chronicle:"


class QueryCache:
    """
    Redis-backed cache for enriched Chronicle pipeline results.

    Keyed by normalized query string, prefixed with 'chronicle:'.
    Entries expire automatically after one week (TTL_SECONDS).
    """

    def __init__(self, ttl: int = TTL_SECONDS):
        self._ttl    = ttl
        self._client = redis.from_url(
            os.environ["REDIS_URL"],
            decode_responses=True,
        )
        logger.info("Cache: connected to Redis.")

    ### WRITE API

    def set(self, query: str, events: list):
        """
        Store the full SSE event list for a query.
        Events are the list of {"type": ..., "data": ...} dicts from the job store.
        The 'done' event is included so replays terminate cleanly.
        """
        key   = self._key(query)
        value = json.dumps({
            "events":         events,
            "original_query": query,
        })
        self._client.setex(key, self._ttl, value)
        logger.info(f"Cache: stored {len(events)} events for '{query}' (expires in {self._ttl // 86400}d)")

    def clear(self):
        """Wipe all Chronicle cache entries."""
        keys  = self._client.keys(f"{KEY_PREFIX}*")
        count = len(keys)
        if keys:
            self._client.delete(*keys)
        logger.info(f"Cache: cleared {count} entries")


    ### READ API
    def get(self, query: str) -> list | None:
        """
        Returns a copy of the cached event list, or None on miss or expiry.
        TTL expiry is handled automatically by Redis.
        """
        key   = self._key(query)
        value = self._client.get(key)
        if value is None:
            logger.info(f"Cache: MISS for '{query}'")
            return None
        entry  = json.loads(value)
        events = entry["events"]
        logger.info(f"Cache: HIT for '{query}' — {len(events)} events")
        return events

    @property
    def size(self) -> int:
        return len(self._client.keys(f"{KEY_PREFIX}*"))



    ### HELPERS
    def _key(self, query: str) -> str:
        return f"{KEY_PREFIX}{query.strip().lower()}"


# global instance
cache = QueryCache()