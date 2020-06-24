import sys, os
sys.path.append(os.getcwd() + '/..')
from cachesimulator.cachesimulator import *

n = 100
ms = MemorySystem()
ms.add_cache(Cache(128, 64, 1))
A = ms.create_doubles(n * n)
B = ms.create_doubles(n * n)
C = ms.create_doubles(n * n)

c = 0
for i in range(n):
    for j in range(n):
        for k in range(n):
            C[n * i + j].read()
            A[n * i + k].read()
            B[n * k + j].read()
            C[n * i + j].write()

miss_rate = ms.caches[0].stats.misses / ms.caches[0].stats.accesses
print(miss_rate)
