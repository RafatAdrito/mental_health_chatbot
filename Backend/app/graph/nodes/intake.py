from app.graph.state import AgentState

MOOD_CHECKIN_INTERVAL = 5


def intake_node(state: AgentState) -> dict:
    metadata = state.get("session_metadata", {})
    turn_count = metadata.get("turn_count", 0) + 1
    last_mood_turn = metadata.get("last_mood_checkin_turn", 0)

    needs_checkin = False
    if turn_count == 1:
        needs_checkin = True
    elif (turn_count - last_mood_turn) >= MOOD_CHECKIN_INTERVAL:
        needs_checkin = True

    metadata = {**metadata, "turn_count": turn_count}

    return {
        "needs_mood_checkin": needs_checkin,
        "session_metadata": metadata,
    }
