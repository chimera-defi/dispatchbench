from collections import OrderedDict

from .stats import Stats


class TTLCache:
    """Least-recently-used cache with a per-entry time to live.

    `capacity` is the maximum number of live entries. `ttl` is in seconds: an entry written at time t
    expires at time t + ttl, and is gone from that instant on. `clock` is a zero-argument callable
    returning the current time.
    """

    def __init__(self, capacity: int, ttl: int, clock):
        if capacity < 1 or ttl < 1:
            raise ValueError("capacity and ttl must be >= 1")
        self.capacity, self.ttl, self.clock = capacity, ttl, clock
        self._data: OrderedDict = OrderedDict()  # key -> (value, expires_at); last item is most recently used
        self.stats = Stats()

    def get(self, key, default=None):
        if key not in self._data:
            self.stats.misses += 1
            return default
        value, expires_at = self._data[key]
        self.stats.hits += 1
        if self.clock() > expires_at:
            del self._data[key]
            self.stats.expirations += 1
            return default
        self._data.move_to_end(key)
        return value

    def put(self, key, value) -> None:
        self._data[key] = (value, self.clock() + self.ttl)
        if len(self._data) > self.capacity:
            self._data.popitem(last=False)
            self.stats.evictions += 1

    def __len__(self) -> int:
        return len(self._data)
