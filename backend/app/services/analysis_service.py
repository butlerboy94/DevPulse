from __future__ import annotations

import hashlib
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.analysis import Analysis
from app.services.ai_recommendations import AIRecommendationError, generate_recommendations
from app.services.sandbox import run_python_sandbox
from app.services.static_analysis import StaticAnalysisReport, StaticAnalyzer

# Static analysis relies on Python's `ast` module, so it (and the benchmark
# sandbox, which reuses the C++/Python engine from Phase 2) only understand
# Python submissions for now. Other languages are a Phase 4+ frontend
# concern until a matching backend analyzer exists for them.
_SUPPORTED_LANGUAGES = {"python"}


class UnsupportedLanguageError(Exception):
    pass


def analyze_submission(
    db: Session,
    language: str,
    source_code: str,
    user_id: int | None,
    iterations: int = 5,
) -> Analysis:
    """
    Run the full DevPulse analysis pipeline on a code submission: benchmark
    it in the sandbox, run static analysis, ask Claude for optimization
    recommendations, and store everything in the database.

    Every step after the initial row insert is wrapped so that a failure in
    one step (e.g. the AI call) doesn't lose the results already gathered by
    the others — the analysis is always saved with whatever it managed to
    complete, plus a status/error message describing what happened.
    """
    if language not in _SUPPORTED_LANGUAGES:
        raise UnsupportedLanguageError(
            f"Benchmarking and static analysis currently only support Python. Got: {language!r}"
        )

    code_hash = hashlib.sha256(f"{language}:{source_code}".encode("utf-8")).hexdigest()

    analysis = Analysis(
        user_id=user_id,
        language=language,
        source_code=source_code,
        code_hash=code_hash,
        status="running",
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    try:
        sandbox_result = run_python_sandbox(source_code, iterations=iterations)
        static_report = StaticAnalyzer().analyze(source_code)
        static_report_dict = _static_report_to_dict(static_report)

        analysis.lines_of_code = static_report.lines_of_code
        analysis.function_count = static_report.function_count
        analysis.cyclomatic_complexity = static_report.average_cyclomatic_complexity
        analysis.quality_score = static_report.quality_score

        raw_results: dict[str, Any] = {
            "static_analysis": static_report_dict,
            "sandbox": {
                "success": sandbox_result.success,
                "error": sandbox_result.error,
                "stdout": sandbox_result.stdout,
            },
        }

        if sandbox_result.success and sandbox_result.benchmark:
            analysis.execution_time_ms = sandbox_result.benchmark["execution_time_ms"]
            analysis.execution_time_ns = sandbox_result.benchmark["execution_time_ms"] * 1_000_000
            analysis.memory_bytes = sandbox_result.benchmark["memory_bytes"]
            raw_results["benchmark"] = sandbox_result.benchmark
            raw_results["profile"] = sandbox_result.profile
        else:
            analysis.error_message = sandbox_result.error

        try:
            ai_report = generate_recommendations(
                source_code=source_code,
                language=language,
                benchmark=sandbox_result.benchmark,
                static_analysis=static_report_dict,
            )
        except AIRecommendationError as exc:
            ai_report = None
            raw_results["ai_error"] = str(exc)

        if ai_report is not None:
            analysis.ai_recommendations = {
                "summary": ai_report.summary,
                "overall_score": ai_report.overall_score,
                "recommendations": [asdict(item) for item in ai_report.recommendations],
            }

        analysis.raw_results = raw_results
        analysis.status = "complete" if sandbox_result.success else "error"
        analysis.completed_at = datetime.now(timezone.utc)

    except Exception as exc:
        # Safety net: something unexpected (not the sandboxed user code,
        # which already fails safely inside its own subprocess) went wrong
        # in our own pipeline code. Record it instead of losing the
        # already-created row or crashing the request.
        analysis.status = "error"
        analysis.error_message = f"{type(exc).__name__}: {exc}"
        analysis.completed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(analysis)
    return analysis


def _static_report_to_dict(report: StaticAnalysisReport) -> dict[str, Any]:
    return {
        "lines_of_code": report.lines_of_code,
        "function_count": report.function_count,
        "average_cyclomatic_complexity": report.average_cyclomatic_complexity,
        "max_cyclomatic_complexity": report.max_cyclomatic_complexity,
        "quality_score": report.quality_score,
        "syntax_error": report.syntax_error,
        "functions": [asdict(item) for item in report.functions],
        "naming_violations": [asdict(item) for item in report.naming_violations],
        "unused_variables": [asdict(item) for item in report.unused_variables],
    }
