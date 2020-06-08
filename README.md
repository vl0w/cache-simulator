# The cache simulator
We all love the $ (cache). [Caches](https://en.wikipedia.org/wiki/Cache_(computing)) makes our programs magically run faster. 
However, writing cache friendly code can be hard.

With this tool, you can simulate the reads/writes of your program and find out whether you exploit the full power of your cache.

# Example (under construction)
The following example demonstrates the capabilities of the cache simulator. 
It is inspired by the lecture [Advanced Systems Lab](https://acl.inf.ethz.ch/teaching/fastcode/) at ETH Zurich.

Here is some fancy C code ~~for computing breathtaking machine learning stuff~~ for naïve triple-loop matrix-matrix-multiplication 
(C=A*B where A,B,C have n rows and n columns).
```c
void mmm(double* A, double* B, double* C, int n, int stride) {
    for(int i=0;i<n;++i) {
        for(int j=0;j<n;++j) {
            for(int k=0;k<n;++k) {
                C[n*i + j] = C[n*i + j] + A[n*i + k] * B[n*k + j];
            }
        }
    }
}
```
We have a cache of size 1024 Bytes, each block has 64 Bytes and we have associativity 1. Assume A,B,C are in row-major order.

How large is our cache miss rate? Well, this requires some thinking. As a cache connoisseur, you know that this is
not exactly the kind of work you want to do. Just simulate it instead!

Here you go:
tbd


# Roadmap
Things/ideas to do. This is also a list of features which are definitely missining.

- [ ] Improve performance/memory consumption (pretty poor right now)
- [x] Multi-level caches
- [ ] Cache coherence / support for multiple processors
- [ ] Different replacements strategies (currently, only LRU is supported)
