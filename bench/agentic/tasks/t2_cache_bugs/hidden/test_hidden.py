from kvcache.cache import TTLCache
from kvcache.clock import FakeClock


def test_expires_at_boundary():
    clk = FakeClock(100); c = TTLCache(3, 5, clk); c.put("a", 1)
    clk.advance(4); assert c.get("a") == 1
    clk.advance(1); assert c.get("a") is None
    assert c.stats.hits == 1 and c.stats.misses == 1 and c.stats.expirations == 1


def test_put_refreshes_recency_and_ttl():
    clk = FakeClock(); c = TTLCache(2, 10, clk)
    c.put("a", 1); c.put("b", 2); c.put("a", 3); c.put("c", 4)
    assert c.get("a") == 3 and c.get("b") is None and c.get("c") == 4
    clk2 = FakeClock(); d = TTLCache(2, 10, clk2); d.put("x", 1); clk2.advance(8); d.put("x", 2); clk2.advance(5)
    assert d.get("x") == 2


def test_expired_lookup_is_a_miss():
    clk = FakeClock(); c = TTLCache(2, 3, clk); c.put("a", 1); clk.advance(10)
    assert c.get("a", "d") == "d" and c.get("a", "d") == "d"
    assert (c.stats.hits, c.stats.misses, c.stats.expirations) == (0, 2, 1)
    assert c.stats.hit_rate() == 0.0


def test_expired_entry_never_evicts_live_one():
    clk = FakeClock(); c = TTLCache(2, 10, clk)
    c.put("old", 0); clk.advance(5); c.put("live", 1); clk.advance(5)   # old expires now, live has 5 s left
    c.get("live"); c.put("new", 2)
    assert c.get("live") == 1 and c.get("new") == 2
    assert c.stats.evictions == 0 and c.stats.expirations == 1


def test_lru_victim_is_least_recent_live():
    clk = FakeClock(); c = TTLCache(3, 100, clk)
    for k in "abc": c.put(k, k)
    c.get("a"); c.get("b"); c.put("d", "d")
    assert c.get("c") is None and [c.get(k) for k in "abd"] == ["a", "b", "d"]
    assert c.stats.evictions == 1


def test_len_counts_live_only():
    clk = FakeClock(); c = TTLCache(5, 4, clk)
    c.put("a", 1); clk.advance(2); c.put("b", 2); assert len(c) == 2
    clk.advance(2); assert len(c) == 1
    clk.advance(2); assert len(c) == 0
