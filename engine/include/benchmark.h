#pragma once

#include <string>
#include <vector>

namespace devpulse {

struct BenchmarkResult {
    double execution_time_ns;   // nanoseconds
    double execution_time_ms;   // milliseconds
    long long memory_bytes;     // approximate heap delta
    int loop_depth;             // max nested loop depth detected
    int function_calls;         // number of function calls recorded
};

struct LineProfile {
    int line_number;
    double time_ns;
    int hit_count;
};

// Run the provided callable n times and return aggregated timing.
// The callable is a std::function<void()> passed from Python via pybind11.
BenchmarkResult benchmark_execution(const std::string& label, int iterations);

// Return the maximum nested loop depth for a block of pseudocode tokens.
int detect_loop_depth(const std::vector<std::string>& tokens);

// Return current RSS memory in bytes (best-effort, platform-specific).
long long get_memory_usage();

} // namespace devpulse
