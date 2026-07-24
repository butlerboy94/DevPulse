from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_user_optional
from app.core.database import get_db
from app.models.analysis import Analysis
from app.models.user import User
from app.schemas.analysis import AnalysisHistoryItem, AnalysisOut, AnalyzeRequest
from app.services.analysis_service import UnsupportedLanguageError, analyze_submission

router = APIRouter(tags=["analysis"])


@router.post("/analyze", response_model=AnalysisOut, status_code=status.HTTP_201_CREATED)
def analyze(
    payload: AnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """
    Run a code submission through the full analysis pipeline: benchmark,
    static analysis, and (if an Anthropic API key is configured) AI
    recommendations. Works for both logged-in users (saved to their
    history) and anonymous visitors (saved without an owner).
    """
    try:
        result = analyze_submission(
            db,
            language=payload.language,
            source_code=payload.source_code,
            user_id=current_user.id if current_user else None,
            iterations=payload.iterations,
        )
    except UnsupportedLanguageError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return result


@router.get("/results/{analysis_id}", response_model=AnalysisOut)
def get_result(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """
    Fetch a single analysis by id. Anonymous submissions are viewable by
    anyone with the id; submissions made while logged in are only viewable
    by their owner.
    """
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    if analysis.user_id is not None and (current_user is None or current_user.id != analysis.user_id):
        raise HTTPException(status_code=403, detail="You do not have access to this analysis")
    return analysis


@router.get("/history", response_model=list[AnalysisHistoryItem])
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 50,
):
    """List the logged-in user's past analyses, most recent first."""
    return (
        db.query(Analysis)
        .filter(Analysis.user_id == current_user.id)
        .order_by(Analysis.created_at.desc())
        .limit(limit)
        .all()
    )
