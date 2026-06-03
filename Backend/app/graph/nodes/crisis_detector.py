import json
import logging

from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import get_settings
from app.graph.prompts import CRISIS_ASSESSMENT_PROMPT
from app.graph.state import AgentState
from app.services.crisis_service import classify_risk, compute_keyword_score, scan_keywords

logger = logging.getLogger(__name__)


def _get_last_user_message(state: AgentState) -> str:
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage) or (hasattr(msg, "type") and msg.type == "human"):
            return msg.content if isinstance(msg.content, str) else str(msg.content)
    return ""


async def crisis_detection_node(state: AgentState) -> dict:
    user_text = _get_last_user_message(state)
    if not user_text:
        return {"risk_level": "none"}

    keyword_matches = scan_keywords(user_text)
    keyword_score = compute_keyword_score(keyword_matches)

    llm_score = 0.0
    metadata = state.get("session_metadata", {})
    turn_count = metadata.get("turn_count", 0)
    should_llm_check = keyword_score > 0 or turn_count % 3 == 0

    if should_llm_check:
        try:
            settings = get_settings()
            llm = ChatGoogleGenerativeAI(
                model=settings.gemini_model_name,
                google_api_key=settings.google_api_key,
                temperature=0.0,
            )

            recent_messages = state["messages"][-6:]
            context_str = "\n".join(
                f"{'User' if (isinstance(m, HumanMessage) or (hasattr(m, 'type') and m.type == 'human')) else 'Assistant'}: "
                f"{m.content if isinstance(m.content, str) else str(m.content)}"
                for m in recent_messages
            )

            assessment_prompt = f"{CRISIS_ASSESSMENT_PROMPT}\n\nConversation:\n{context_str}"
            response = await llm.ainvoke([HumanMessage(content=assessment_prompt)])
            response_text = response.content if isinstance(response.content, str) else str(response.content)

            clean_text = response_text.strip()
            if clean_text.startswith("```"):
                clean_text = clean_text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

            parsed = json.loads(clean_text)
            llm_score = float(parsed.get("score", 0.0))
            llm_score = max(0.0, min(1.0, llm_score))

        except Exception as e:
            logger.warning("Crisis LLM assessment failed: %s", e)
            if keyword_score > 0.7:
                llm_score = keyword_score

    context_factor = 0.0
    if metadata.get("previous_risk_level") in ("high", "critical"):
        context_factor = 0.3

    risk_level = classify_risk(keyword_score, llm_score, context_factor)

    metadata = {**metadata, "previous_risk_level": risk_level}

    return {
        "risk_level": risk_level,
        "session_metadata": metadata,
    }
