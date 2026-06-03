import json

from langchain_core.messages import ToolMessage

from app.graph.state import AgentState
from app.tools.coping import get_coping_strategies
from app.tools.location import find_nearby_help

_TOOL_REGISTRY = {
    "find_nearby_help": find_nearby_help,
    "get_coping_strategies": get_coping_strategies,
}


async def tool_executor_node(state: AgentState) -> dict:
    last_message = state["messages"][-1]

    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        return {}

    tool_messages = []
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        tool_fn = _TOOL_REGISTRY.get(tool_name)
        if tool_fn is None:
            tool_messages.append(
                ToolMessage(
                    content=f"Error: Unknown tool '{tool_name}'",
                    tool_call_id=tool_call["id"],
                )
            )
            continue

        try:
            if tool_name == "find_nearby_help":
                if "latitude" not in tool_args and state.get("latitude"):
                    tool_args["latitude"] = state["latitude"]
                if "longitude" not in tool_args and state.get("longitude"):
                    tool_args["longitude"] = state["longitude"]

            result = await tool_fn.ainvoke(tool_args)
            if not isinstance(result, str):
                result = json.dumps(result)

            tool_messages.append(
                ToolMessage(
                    content=result,
                    tool_call_id=tool_call["id"],
                )
            )
        except Exception as e:
            tool_messages.append(
                ToolMessage(
                    content=f"Error executing tool '{tool_name}': {str(e)}",
                    tool_call_id=tool_call["id"],
                )
            )

    return {"messages": tool_messages}
