# Regression test for a real bug found in Session 8: the AI-recommendations
# step is only wrapped for its own dedicated AIRecommendationError, so any
# *other* kind of exception from that step (a bad SDK call, a malformed API
# response, a bug) used to escape all the way out and get caught by the
# outer safety-net handler — which throws away the benchmark and static-
# analysis results that had already succeeded. The AI step is supposed to
# be optional; this confirms it actually behaves that way for any failure,
# not just the one exception type it happens to raise on purpose.
from unittest.mock import patch

from app.services.analysis_service import analyze_submission

SIMPLE_CODE = "def add(a, b):\n    return a + b\n\nprint(add(2, 3))\n"


def test_unexpected_ai_step_failure_does_not_lose_other_results(db_session):
    # Simulate exactly what happened for real: generate_recommendations
    # raising a plain TypeError (an unsupported SDK keyword argument),
    # not the AIRecommendationError the surrounding code was built to
    # expect.
    with patch(
        "app.services.analysis_service.generate_recommendations",
        side_effect=TypeError("Messages.create() got an unexpected keyword argument 'output_config'"),
    ):
        analysis = analyze_submission(
            db_session,
            language="python",
            source_code=SIMPLE_CODE,
            user_id=None,
            iterations=2,
        )

    # The sandbox run and static analysis still succeeded and must survive.
    assert analysis.status == "complete"
    assert analysis.execution_time_ms is not None
    assert analysis.quality_score == 100.0
    assert analysis.raw_results["benchmark"] is not None
    assert analysis.raw_results["static_analysis"] is not None

    # The AI failure is recorded, not silently dropped.
    assert "TypeError" in analysis.raw_results["ai_error"]
    assert analysis.ai_recommendations is None
