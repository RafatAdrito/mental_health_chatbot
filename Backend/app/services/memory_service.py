import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


async def get_user_context(db: AsyncSession, user_id: str) -> str:
    uid = uuid.UUID(user_id)
    result = await db.execute(select(User).where(User.id == uid))
    user = result.scalar_one_or_none()
    if user is None or not user.preferences:
        return ""

    prefs = user.preferences
    parts: list[str] = []

    if prefs.get("preferred_name"):
        parts.append(f"The user prefers to be called {prefs['preferred_name']}.")
    if prefs.get("preferred_coping"):
        parts.append(f"Coping strategies they've found helpful before: {', '.join(prefs['preferred_coping'])}.")
    if prefs.get("topics_discussed"):
        parts.append(f"Topics discussed in past sessions: {', '.join(prefs['topics_discussed'][-5:])}.")
    if prefs.get("communication_style"):
        parts.append(f"Communication preference: {prefs['communication_style']}.")

    return " ".join(parts)


async def update_user_preferences(db: AsyncSession, user_id: str, key: str, value: object) -> None:
    uid = uuid.UUID(user_id)
    result = await db.execute(select(User).where(User.id == uid))
    user = result.scalar_one_or_none()
    if user is None:
        return

    prefs = dict(user.preferences) if user.preferences else {}
    prefs[key] = value
    user.preferences = prefs
    await db.flush()
