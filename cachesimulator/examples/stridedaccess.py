import sys, os
sys.path.append(os.getcwd() + '/..')
from cachesimulator.cachesimulator import *

n = 40
stride = 16

ms = MemorySystem()
ms.add_cache(Cache(4096, 64, 2, description="L1"))
ms.add_cache(Cache(4096, 64, 2, description="L2"))

variables = ms.create_doubles(n * stride)

for j in range(2):
    for i in range(n):
        variables[i * stride].read()

for cache in ms.caches:
    miss_rate = cache.stats.misses / cache.stats.accesses
    print("{} miss rate: {}".format(cache.description, miss_rate))
