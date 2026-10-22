from kvcache.cache import TTLCache
from kvcache.clock import FakeClock


def test_basic_get_put():
    c = TTLCache(2, 10, FakeClock())
    c.put("a", 1)
    assert c.get("a") == 1 and c.get("zz", "none") == "none"


def test_lru_eviction():
    c = TTLCache(2, 10, FakeClock())
    c.put("a", 1); c.put("b", 2); c.get("a"); c.put("c", 3)
    assert c.get("b") is None and c.get("a") == 1 and c.get("c") == 3
