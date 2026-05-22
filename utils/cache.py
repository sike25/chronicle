import json
import os
import redis

from utils.log import setup_logging

logger = setup_logging()

TTL_SECONDS = 7 * 24 * 60 * 60  # one week
KEY_PREFIX  = "chronicle:"


class QueryCache:
    """
    Redis-backed cache for enriched Chronicle pipeline results.

    Keyed by normalized query string, 
    in the dated form 'chronicle:QUERY=query string_FROM=YYYY-MM-DD_TO=YYYY-MM-DD', 
    and the undated form 'chronicle:QUERY=query string'.
    Entries expire automatically after one week (TTL_SECONDS).

    If Redis fails to start, the cache is degraded, and the run is treated as a cache miss.
    """

    def __init__(self, ttl: int = TTL_SECONDS):
        self._ttl    = ttl
        self._client = None

        redis_url = os.environ.get("REDIS_URL", "").strip()
        if not redis_url:
            logger.error("Cache: REDIS_URL not set — cache disabled.")
            return
        
        try:
            client = redis.from_url(redis_url, decode_responses=True, socket_connect_timeout=2)
            client.ping()
            self._client = client
            logger.info("Cache: connected to Redis.")
        except Exception as e:
            logger.error(
                f"Cache: Redis unavailable ({e}) — "
                "cache disabled. Pipeline will run fresh on every request."
            )

    @property
    def _available(self) -> bool:
        return self._client is not None

    ### WRITE API

    def set(self, query: str, events: list,  start_date, end_date):
        """
        Store the full SSE event list for a query.
        Events are the list of {"type": ..., "data": ...} dicts from the job store.
        The 'done' event is included so replays terminate cleanly.
        No-op if Redis is unavailable.
        """
        if not self._available:
            return

        try:
            key   = self._key(query, start_date, end_date)
            value = json.dumps({
                "events":         events,
                "original_query": query,
            })
            self._client.setex(key, self._ttl, value)
            logger.info(f"Cache: stored {len(events)} events for '{query}' (expires in {self._ttl // 86400}d)")
        except Exception as e:
            logger.error(f"Cache: set failed for '{query}': {e}")

    def clear(self):
        """Wipe all Chronicle cache entries. No-op if Redis is unavailable."""
        if not self._available:
            return
        
        try:
            keys  = self._client.keys(f"{KEY_PREFIX}*")
            count = len(keys)
            if keys:
                self._client.delete(*keys)
            logger.info(f"Cache: cleared {count} entries")
        except Exception as e:
            logger.error(f"Cache: clear failed: {e}")


    ### READ API
    def get(self, query: str, start_date, end_date) -> list | None:
        """
        Returns a copy of the cached event list, or None on miss, expiry or Redis failure.
        TTL expiry is handled automatically by Redis.
        """
        if not self._available:
            return None
        
        try:
            key   = self._key(query, start_date, end_date)
            value = self._client.get(key)
            if value is None:
                logger.info(f"Cache: MISS for '{query}'")
                return None
            entry  = json.loads(value)
            events = entry["events"]
            logger.info(f"Cache: HIT for '{query}' — {len(events)} events")
            return events        
        except Exception as e:
            logger.error(f"Cache: get failed for '{query}': {e}")
            return None
        

    @property
    def size(self) -> int:
        if not self._available:
            return 0  
        try:
            return len(self._client.keys(f"{KEY_PREFIX}*"))
        except Exception:
            return 0



    ### HELPERS
    def _key(self, query: str, start_date, end_date) -> str:
        slug = query.strip().lower().replace(" ", "-")
        key  = f"{KEY_PREFIX}QUERY={slug}"
        if start_date and end_date:
            key += f"_FROM={start_date}_TO={end_date}"
        return key


# global instance
cache = QueryCache()