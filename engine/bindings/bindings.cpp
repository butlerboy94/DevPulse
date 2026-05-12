#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "benchmark.h"

namespace py = pybind11;

PYBIND11_MODULE(devpulse_engine, m) {
    m.doc() = "DevPulse C++ benchmarking engine";

    py::class_<devpulse::BenchmarkResult>(m, "BenchmarkResult")
        .def_readonly("execution_time_ns", &devpulse::BenchmarkResult::execution_time_ns)
        .def_readonly("execution_time_ms", &devpulse::BenchmarkResult::execution_time_ms)
        .def_readonly("memory_bytes",      &devpulse::BenchmarkResult::memory_bytes)
        .def_readonly("loop_depth",        &devpulse::BenchmarkResult::loop_depth)
        .def_readonly("function_calls",    &devpulse::BenchmarkResult::function_calls)
        .def("__repr__", [](const devpulse::BenchmarkResult& r) {
            return "<BenchmarkResult time_ms=" + std::to_string(r.execution_time_ms) + ">";
        });

    m.def("benchmark_execution", &devpulse::benchmark_execution,
          py::arg("label"), py::arg("iterations") = 100,
          "Run a benchmark and return timing/memory results");

    m.def("detect_loop_depth", &devpulse::detect_loop_depth,
          py::arg("tokens"),
          "Return the maximum nested loop depth from a token stream");

    m.def("get_memory_usage", &devpulse::get_memory_usage,
          "Return current process RSS in bytes");
}
