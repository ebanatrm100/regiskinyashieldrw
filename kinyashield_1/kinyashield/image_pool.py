"""Shared plumbing that lets Image Studio serve many people at once (pure Python, thread-safe, one instance per server process):

  Cache     LRU + time-to-live + byte cap: identical requests are answered instantly and do not use provider quota.
  Health    per-service circuit breaker: a service that is out of quota or failing is skipped for a growing cool-down, then retried.
  Gate      limits how many generations run at the same time in this process; others wait in line (bounded) instead of crashing the server.
  Limiter   fair-use sliding window per visitor, so one person cannot use up the quota of everyone else.
  Counters  simple statistics for the status line.

Honest limits: this spreads load and avoids waste, but it cannot create capacity. The number of pictures per minute is set by your provider quotas
(number of keys and plan) and by the hosting plan (CPU/RAM). Streamlit Community Cloud is a small shared server; for thousands of simultaneous users,
add several keys/services and run the app on a bigger host. No secrets are stored here and nothing is written to disk."""
from __future__ import annotations
import hashlib, threading, time
from collections import OrderedDict, deque

_LOCK = threading.RLock()


# ------------------------------------------------------------------ cache
class Cache:
    def __init__(self, max_bytes=120 * 1024 * 1024, ttl=6 * 3600, max_items=400):
        self.max_bytes, self.ttl, self.max_items = max_bytes, ttl, max_items
        self._d = OrderedDict()      # key -> (expires, size, value)
        self._bytes = 0

    @staticmethod
    def key(*parts):
        return hashlib.sha256("\x1f".join(map(str, parts)).encode("utf-8")).hexdigest()

    def get(self, key):
        with _LOCK:
            it = self._d.get(key)
            if not it:
                return None
            if it[0] < time.time():
                self._drop(key)
                return None
            self._d.move_to_end(key)
            return it[2]

    def put(self, key, value, size):
        if size > self.max_bytes // 2:
            return
        with _LOCK:
            if key in self._d:
                self._drop(key)
            self._d[key] = (time.time() + self.ttl, size, value)
            self._bytes += size
            while self._d and (self._bytes > self.max_bytes or len(self._d) > self.max_items):
                self._drop(next(iter(self._d)))

    def _drop(self, key):
        it = self._d.pop(key, None)
        if it:
            self._bytes -= it[1]

    def stats(self):
        with _LOCK:
            return {"items": len(self._d), "bytes": self._bytes}

    def clear(self):
        with _LOCK:
            self._d.clear(); self._bytes = 0


# ------------------------------------------------------------------ service health (circuit breaker)
COOLDOWN = {"quota": (120, 1800), "auth": (900, 3600), "busy": (15, 240), "other": (30, 600)}   # kind -> (first, maximum) seconds


class Health:
    def __init__(self, clock=time.time):
        self._s = {}            # name -> [fail_count, open_until]
        self._clock = clock

    def available(self, name):
        with _LOCK:
            s = self._s.get(name)
            return not s or s[1] <= self._clock()

    def wait(self, name):
        with _LOCK:
            s = self._s.get(name)
            return max(0.0, s[1] - self._clock()) if s else 0.0

    def ok(self, name):
        with _LOCK:
            self._s.pop(name, None)

    def fail(self, name, kind="other"):
        first, top = COOLDOWN.get(kind, COOLDOWN["other"])
        with _LOCK:
            n = (self._s.get(name) or [0, 0])[0] + 1
            self._s[name] = [n, self._clock() + min(top, first * (2 ** (n - 1)))]

    def snapshot(self):
        with _LOCK:
            now = self._clock()
            return {k: max(0.0, v[1] - now) for k, v in self._s.items()}

    def reset(self):
        with _LOCK:
            self._s.clear()


def classify(message):
    """kind of a (secret-free) failure message: quota / auth / busy / other."""
    m = (message or "").lower()
    if any(w in m for w in ("quota", "429", "rate limit", "resource_exhausted", "too many")):
        return "quota"
    if any(w in m for w in ("401", "403", "404", "key rejected", "not allowed", "not available for this key", "no image model")):
        return "auth"
    if any(w in m for w in ("503", "502", "504", "busy", "timeout", "timed out", "urlerror", "overloaded", "service error", "500")):
        return "busy"
    return "other"


# ------------------------------------------------------------------ concurrency gate with a bounded wait
class Gate:
    def __init__(self, size=6):
        self.size = max(1, int(size))
        self._sem = threading.BoundedSemaphore(self.size)
        self._waiting = 0
        self._active = 0

    def acquire(self, timeout=45.0):
        with _LOCK:
            self._waiting += 1
        try:
            ok = self._sem.acquire(timeout=timeout)
        finally:
            with _LOCK:
                self._waiting -= 1
        if ok:
            with _LOCK:
                self._active += 1
        return ok

    def release(self):
        with _LOCK:
            self._active = max(0, self._active - 1)
        self._sem.release()

    def stats(self):
        with _LOCK:
            return {"active": self._active, "waiting": self._waiting, "size": self.size}


# ------------------------------------------------------------------ fair-use limiter
class Limiter:
    def __init__(self, clock=time.time):
        self._h = {}
        self._clock = clock

    def check(self, who, per_minute=6, per_hour=40, cost=1):
        """(allowed, seconds_to_wait). Records the use when allowed. A limit of 0 means unlimited."""
        now = self._clock()
        with _LOCK:
            q = self._h.setdefault(who, deque())
            while q and q[0] < now - 3600:
                q.popleft()
            last_min = [t for t in q if t >= now - 60]
            if per_minute and len(last_min) + cost > per_minute:
                return False, max(1.0, 60 - (now - last_min[0]))
            if per_hour and len(q) + cost > per_hour:
                return False, max(1.0, 3600 - (now - q[0]))
            for _ in range(cost):
                q.append(now)
            if len(self._h) > 5000:                     # forget old visitors
                for k in [k for k, v in self._h.items() if not v or v[-1] < now - 3600][:2500]:
                    self._h.pop(k, None)
            return True, 0.0


# ------------------------------------------------------------------ single flight: identical requests at the same moment share one generation
class SingleFlight:
    def __init__(self):
        self._ev = {}

    def begin(self, key):
        """(is_leader, event). The leader generates; followers wait on the event, then read the shared cache."""
        with _LOCK:
            ev = self._ev.get(key)
            if ev is not None:
                return False, ev
            ev = threading.Event()
            self._ev[key] = ev
            return True, ev

    def done(self, key):
        with _LOCK:
            ev = self._ev.pop(key, None)
        if ev is not None:
            ev.set()


# ------------------------------------------------------------------ shared instances and counters
CACHE = Cache()
HEALTH = Health()
LIMITER = Limiter()
GATE = Gate()
FLIGHT = SingleFlight()
COUNTERS = {"requests": 0, "cache_hits": 0, "images": 0, "failures": 0, "busy": 0}
_ROT = [0]


def count(name, n=1):
    with _LOCK:
        COUNTERS[name] = COUNTERS.get(name, 0) + n


def rotate():
    """A rising number used to start at a different key each time, spreading load evenly over all keys."""
    with _LOCK:
        _ROT[0] += 1
        return _ROT[0]


def configure(max_concurrent=None, cache_mb=None, ttl=None):
    global GATE
    with _LOCK:
        if max_concurrent and int(max_concurrent) != GATE.size:
            GATE = Gate(int(max_concurrent))
        if cache_mb:
            CACHE.max_bytes = int(cache_mb) * 1024 * 1024
        if ttl:
            CACHE.ttl = int(ttl)
