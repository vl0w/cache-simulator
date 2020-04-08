from cachesimulator import *

n = 40
stride = 16

vars = create_doubles(0, n * stride)
cache = Cache(4096., 64., 2.)

for j in range(2):
    for i in range(n):
        vars[i * stride].simulate_read(cache)

miss_rate = cache.stats["misses"] / cache.stats["accesses"]
print(miss_rate)
