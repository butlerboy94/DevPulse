from __future__ import annotations

import cProfile
import io
import pstats
from dataclasses import dataclass, field
from typing import Callable, List


@dataclass
class ProfileEntry:
    """Timing data for a single function seen during profiling."""
    function_name: str
    filename: str
    line_number: int
    call_count: int
    total_time_ms: float       # time spent inside this function only
    cumulative_time_ms: float  # time spent here + everything it called


@dataclass
class ProfileReport:
    """Full profiling results for one execution of a function."""
    total_time_ms: float
    function_count: int        # number of distinct functions called
    total_call_count: int      # total number of function calls made
    hotspots: List[ProfileEntry] = field(default_factory=list)  # top N slowest

    @property
    def top_hotspot(self) -> ProfileEntry | None:
        """The single slowest function, or None if nothing was profiled."""
        return self.hotspots[0] if self.hotspots else None


class CodeProfiler:
    """
    Runs a Python function and records exactly which internal functions
    were called, how many times, and how long each one took.

    Uses Python's built-in `cProfile` module — the same tool professional
    Python developers use to diagnose slow code.
    """

    def __init__(self, top_n: int = 20) -> None:
        """
        Args:
            top_n: How many of the slowest functions to include in the report.
                   Default is 20. You rarely need more than the top 5-10.
        """
        self.top_n = top_n

    def profile(self, fn: Callable) -> ProfileReport:
        """
        Run `fn` once under the profiler and return a ProfileReport.

        Args:
            fn: Any zero-argument Python function.

        Returns:
            A ProfileReport with hotspot data sorted by cumulative time.
        """
        pr = cProfile.Profile()
        pr.enable()
        fn()
        pr.disable()

        return self._parse(pr)

    # ── private helpers ──────────────────────────────────────────────────────

    def _parse(self, pr: cProfile.Profile) -> ProfileReport:
        stream = io.StringIO()
        stats = pstats.Stats(pr, stream=stream)
        stats.sort_stats("cumulative")

        # pstats.Stats stores raw data in .stats:
        # key   = (filename, line_number, function_name)
        # value = (call_count, non_recursive_calls, total_time_sec, cumulative_time_sec, ...)
        entries: List[ProfileEntry] = []
        total_calls = 0

        for (filename, lineno, funcname), (cc, nc, tt, ct, _) in stats.stats.items():
            total_calls += cc
            entries.append(ProfileEntry(
                function_name=funcname,
                filename=filename,
                line_number=lineno,
                call_count=cc,
                total_time_ms=tt * 1_000,
                cumulative_time_ms=ct * 1_000,
            ))

        entries.sort(key=lambda e: e.cumulative_time_ms, reverse=True)
        total_ms = sum(e.total_time_ms for e in entries)

        return ProfileReport(
            total_time_ms=total_ms,
            function_count=len(entries),
            total_call_count=total_calls,
            hotspots=entries[: self.top_n],
        )
