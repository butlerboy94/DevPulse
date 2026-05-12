#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "benchmark.h"

namespace py = pybind11;

PYBIND11_MODULE(devpulse_engine, m) {
    m.doc() = "DevPulse C++ benchmarking engine";

    py::class_<devpulse::BenchmarkResult>(m, "BenchmarkResult")
        .def_readonly("execution_time_ns", &devpulse::BenchmarkResult::execution_time_ns)
        .def_readonly("execution_time_ms", &devpulse::BenchmarkResult::execution_time_ms)
        .def_readonly("median_time_ns",    &devpulse::BenchmarkResult::median_time_ns)
        .def_readonly("p95_time_ns",       &devpulse::BenchmarkResult::p95_time_ns)
        .def_readonly("min_time_ns",       &devpulse::BenchmarkResult::min_time_ns)
        .def_readonly("max_time_ns",       &devpulse::BenchmarkResult::max_time_ns)
        .def_readonly("memory_bytes",      &devpulse::BenchmarkResult::memory_bytes)
        .def_readonly("loop_depth",        &devpulse::BenchmarkResult::loop_depth)
        .def_readonly("function_calls",    &devpulse::BenchmarkResult::function_calls)
        .def_readonly("iterations",        &devpulse::BenchmarkResult::iterations)
        .def("__repr__", [](const devpulse::BenchmarkResult& r) {
            return "<BenchmarkResult mean=" + std::to_string(r.execution_time_ms)
                 + "ms median=" + std::to_string(r.median_time_ns / 1.0e6)
                 + "ms p95=" + std::to_string(r.p95_time_ns / 1.0e6) + "ms>";
        });

    // Accept any Python callable, wrap it in a C++ lambda, and time it.
    m.def("benchmark_callable",
        [](py::object fn, int iterations) {
            return devpulse::benchmark_callable(
                [&fn]() { fn(); },
                iterations
            );
        },
        py::arg("fn"),
        py::arg("iterations") = 100,
        "Time a Python callable using a high-precision C++ clock. "
        "Returns a BenchmarkResult with mean, median, p95, min, max timing and memory delta."
    );

    m.def("detect_loop_depth", &devpulse::detect_loop_depth,
          py::arg("tokens"),
          "Return the maximum nested loop depth from a list of keyword tokens.");

    m.def("get_memory_usage", &devpulse::get_memory_usage,
          "Return the current process memory usage in bytes.");
}
