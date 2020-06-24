import unittest
from cachesimulator import *


class MyTestCase(unittest.TestCase):

    def test_singlelevel_associativity(self):
        ms = MemorySystem()
        cache = Cache(8, 4, 2)
        ms.add_cache(cache)

        variables = ms.create_floats(3)

        variables[0].read()
        self.assertTrue(cache.is_in_cache(variables[0]))
        self.assertFalse(cache.is_in_cache(variables[1]))
        self.assertFalse(cache.is_in_cache(variables[2]))

        variables[1].read()
        self.assertTrue(cache.is_in_cache(variables[0]))
        self.assertTrue(cache.is_in_cache(variables[1]))
        self.assertFalse(cache.is_in_cache(variables[2]))

        variables[2].read()
        self.assertFalse(cache.is_in_cache(variables[0]))
        self.assertTrue(cache.is_in_cache(variables[1]))
        self.assertTrue(cache.is_in_cache(variables[2]))

    def test_supports_spatial_locality(self):
        ms = MemorySystem()
        variables = ms.create_floats(2)
        ms.add_cache(Cache(32, 8))

        variables[0].read()

        self.assertTrue(ms.caches[0].is_in_cache(variables[1]))

    def test_multilevel_noassociativity(self):
        ms = MemorySystem()
        ms.add_cache(Cache(4, 4, 1))
        ms.add_cache(Cache(8, 4, 2))
        cache0 = ms.caches[0]
        cache1 = ms.caches[1]

        variables = ms.create_floats(2)
        f1 = variables[0]
        f2 = variables[1]

        f1.read()
        self.assertEqual(cache0.stats.hits, 0)
        self.assertEqual(cache1.stats.hits, 0)
        self.assertEqual(cache0.stats.misses, 1)
        self.assertEqual(cache1.stats.misses, 1)
        self.assertEqual(cache0.stats.accesses, 1)
        self.assertEqual(cache1.stats.accesses, 1)
        self.assertTrue(cache0.is_in_cache(f1))
        self.assertTrue(cache1.is_in_cache(f1))

        f1.read()
        self.assertEqual(cache0.stats.hits, 1)
        self.assertEqual(cache1.stats.hits, 0)
        self.assertEqual(cache0.stats.misses, 1)
        self.assertEqual(cache1.stats.misses, 1)
        self.assertEqual(cache0.stats.accesses, 2)
        self.assertEqual(cache1.stats.accesses, 1)

        f2.read()
        self.assertEqual(cache0.stats.hits, 1)
        self.assertEqual(cache1.stats.hits, 0)
        self.assertEqual(cache0.stats.misses, 2)
        self.assertEqual(cache1.stats.misses, 2)
        self.assertEqual(cache0.stats.accesses, 3)
        self.assertEqual(cache1.stats.accesses, 2)
        self.assertFalse(cache0.is_in_cache(f1))
        self.assertTrue(cache1.is_in_cache(f1))
        self.assertTrue(cache0.is_in_cache(f2))
        self.assertTrue(cache1.is_in_cache(f2))

        f1.read()
        self.assertEqual(cache0.stats.hits, 1)
        self.assertEqual(cache1.stats.hits, 1)
        self.assertEqual(cache0.stats.misses, 3)
        self.assertEqual(cache1.stats.misses, 2)
        self.assertEqual(cache0.stats.accesses, 4)
        self.assertEqual(cache1.stats.accesses, 3)
        self.assertTrue(cache0.is_in_cache(f1))
        self.assertTrue(cache1.is_in_cache(f1))
        self.assertFalse(cache0.is_in_cache(f2))
        self.assertTrue(cache1.is_in_cache(f2))


if __name__ == '__main__':
    unittest.main()
