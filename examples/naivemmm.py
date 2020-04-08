from cachesimulator import *

cache = Cache(32, 16, 1)  # directly mapped cache

n = 100
A = create_doubles(0, n * n)
B = create_doubles(8 * n * n, n * n)
C = create_doubles(2 * 8 * n * n, n * n)

for i in range(n):
    for j in range(n):
        for k in range(n):
            C[n * i + j].simulate_read(cache)
            A[n * i + k].simulate_read(cache)
            B[n * k + j].simulate_read(cache)
            C[n * i + j].simulate_write(cache)

miss_rate = cache.stats["misses"] / cache.stats["accesses"]
print(miss_rate)
