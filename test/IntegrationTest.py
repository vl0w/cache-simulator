import unittest
from cachesimulator import *


class MyTestCase(unittest.TestCase):
    def test_with_associativity(self):
        variables = create_floats(0, 3)
        cache = Cache(8, 4, 2)

        variables[0].simulate_read(cache)
        self.assertTrue(cache.is_in_cache(variables[0]))
        self.assertFalse(cache.is_in_cache(variables[1]))
        self.assertFalse(cache.is_in_cache(variables[2]))

        variables[1].simulate_read(cache)
        self.assertTrue(cache.is_in_cache(variables[0]))
        self.assertTrue(cache.is_in_cache(variables[1]))
        self.assertFalse(cache.is_in_cache(variables[2]))

        variables[2].simulate_read(cache)
        self.assertFalse(cache.is_in_cache(variables[0]))
        self.assertTrue(cache.is_in_cache(variables[1]))
        self.assertTrue(cache.is_in_cache(variables[2]))


if __name__ == '__main__':
    unittest.main()
