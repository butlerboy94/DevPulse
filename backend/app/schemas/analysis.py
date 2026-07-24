from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    language: str = Field(default="python", description="Programming language of the submitted code")
    source_code: str = Field(min_length=1, max_length=20_000)
    iterations: int = Field(default=5, ge=1, le=50, description="How many timed runs to average")


class AnalysisOut(BaseModel):
    id: int
    language: str
    status: str
    execution_time_ms: float | None = None
    memory_bytes: int | None = None
    cyclomatic_complexity: float | None = None
    lines_of_code: int | None = None
    function_count: int | None = None
    quality_score: float | None = None
    ai_recommendations: dict[str, Any] | None = None
    raw_results: dict[str, Any] | None = None
    error_message: str | None = None
    created_at: datetime
    completed_at: datetime | None = None

    class Config:
        from_attributes = True


class AnalysisHistoryItem(BaseModel):
    id: int
    language: str
    status: str
    quality_score: float | None = None
    execution_time_ms: float | None = None
    created_at: datetime

    class Config:
        from_attributes = True
