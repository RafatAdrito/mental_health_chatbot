from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import get_settings
from app.graph.prompts import MOOD_CHECKIN_PROMPT
from app.graph.state import AgentState


async def mood_checkin_node(state: AgentState) -> dict:
    metadata = state.get("session_metadata", {})
    turn_count = metadata.get("turn_count", 0)

    if turn_count <= 1:
        settings = get_settings()
        llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model_name,
            google_api_key=settings.google_api_key,
            streaming=True,
            temperature=0.8,
        )

        user_context = state.get("user_context", "")
        checkin_system = MOOD_CHECKIN_PROMPT
        if user_context:
            checkin_system += f"\n\nContext about this user: {user_context}"

        messages = [
            SystemMessage(content=checkin_system),
            HumanMessage(content=state["messages"][-1].content if state["messages"] else "Hello"),
        ]

        full_content = ""
        async for chunk in llm.astream(messages):
            if hasattr(chunk, "content") and isinstance(chunk.content, str):
                full_content += chunk.content

        metadata = {**metadata, "last_mood_checkin_turn": turn_count}
        return {
            "messages": [AIMessage(content=full_content)],
            "needs_mood_checkin": False,
            "session_metadata": metadata,
        }

    settings = get_settings()
    llm = ChatGoogleGenerativeAI(
        model=settings.gemini_model_name,
        google_api_key=settings.google_api_key,
        streaming=True,
        temperature=0.8,
    )

    messages = [
        SystemMessage(content=MOOD_CHECKIN_PROMPT),
    ] + list(state["messages"][-4:])

    full_content = ""
    async for chunk in llm.astream(messages):
        if hasattr(chunk, "content") and isinstance(chunk.content, str):
            full_content += chunk.content

    metadata = {**metadata, "last_mood_checkin_turn": turn_count}
    return {
        "messages": [AIMessage(content=full_content)],
        "needs_mood_checkin": False,
        "session_metadata": metadata,
    }
