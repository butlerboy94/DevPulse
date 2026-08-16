# Tests for the subprocess-based code sandbox (services/sandbox.py):
# successful runs, crashes, timeouts, and syntax errors.
from app.services.sandbox import run_python_sandbox


def test_successful_execution_returns_benchmark():
    result = run_python_sandbox("x = sum(range(1000))\n", iterations=3, timeout_seconds=5)
    assert result.success is True
    assert result.error is None
    assert result.benchmark is not None
    assert result.benchmark["iterations"] == 3
    assert result.profile is not None


def test_stdout_from_submitted_code_is_captured():
    result = run_python_sandbox("print('hello from sandbox')\n", iterations=2, timeout_seconds=5)
    assert result.success is True
    assert "hello from sandbox" in result.stdout


def test_syntax_error_is_reported_without_crashing():
    result = run_python_sandbox("def broken(:\n    pass", iterations=1, timeout_seconds=5)
    assert result.success is False
    assert result.error is not None


def test_runtime_error_is_reported():
    result = run_python_sandbox("1 / 0\n", iterations=1, timeout_seconds=5)
    assert result.success is False
    assert "ZeroDivisionError" in result.error


def test_infinite_loop_times_out():
    result = run_python_sandbox("while True:\n    pass\n", iterations=1, timeout_seconds=2)
    assert result.success is False
    assert "timed out" in result.error
