from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# The backend project root (the folder that contains the "app" package).
# sandbox.py lives at app/services/sandbox.py, so two levels up is the root.
_BACKEND_ROOT = Path(__file__).resolve().parents[2]

_RESULT_START = "###DEVPULSE_RESULT_START###"
_RESULT_END = "###DEVPULSE_RESULT_END###"

# This is the program that actually runs inside the throwaway subprocess.
# It imports the C++/Python benchmarking engine, times the user's code,
# profiles it, and prints the results as one line of JSON between two
# marker strings so the parent process can find them even if the user's
# code itself prints things to the screen.
_RUNNER_SOURCE = """
import contextlib
import io
import json
import sys

sys.path.insert(0, {backend_root!r})

try:
    import resource  # POSIX only — not available on Windows

    resource.setrlimit(resource.RLIMIT_CPU, ({cpu_seconds}, {cpu_seconds}))
    resource.setrlimit(resource.RLIMIT_AS, ({memory_bytes}, {memory_bytes}))
except ImportError:
    pass

from app.engine.wrapper import BenchmarkEngine
from app.engine.profiler import CodeProfiler

with open({user_code_path!r}, "r", encoding="utf-8") as _f:
    _source = _f.read()

_compiled = compile(_source, "<submitted_code>", "exec")


def _run_user_code():
    exec(_compiled, {{"__name__": "__main__"}})


_stdout = io.StringIO()
result: dict = {{}}
try:
    with contextlib.redirect_stdout(_stdout):
        engine = BenchmarkEngine()
        bench = engine.benchmark(_run_user_code, iterations={iterations})
        profiler = CodeProfiler(top_n=10)
        profile = profiler.profile(_run_user_code)

    result = {{
        "success": True,
        "error": None,
        "stdout": _stdout.getvalue()[-4000:],
        "benchmark": {{
            "execution_time_ms": bench.execution_time_ms,
            "median_time_ms": bench.median_time_ms,
            "p95_time_ms": bench.p95_time_ms,
            "min_time_ms": bench.min_time_ms,
            "max_time_ms": bench.max_time_ms,
            "memory_bytes": bench.memory_bytes,
            "iterations": bench.iterations,
            "source": bench.source,
        }},
        "profile": {{
            "total_time_ms": profile.total_time_ms,
            "function_count": profile.function_count,
            "total_call_count": profile.total_call_count,
            "hotspots": [
                {{
                    "function_name": h.function_name,
                    "filename": h.filename,
                    "line_number": h.line_number,
                    "call_count": h.call_count,
                    "total_time_ms": h.total_time_ms,
                    "cumulative_time_ms": h.cumulative_time_ms,
                }}
                for h in profile.hotspots
            ],
        }},
    }}
except Exception as exc:
    result = {{
        "success": False,
        "error": f"{{type(exc).__name__}}: {{exc}}",
        "stdout": _stdout.getvalue()[-4000:],
        "benchmark": None,
        "profile": None,
    }}

print({result_start!r})
print(json.dumps(result))
print({result_end!r})
"""


@dataclass
class SandboxResult:
    """What came back from running a piece of code in the sandbox."""

    success: bool
    stdout: str
    error: str | None
    benchmark: dict[str, Any] | None
    profile: dict[str, Any] | None


def run_python_sandbox(
    source_code: str,
    iterations: int = 5,
    timeout_seconds: int = 10,
    memory_limit_mb: int = 256,
) -> SandboxResult:
    """
    Run `source_code` in a brand-new, throwaway Python process and report
    how long it took, how much memory it used, and which functions were slow.

    This is a *soft* sandbox appropriate for a portfolio/learning project,
    not a hard security boundary: it isolates the submitted code in its own
    process (so a crash or infinite loop can't take down the API server),
    enforces a wall-clock timeout, and caps CPU time + memory on POSIX
    systems. It does not prevent filesystem or network access — a real
    production deployment would add OS-level sandboxing (containers,
    gVisor, seccomp) on top of this.
    """
    with tempfile.TemporaryDirectory(prefix="devpulse_sandbox_") as tmp_dir:
        tmp_path = Path(tmp_dir)
        user_code_path = tmp_path / "submitted_code.py"
        runner_path = tmp_path / "runner.py"

        user_code_path.write_text(source_code, encoding="utf-8")
        runner_path.write_text(
            _RUNNER_SOURCE.format(
                backend_root=str(_BACKEND_ROOT),
                user_code_path=str(user_code_path),
                iterations=iterations,
                cpu_seconds=timeout_seconds,
                memory_bytes=memory_limit_mb * 1024 * 1024,
                result_start=_RESULT_START,
                result_end=_RESULT_END,
            ),
            encoding="utf-8",
        )

        try:
            completed = subprocess.run(
                [sys.executable, str(runner_path)],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                cwd=tmp_dir,
            )
        except subprocess.TimeoutExpired:
            return SandboxResult(
                success=False,
                stdout="",
                error=f"Execution timed out after {timeout_seconds} seconds",
                benchmark=None,
                profile=None,
            )

        parsed = _extract_result(completed.stdout)
        if parsed is not None:
            return SandboxResult(**parsed)

        # The runner crashed before it could print a result (e.g. a syntax
        # error in the submitted code, or the process was killed).
        error_detail = completed.stderr.strip() or completed.stdout.strip() or "Unknown sandbox failure"
        return SandboxResult(
            success=False,
            stdout="",
            error=error_detail[-2000:],
            benchmark=None,
            profile=None,
        )


def _extract_result(stdout: str) -> dict[str, Any] | None:
    if _RESULT_START not in stdout or _RESULT_END not in stdout:
        return None
    payload = stdout.split(_RESULT_START, 1)[1].split(_RESULT_END, 1)[0].strip()
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        return None
