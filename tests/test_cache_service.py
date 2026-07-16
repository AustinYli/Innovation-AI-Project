import unittest

from app.services.cache_service import TTLCache


class CacheServiceTests(unittest.TestCase):
    def test_cache_returns_copy_and_counts_hits(self):
        cache = TTLCache(ttl_seconds=60)
        cache.set("wallet:test", {"value": ["original"]})

        first = cache.get("wallet:test")
        first["value"].append("changed")
        second = cache.get("wallet:test")

        self.assertEqual(second, {"value": ["original"]})
        stats = cache.stats()
        self.assertEqual(stats["hits"], 2)
        self.assertEqual(stats["misses"], 0)
        self.assertEqual(stats["entries"], 1)

    def test_cache_miss_when_disabled(self):
        cache = TTLCache(ttl_seconds=0)
        cache.set("wallet:test", {"value": 1})

        self.assertIsNone(cache.get("wallet:test"))
        self.assertFalse(cache.stats()["enabled"])


if __name__ == "__main__":
    unittest.main()
