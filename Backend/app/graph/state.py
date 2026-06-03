from typing import Annotated, Any

from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    user_id: str
    session_id: str
    risk_level: str
    mood_score: float | None
    needs_mood_checkin: bool
    session_metadata: dict[str, Any]
    user_context: str
    latitude: float | None
    longitude: float | None
