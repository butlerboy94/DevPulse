#pragma once

#include <algorithm>
#include <chrono>
#include <numeric>
#include <string>
#include <vector>

namespace devpulse {

struct BenchmarkResult {
    double execution_time_ns;   // mean execution time in nanoseconds
    double execution_time_ms;   // mean execution time in milliseconds
    double median_time_ns;      // middle value across all runs
    double p95_time_ns;         // 95th percentile — worst-case without outliers
    double min_time_ns;         // fastest single run
    double max_time_ns;         // slowest single run
    long long memory_bytes;     // approximate memory change during the benchmark
    int loop_depth;             // max nested loop depth (filled in by the caller)
    int function_calls;         // function call count (filled in by the caller)
    int iterations;             // how many timed runs were performed
};

// Forward declarations — these are implemented in benchmark.cpp
long long get_memory_usage();
int detect_loop_depth(const std::vector<std::string>& tokens);

/**
 * Time any zero-argument callable `iterations` times using a
 * high-precision clock, then return aggregate statistics.
 *
 * One warm-up call is made before timing begins so that CPU caches
 * and Python interpreter state are already "hot" when measurement starts.
 *
 * This is a C++ template, meaning it works with any function-like thing:
 * a plain C++ lambda, a std::function, or (via pybind11) a Python callable.
 */
template<typename Fn>
BenchmarkResult benchmark_callable(Fn&& fn, int iterations = 100) {
    std::vector<double> samples;
    samples.reserve(iterations);

    fn(); // warm-up run — not measured

    long long mem_before = get_memory_usage();

    for (int i = 0; i < iterations; ++i) {
        auto t0 = std::chrono::high_resolution_clock::now();
        fn();
        auto t1 = std::chrono::high_resolution_clock::now();
        samples.push_back(
            std::chrono::duration<double, std::nano>(t1 - t0).count()
        );
    }

    long long mem_after = get_memory_usage();

    double mean = std::accumulate(samples.begin(), samples.end(), 0.0)
                  / static_cast<double>(samples.size());

    std::sort(samples.begin(), samples.end());
    double median = samples[samples.size() / 2];
    double p95    = samples[static_cast<size_t>(samples.size() * 0.95)];

    BenchmarkResult r{};
    r.execution_time_ns = mean;
    r.execution_time_ms = mean / 1.0e6;
    r.median_time_ns    = median;
    r.p95_time_ns       = p95;
    r.min_time_ns       = samples.front();
    r.max_time_ns       = samples.back();
    r.memory_bytes      = (mem_after > 0 && mem_before > 0)
                          ? mem_after - mem_before : 0;
    r.loop_depth        = 0;
    r.function_calls    = 0;
    r.iterations        = iterations;
    return r;
}

} // namespace devpulse
