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
        self._data: OrderedDict = OrderedDict()
        self.stats = Stats()

    def _purge(self):
        now = self.clock()
        for k in [k for k, (_, exp) in self._data.items() if now >= exp]:
            del self._data[k]; self.stats.expirations += 1

    def get(self, key, default=None):
        if key in self._data and self.clock() >= self._data[key][1]:
            del self._data[key]; self.stats.expirations += 1
        if key not in self._data:
            self.stats.misses += 1
            return default
        self.stats.hits += 1
        self._data.move_to_end(key)
        return self._data[key][0]

    def put(self, key, value) -> None:
        self._data[key] = (value, self.clock() + self.ttl)
        self._data.move_to_end(key)
        if len(self._data) > self.capacity:
            self._purge()
        if len(self._data) > self.capacity:
            self._data.popitem(last=False); self.stats.evictions += 1

    def __len__(self) -> int:
        now = self.clock()
        return sum(1 for _, exp in self._data.values() if now < exp)
