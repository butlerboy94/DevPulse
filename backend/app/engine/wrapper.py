from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, List


@dataclass
class BenchmarkReport:
    """The results of timing a piece of code — all measurements in milliseconds."""
    execution_time_ms: float   # average across all runs
    median_time_ms: float      # middle value (less affected by outliers)
    p95_time_ms: float         # worst-case ignoring the top 5% slowest runs
    min_time_ms: float         # fastest single run
    max_time_ms: float         # slowest single run
    memory_bytes: int          # approximate memory used during the run
    iterations: int            # how many times the code was run
    source: str                # "cpp_engine" if C++ was used, "python_fallback" if not

    @property
    def execution_time_readable(self) -> str:
        """Return a human-friendly time string, e.g. '1.23 ms' or '456.78 µs'."""
        if self.execution_time_ms < 1.0:
            return f"{self.execution_time_ms * 1_000:.2f} µs"
        return f"{self.execution_time_ms:.3f} ms"

    @property
    def memory_readable(self) -> str:
        """Return a human-friendly memory string, e.g. '1.23 MB' or '456 KB'."""
        if self.memory_bytes <= 0:
            return "N/A"
        kb = self.memory_bytes / 1_024
        if kb < 1_024:
            return f"{kb:.1f} KB"
        return f"{kb / 1_024:.2f} MB"


class BenchmarkEngine:
    """
    Times how long a Python function takes to run.

    Tries to use the compiled C++ engine for nanosecond-precision measurements.
    If the C++ engine has not been compiled yet, automatically falls back to
    Python's own high-resolution timer — same results, slightly less precision.
    """

    def __init__(self) -> None:
        try:
            import devpulse_engine as _eng  # compiled C++ module
            self._eng = _eng
            self.native_available = True
        except ImportError:
            self._eng = None
            self.native_available = False

    def benchmark(self, fn: Callable, iterations: int = 100) -> BenchmarkReport:
        """
        Run `fn` `iterations` times and return timing + memory statistics.

        Args:
            fn:         Any zero-argument Python function, e.g. `lambda: my_code()`.
            iterations: Number of timed runs. More runs = more accurate averages.

        Returns:
            A BenchmarkReport with mean, median, p95, min, max, and memory usage.
        """
        if self.native_available:
            return self._benchmark_cpp(fn, iterations)
        return self._benchmark_python(fn, iterations)

    def detect_loop_depth(self, tokens: List[str]) -> int:
        """
        Given a list of keywords, return how deeply nested the loops go.

        Example: ["for", "while", "end_loop", "end_loop"] → depth 2
        """
        if self.native_available:
            return self._eng.detect_loop_depth(tokens)
        return self._detect_loop_depth_python(tokens)

    def get_memory(self) -> int:
        """Return the current process memory in bytes, or -1 if unavailable."""
        if self.native_available:
            return self._eng.get_memory_usage()
        return -1

    # ── private helpers ──────────────────────────────────────────────────────

    def _benchmark_cpp(self, fn: Callable, iterations: int) -> BenchmarkReport:
        r = self._eng.benchmark_callable(fn, iterations)
        return BenchmarkReport(
            execution_time_ms=r.execution_time_ms,
            median_time_ms=r.median_time_ns / 1.0e6,
            p95_time_ms=r.p95_time_ns / 1.0e6,
            min_time_ms=r.min_time_ns / 1.0e6,
            max_time_ms=r.max_time_ns / 1.0e6,
            memory_bytes=r.memory_bytes,
            iterations=r.iterations,
            source="cpp_engine",
        )

    def _benchmark_python(self, fn: Callable, iterations: int) -> BenchmarkReport:
        samples: List[float] = []

        fn()  # warm-up run, not measured

        for _ in range(iterations):
            t0 = time.perf_counter_ns()
            fn()
            samples.append(time.perf_counter_ns() - t0)

        samples.sort()
        mean_ns   = sum(samples) / len(samples)
        median_ns = samples[len(samples) // 2]
        p95_ns    = samples[int(len(samples) * 0.95)]

        return BenchmarkReport(
            execution_time_ms=mean_ns / 1.0e6,
            median_time_ms=median_ns / 1.0e6,
            p95_time_ms=p95_ns / 1.0e6,
            min_time_ms=samples[0] / 1.0e6,
            max_time_ms=samples[-1] / 1.0e6,
            memory_bytes=0,
            iterations=iterations,
            source="python_fallback",
        )

    @staticmethod
    def _detect_loop_depth_python(tokens: List[str]) -> int:
        max_depth = current = 0
        for token in tokens:
            if token in ("for", "while"):
                current += 1
                max_depth = max(max_depth, current)
            elif token == "end_loop" and current > 0:
                current -= 1
        return max_depth
