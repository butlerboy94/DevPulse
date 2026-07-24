from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import anthropic

from app.core.config import settings

# claude-opus-5 is Anthropic's current flagship model — strongest at reading
# code, spotting inefficiencies, and explaining *why* something is slow in
# plain English, which is exactly what this feature needs.
_MODEL = "claude-opus-5"

_RECOMMENDATION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "summary": {
            "type": "string",
            "description": "One or two sentence plain-English summary of the code's overall performance and quality.",
        },
        "overall_score": {
            "type": "integer",
            "description": "Overall score from 0 (needs major work) to 100 (excellent).",
        },
        "recommendations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Short title for the issue."},
                    "severity": {"type": "string", "enum": ["low", "medium", "high"]},
                    "explanation": {
                        "type": "string",
                        "description": "Plain-English explanation of the issue and why it matters, written for someone with no programming background.",
                    },
                    "suggested_fix": {
                        "type": "string",
                        "description": "A concrete suggested code change or approach to fix the issue.",
                    },
                },
                "required": ["title", "severity", "explanation", "suggested_fix"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["summary", "overall_score", "recommendations"],
    "additionalProperties": False,
}


@dataclass
class Recommendation:
    title: str
    severity: str
    explanation: str
    suggested_fix: str


@dataclass
class AIReport:
    summary: str
    overall_score: int
    recommendations: list[Recommendation]


class AIRecommendationError(Exception):
    """Raised when the AI step fails — callers should treat this as optional
    and continue without recommendations rather than failing the whole
    analysis."""


def generate_recommendations(
    source_code: str,
    language: str,
    benchmark: dict[str, Any] | None,
    static_analysis: dict[str, Any] | None,
) -> AIReport | None:
    """
    Ask Claude to review the code's benchmark and static-analysis results
    and return plain-English optimization advice as structured JSON.

    Returns None (rather than raising) when no API key is configured, so
    the rest of the analysis pipeline keeps working without AI
    recommendations — useful for local development and tests that don't
    have a real Anthropic API key.
    """
    if not settings.anthropic_api_key:
        return None

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    prompt = _build_prompt(source_code, language, benchmark, static_analysis)

    try:
        response = client.messages.create(
            model=_MODEL,
            max_tokens=2048,
            output_config={
                "effort": "medium",
                "format": {"type": "json_schema", "schema": _RECOMMENDATION_SCHEMA},
            },
            messages=[{"role": "user", "content": prompt}],
        )
    except anthropic.APIError as exc:
        raise AIRecommendationError(str(exc)) from exc

    if response.stop_reason == "refusal":
        raise AIRecommendationError("The AI declined to analyze this submission.")

    text = next((block.text for block in response.content if block.type == "text"), None)
    if text is None:
        raise AIRecommendationError("The AI response did not contain the expected JSON.")

    data = json.loads(text)
    return AIReport(
        summary=data["summary"],
        overall_score=data["overall_score"],
        recommendations=[Recommendation(**item) for item in data["recommendations"]],
    )


def _build_prompt(
    source_code: str,
    language: str,
    benchmark: dict[str, Any] | None,
    static_analysis: dict[str, Any] | None,
) -> str:
    sections = [
        f"You are reviewing a {language} code submission for DevPulse, a code performance "
        "analysis tool. Give plain-English, actionable optimization recommendations that a "
        "developer can act on immediately. Be specific and reference the actual code.",
        "",
        "SOURCE CODE:",
        f"```{language}",
        source_code,
        "```",
    ]
    if benchmark:
        sections += ["", "BENCHMARK RESULTS:", json.dumps(benchmark, indent=2)]
    if static_analysis:
        sections += ["", "STATIC ANALYSIS RESULTS:", json.dumps(static_analysis, indent=2)]
    return "\n".join(sections)
