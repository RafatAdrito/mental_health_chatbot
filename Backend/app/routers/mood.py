import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models import MoodEntry, User
from app.schemas import MoodCreateRequest, MoodEntryResponse, MoodHistoryResponse

router = APIRouter(prefix="/api/v1/mood", tags=["mood"])


@router.get("", response_model=MoodHistoryResponse)
async def get_mood_history(
    days: int = Query(default=30, ge=1, le=365),
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    result = await db.execute(
        select(MoodEntry)
        .where(MoodEntry.user_id == current_user.id, MoodEntry.created_at >= cutoff)
        .order_by(MoodEntry.created_at.desc())
        .limit(limit)
    )
    entries = result.scalars().all()

    return MoodHistoryResponse(
        user_id=str(current_user.id),
        entries=[
            MoodEntryResponse(
                id=str(e.id),
                user_id=str(e.user_id),
                session_id=str(e.session_id) if e.session_id else None,
                mood_score=e.mood_score,
                mood_label=e.mood_label,
                notes=e.notes,
                coping_strategies_offered=e.coping_strategies_offered,
                created_at=e.created_at,
            )
            for e in entries
        ],
    )


@router.post("", response_model=MoodEntryResponse, status_code=201)
async def create_mood_entry(
    req: MoodCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    entry = MoodEntry(
        user_id=current_user.id,
        session_id=uuid.UUID(req.session_id) if req.session_id else None,
        mood_score=req.mood_score,
        mood_label=req.mood_label,
        notes=req.notes,
    )
    db.add(entry)
    await db.flush()

    return MoodEntryResponse(
        id=str(entry.id),
        user_id=str(entry.user_id),
        session_id=str(entry.session_id) if entry.session_id else None,
        mood_score=entry.mood_score,
        mood_label=entry.mood_label,
        notes=entry.notes,
        coping_strategies_offered=entry.coping_strategies_offered,
        created_at=entry.created_at,
    )
