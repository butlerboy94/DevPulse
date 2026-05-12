from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text

from app.core.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    # Submitted code
    language = Column(String(20), nullable=False)          # python | cpp | javascript
    source_code = Column(Text, nullable=False)
    code_hash = Column(String(64), index=True)             # SHA-256 for cache lookup

    # Benchmark results (from C++ engine)
    execution_time_ns = Column(Float, nullable=True)
    execution_time_ms = Column(Float, nullable=True)
    memory_bytes = Column(Integer, nullable=True)
    loop_depth = Column(Integer, nullable=True)

    # Static analysis results (from Python ast)
    cyclomatic_complexity = Column(Float, nullable=True)
    lines_of_code = Column(Integer, nullable=True)
    function_count = Column(Integer, nullable=True)
    quality_score = Column(Float, nullable=True)           # 0–100

    # AI recommendations (from Anthropic API)
    ai_recommendations = Column(JSON, nullable=True)       # structured JSON report

    # Full raw results blob for flexibility
    raw_results = Column(JSON, nullable=True)

    status = Column(String(20), default="pending")         # pending | running | complete | error
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
