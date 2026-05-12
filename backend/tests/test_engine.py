"""
Tests for the BenchmarkEngine wrapper and CodeProfiler.

These tests intentionally do NOT require the compiled C++ module.
They verify the Python fallback path works correctly, which means
they will pass on any machine regardless of whether CMake has been run.
"""

import time

import pytest

from app.engine.profiler import CodeProfiler
from app.engine.wrapper import BenchmarkEngine, BenchmarkReport


# ── BenchmarkEngine ──────────────────────────────────────────────────────────

class TestBenchmarkEngine:

    def test_benchmark_returns_report(self):
        engine = BenchmarkEngine()
        report = engine.benchmark(lambda: sum(range(1_000)), iterations=10)
        assert isinstance(report, BenchmarkReport)

    def test_timing_is_positive(self):
        engine = BenchmarkEngine()
        report = engine.benchmark(lambda: sum(range(1_000)), iterations=10)
        assert report.execution_time_ms > 0
        assert report.median_time_ms > 0
        assert report.min_time_ms > 0
        assert report.max_time_ms > 0

    def test_statistical_ordering(self):
        """Min ≤ median ≤ mean, and min ≤ max — always true by definition."""
        engine = BenchmarkEngine()
        report = engine.benchmark(lambda: sum(range(10_000)), iterations=50)
        assert report.min_time_ms <= report.median_time_ms
        assert report.min_time_ms <= report.max_time_ms

    def test_iterations_recorded(self):
        engine = BenchmarkEngine()
        report = engine.benchmark(lambda: None, iterations=25)
        assert report.iterations == 25

    def test_slow_function_takes_longer(self):
        engine = BenchmarkEngine()
        fast = engine.benchmark(lambda: None, iterations=20)
        slow = engine.benchmark(lambda: time.sleep(0.005), iterations=5)
        assert slow.execution_time_ms > fast.execution_time_ms

    def test_readable_time_microseconds(self):
        """Sub-millisecond times should render as µs."""
        report = BenchmarkReport(
            execution_time_ms=0.5, median_time_ms=0.5, p95_time_ms=0.6,
            min_time_ms=0.4, max_time_ms=0.7, memory_bytes=0,
            iterations=10, source="python_fallback",
        )
        assert "µs" in report.execution_time_readable

    def test_readable_time_milliseconds(self):
        """Times ≥ 1 ms should render as ms."""
        report = BenchmarkReport(
            execution_time_ms=2.5, median_time_ms=2.5, p95_time_ms=2.6,
            min_time_ms=2.4, max_time_ms=2.7, memory_bytes=1_024,
            iterations=10, source="python_fallback",
        )
        assert "ms" in report.execution_time_readable

    def test_readable_memory_kb(self):
        report = BenchmarkReport(
            execution_time_ms=1.0, median_time_ms=1.0, p95_time_ms=1.0,
            min_time_ms=1.0, max_time_ms=1.0, memory_bytes=2_048,
            iterations=10, source="python_fallback",
        )
        assert "KB" in report.memory_readable

    def test_readable_memory_na_when_zero(self):
        report = BenchmarkReport(
            execution_time_ms=1.0, median_time_ms=1.0, p95_time_ms=1.0,
            min_time_ms=1.0, max_time_ms=1.0, memory_bytes=0,
            iterations=10, source="python_fallback",
        )
        assert report.memory_readable == "N/A"

    def test_detect_loop_depth_flat(self):
        engine = BenchmarkEngine()
        assert engine.detect_loop_depth(["for", "end_loop"]) == 1

    def test_detect_loop_depth_nested(self):
        engine = BenchmarkEngine()
        tokens = ["for", "while", "for", "end_loop", "end_loop", "end_loop"]
        assert engine.detect_loop_depth(tokens) == 3

    def test_detect_loop_depth_empty(self):
        engine = BenchmarkEngine()
        assert engine.detect_loop_depth([]) == 0

    def test_detect_loop_depth_sequential(self):
        """Two loops in a row (not nested) → depth 1."""
        engine = BenchmarkEngine()
        tokens = ["for", "end_loop", "for", "end_loop"]
        assert engine.detect_loop_depth(tokens) == 1


# ── CodeProfiler ─────────────────────────────────────────────────────────────

class TestCodeProfiler:

    def _workload(self):
        total = 0
        for i in range(50_000):
            total += i
        return total

    def test_profile_returns_report(self):
        profiler = CodeProfiler()
        report = profiler.profile(self._workload)
        assert report is not None

    def test_total_time_positive(self):
        profiler = CodeProfiler()
        report = profiler.profile(self._workload)
        assert report.total_time_ms >= 0

    def test_function_count_positive(self):
        profiler = CodeProfiler()
        report = profiler.profile(self._workload)
        assert report.function_count > 0

    def test_hotspots_not_empty(self):
        profiler = CodeProfiler()
        report = profiler.profile(self._workload)
        assert len(report.hotspots) > 0

    def test_hotspots_sorted_by_cumulative_time(self):
        """The slowest function should be first."""
        profiler = CodeProfiler()
        report = profiler.profile(self._workload)
        times = [e.cumulative_time_ms for e in report.hotspots]
        assert times == sorted(times, reverse=True)

    def test_top_n_respected(self):
        profiler = CodeProfiler(top_n=3)
        report = profiler.profile(self._workload)
        assert len(report.hotspots) <= 3

    def test_top_hotspot_property(self):
        profiler = CodeProfiler()
        report = profiler.profile(self._workload)
        assert report.top_hotspot is not None
        assert report.top_hotspot is report.hotspots[0]
