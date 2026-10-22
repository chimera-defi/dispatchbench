Users report three bugs in the `kvcache` package in this repository. Work in the current directory.

1. An entry is still returned at exactly the moment it should expire. The docstring of `TTLCache` says an entry written at time t is gone from time t + ttl on.
2. Overwriting an existing key with `put` does not count as using it: the overwritten key can be evicted before keys that were used less recently.
3. `stats.hits` goes up when `get` finds an expired entry. A lookup of an expired entry must count as a miss (and as an expiration), never as a hit.

There is a fourth, related problem: when the cache is full, `put` can evict a live entry even though an expired entry is still taking up a slot. Expired entries must never cause a live entry to be evicted. Evicting a live entry counts in `stats.evictions`; dropping an expired one counts in `stats.expirations` instead.

`len(cache)` must report only live (unexpired) entries.

Fix all of these, keep the public API unchanged, and add regression tests in `tests/test_regressions.py`. Run `python3 -m pytest -q`; all tests must pass.
