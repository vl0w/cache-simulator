import unittest
from cachesimulator import Cache

class CacheConstructor(unittest.TestCase):
    def test_block_size_is_exponential_with_base_2(self):
        self.assertRaises(AttributeError, Cache, 32, 3)

    def test_total_size_is_exponential_with_base_2(self):
        self.assertRaises(AttributeError, Cache, 3, 2)

    def test_associativity_is_exponential_with_base_2(self):
        self.assertRaises(AttributeError, Cache, 4, 2, 3)



if __name__ == '__main__':
    unittest.main()
