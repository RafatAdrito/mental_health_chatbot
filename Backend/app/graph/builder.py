from langgraph.graph import END, START, StateGraph

from app.graph.nodes.conversation import conversation_node
from app.graph.nodes.crisis_detector import crisis_detection_node
from app.graph.nodes.crisis_responder import crisis_response_node
from app.graph.nodes.intake import intake_node
from app.graph.nodes.mood_checkin import mood_checkin_node
from app.graph.nodes.tool_executor import tool_executor_node
from app.graph.state import AgentState


def _route_after_crisis_check(state: AgentState) -> str:
    risk = state.get("risk_level", "none")
    if risk in ("high", "critical"):
        return "crisis_responder"
    if state.get("needs_mood_checkin", False):
        return "mood_checkin"
    return "conversation"


def _route_after_conversation(state: AgentState) -> str:
    last_msg = state["messages"][-1] if state["messages"] else None
    if last_msg and hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        return "tool_executor"
    return END


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("intake", intake_node)
    graph.add_node("crisis_detector", crisis_detection_node)
    graph.add_node("crisis_responder", crisis_response_node)
    graph.add_node("mood_checkin", mood_checkin_node)
    graph.add_node("conversation", conversation_node)
    graph.add_node("tool_executor", tool_executor_node)

    graph.add_edge(START, "intake")
    graph.add_edge("intake", "crisis_detector")

    graph.add_conditional_edges(
        "crisis_detector",
        _route_after_crisis_check,
        {
            "crisis_responder": "crisis_responder",
            "mood_checkin": "mood_checkin",
            "conversation": "conversation",
        },
    )

    graph.add_edge("crisis_responder", END)

    graph.add_edge("mood_checkin", END)

    graph.add_conditional_edges(
        "conversation",
        _route_after_conversation,
        {
            "tool_executor": "tool_executor",
            END: END,
        },
    )

    graph.add_edge("tool_executor", "conversation")

    return graph
