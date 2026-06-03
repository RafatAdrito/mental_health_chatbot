from langchain_core.messages import AIMessage

from app.graph.state import AgentState
from app.services.crisis_service import CRISIS_HOTLINES


def crisis_response_node(state: AgentState) -> dict:
    risk_level = state.get("risk_level", "high")

    hotline_text = "\n".join(
        f"- **{h['name']}**: {h['contact']} — {h['description']}"
        for h in CRISIS_HOTLINES[:3]
    )

    if risk_level == "critical":
        response = (
            "I hear you, and I want you to know that what you're feeling matters deeply. "
            "You don't have to go through this alone.\n\n"
            "**Please reach out to one of these resources right now — they are free, confidential, and available 24/7:**\n\n"
            f"{hotline_text}\n\n"
            "If you're in immediate danger, please call 911 or go to your nearest emergency room.\n\n"
            "I'm here with you. Would you like to talk more while you consider reaching out?"
        )
    else:
        response = (
            "I can sense you're going through something really difficult right now, and I'm glad you're sharing this with me. "
            "Your feelings are valid.\n\n"
            "I want to make sure you have access to support beyond our conversation:\n\n"
            f"{hotline_text}\n\n"
            "These are free, confidential services with trained counselors who can help.\n\n"
            "Would you like to talk more about what you're experiencing? I'm here to listen."
        )

    return {
        "messages": [AIMessage(content=response)],
    }
