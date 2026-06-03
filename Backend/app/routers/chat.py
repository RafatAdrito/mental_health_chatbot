import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from langchain_core.messages import AIMessage, HumanMessage
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory, get_db
from app.dependencies.auth import get_current_user
from app.models import ConversationMessage, ConversationSession, User

from app.schemas import (
    ChatHistoryMessage,
    ChatHistoryResponse,
    ChatRequest,
    ChatResponse,
    DeleteSessionResponse,
    SessionCreateResponse,
    SessionListResponse,
    SessionSummary,
    WSEvent,
    WSMessage,
)
from app.services.memory_service import get_user_context

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _parse_session_id(session_id: str) -> uuid.UUID:
    try:
        return uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID format",
        )


def _get_compiled_graph():
    from app.main import compiled_graph
    return compiled_graph


# ── Session management ──────────────────────────────────────────────────────

@router.post("/session", response_model=SessionCreateResponse)
async def create_session(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = ConversationSession(user_id=current_user.id)
    db.add(session)
    await db.flush()
    return SessionCreateResponse(session_id=str(session.id), user_id=str(current_user.id))


@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ConversationSession)
        .where(ConversationSession.user_id == current_user.id)
        .order_by(ConversationSession.updated_at.desc())
    )
    sessions = result.scalars().all()
    return SessionListResponse(
        sessions=[
            SessionSummary(
                session_id=str(s.id),
                title=s.title,
                created_at=s.created_at,
                updated_at=s.updated_at,
            )
            for s in sessions
        ]
    )


# ── Chat ─────────────────────────────────────────────────────────────────────

@router.post("", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    graph = _get_compiled_graph()

    session_uid = _parse_session_id(req.session_id)
    result = await db.execute(
        select(ConversationSession).where(ConversationSession.id == session_uid)
    )
    session = result.scalar_one_or_none()

    if session is None:
        session = ConversationSession(id=session_uid, user_id=current_user.id)
        db.add(session)
        await db.flush()
    elif session.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Session not found")

    db.add(
        ConversationMessage(
            session_id=session.id,
            user_id=current_user.id,
            role="user",
            content=req.message,
        )
    )
    session.updated_at = _utcnow()
    await db.commit()

    user_ctx = await get_user_context(db, str(current_user.id))
    config = {"configurable": {"thread_id": req.session_id}}

    input_state = {
        "messages": [HumanMessage(content=req.message)],
        "user_id": str(current_user.id),
        "session_id": req.session_id,
        "risk_level": "none",
        "mood_score": None,
        "needs_mood_checkin": False,
        "session_metadata": {},
        "user_context": user_ctx,
        "latitude": req.latitude,
        "longitude": req.longitude,
    }

    final_state = await graph.ainvoke(input_state, config=config)

    ai_response = ""
    for msg in reversed(final_state["messages"]):
        if isinstance(msg, AIMessage) and isinstance(msg.content, str) and msg.content:
            ai_response = msg.content
            break

    # Update session title from first user message if not yet set
    if not session.title:
        session.title = req.message[:80]
    session.updated_at = _utcnow()

    if ai_response:
        db.add(
            ConversationMessage(
                session_id=session.id,
                user_id=current_user.id,
                role="assistant",
                content=ai_response,
            )
        )

    return ChatResponse(
        response=ai_response,
        risk_level=final_state.get("risk_level", "none"),
        mood_score=final_state.get("mood_score"),
        session_id=req.session_id,
    )


@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
async def get_history(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify ownership
    session_uid = _parse_session_id(session_id)
    result = await db.execute(
        select(ConversationSession).where(
            ConversationSession.id == session_uid,
            ConversationSession.user_id == current_user.id,
        )
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    msg_result = await db.execute(
        select(ConversationMessage)
        .where(
            ConversationMessage.session_id == session_uid,
            ConversationMessage.user_id == current_user.id,
        )
        .order_by(ConversationMessage.created_at.asc(), ConversationMessage.id.asc())
    )
    messages = [
        ChatHistoryMessage(
            id=str(msg.id),
            role=msg.role,
            content=msg.content,
            created_at=msg.created_at,
        )
        for msg in msg_result.scalars().all()
    ]
    return ChatHistoryResponse(session_id=session_id, messages=messages)


@router.delete("/session/{session_id}", response_model=DeleteSessionResponse)
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session_uid = _parse_session_id(session_id)

    result = await db.execute(
        select(ConversationSession).where(
            ConversationSession.id == session_uid,
            ConversationSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # Delete the session row (cascades to MoodEntry via ORM relationship)
    await db.delete(session)

    # Clean up LangGraph checkpointer tables for this thread
    tid = session_id
    await db.execute(text("DELETE FROM checkpoint_blobs WHERE thread_id = :tid"), {"tid": tid})
    await db.execute(text("DELETE FROM checkpoint_writes WHERE thread_id = :tid"), {"tid": tid})
    await db.execute(text("DELETE FROM checkpoints WHERE thread_id = :tid"), {"tid": tid})

    return DeleteSessionResponse(session_id=session_id, message="Session deleted successfully")


# ── WebSocket ────────────────────────────────────────────────────────────────

@router.websocket("/wss/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str, token: str | None = None):
    """
    WebSocket endpoint. Pass the JWT as a query param:
      ws://host/api/v1/chat/ws/<session_id>?token=<jwt>
    """
    await websocket.accept()

    # Authenticate via query-param token
    if not token:
        await websocket.send_text(WSEvent(type="error", data="Unauthorized").model_dump_json())
        await websocket.close(code=1008)
        return

    from app.services.auth_service import decode_access_token
    from jose import JWTError

    try:
        user_id_str = decode_access_token(token)
    except JWTError:
        await websocket.send_text(WSEvent(type="error", data="Invalid token").model_dump_json())
        await websocket.close(code=1008)
        return

    try:
        session_uid = uuid.UUID(session_id)
        user_uid = uuid.UUID(user_id_str)
    except ValueError:
        await websocket.send_text(WSEvent(type="error", data="Invalid session").model_dump_json())
        await websocket.close(code=1008)
        return

    graph = _get_compiled_graph()

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = WSMessage.model_validate_json(raw)
            except Exception:
                await websocket.send_text(
                    WSEvent(type="error", data="Invalid message format").model_dump_json()
                )
                continue

            await websocket.send_text(WSEvent(type="status", data="processing").model_dump_json())

            async with async_session_factory() as db:
                try:
                    result = await db.execute(
                        select(ConversationSession).where(
                            ConversationSession.id == session_uid
                        )
                    )
                    session = result.scalar_one_or_none()
                    if session is None:
                        session = ConversationSession(id=session_uid, user_id=user_uid)
                        db.add(session)
                        await db.flush()
                    elif session.user_id != user_uid:
                        await websocket.send_text(WSEvent(type="error", data="Session not found").model_dump_json())
                        await websocket.close(code=1008)
                        return

                    user_ctx = await get_user_context(db, user_id_str)
                    if not session.title:
                        session.title = data.message[:80]
                    session.updated_at = _utcnow()
                    db.add(
                        ConversationMessage(
                            session_id=session.id,
                            user_id=user_uid,
                            role="user",
                            content=data.message,
                        )
                    )
                    await db.commit()
                except Exception as e:
                    await db.rollback()
                    logger.error("WebSocket session/message save error: %s", e)
                    await websocket.send_text(
                        WSEvent(type="error", data="Unable to save your message.").model_dump_json()
                    )
                    continue

            config = {"configurable": {"thread_id": session_id}}
            input_state = {
                "messages": [HumanMessage(content=data.message)],
                "user_id": user_id_str,
                "session_id": session_id,
                "risk_level": "none",
                "mood_score": None,
                "needs_mood_checkin": False,
                "session_metadata": {},
                "user_context": user_ctx,
                "latitude": data.latitude,
                "longitude": data.longitude,
            }

            try:
                async for event in graph.astream_events(input_state, config=config, version="v2"):
                    kind = event.get("event", "")
                    if kind == "on_chat_model_stream":
                        chunk = event.get("data", {}).get("chunk")
                        if chunk and hasattr(chunk, "content") and isinstance(chunk.content, str):
                            await websocket.send_text(
                                WSEvent(type="token", data=chunk.content).model_dump_json()
                            )

                final_state = await graph.aget_state(config)
                risk_level = "none"
                ai_response = ""
                if final_state and final_state.values:
                    risk_level = final_state.values.get("risk_level", "none")
                    for msg in reversed(final_state.values.get("messages", [])):
                        if isinstance(msg, AIMessage) and isinstance(msg.content, str) and msg.content:
                            ai_response = msg.content
                            break

                if ai_response:
                    async with async_session_factory() as db:
                        try:
                            result = await db.execute(
                                select(ConversationSession).where(
                                    ConversationSession.id == session_uid,
                                    ConversationSession.user_id == user_uid,
                                )
                            )
                            session = result.scalar_one_or_none()
                            if session is None:
                                await websocket.send_text(
                                    WSEvent(type="error", data="Session not found").model_dump_json()
                                )
                                await websocket.close(code=1008)
                                return

                            session.updated_at = _utcnow()
                            db.add(
                                ConversationMessage(
                                    session_id=session.id,
                                    user_id=user_uid,
                                    role="assistant",
                                    content=ai_response,
                                )
                            )
                            await db.commit()
                        except Exception as e:
                            await db.rollback()
                            logger.error("WebSocket assistant message save error: %s", e)

                if risk_level in ("high", "critical"):
                    await websocket.send_text(
                        WSEvent(type="crisis_alert", data=risk_level).model_dump_json()
                    )

                await websocket.send_text(WSEvent(type="done", data="").model_dump_json())
            except Exception as e:
                logger.error("WebSocket graph error: %s", e)
                await websocket.send_text(
                    WSEvent(type="error", data="An error occurred processing your message.").model_dump_json()
                )

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected: session %s", session_id)

