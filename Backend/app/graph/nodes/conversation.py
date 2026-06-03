from langchain_core.messages import AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import get_settings
from app.graph.prompts import SYSTEM_PROMPT
from app.graph.state import AgentState
from app.tools.coping import get_coping_strategies
from app.tools.location import find_nearby_help
from app.utils.safety import sanitize_response

TOOLS = [find_nearby_help, get_coping_strategies]


async def conversation_node(state: AgentState) -> dict:
    settings = get_settings()
    llm = ChatGoogleGenerativeAI(
        model=settings.gemini_model_name,
        google_api_key=settings.google_api_key,
        streaming=True,
        temperature=0.7,
        max_tokens=1024,
    )

    llm_with_tools = llm.bind_tools(TOOLS)

    user_context = state.get("user_context", "")
    system_content = SYSTEM_PROMPT.format(
        user_context=f"\nUSER CONTEXT:\n{user_context}" if user_context else ""
    )

    messages = [SystemMessage(content=system_content)] + list(state["messages"])

    full_content = ""
    async for chunk in llm_with_tools.astream(messages):
        if hasattr(chunk, "content") and isinstance(chunk.content, str):
            full_content += chunk.content

    # Create a response message from the streamed content
    response = AIMessage(content=full_content)
    
    # Check if original had tool calls by doing one more invoke to get structured output
    if not full_content or full_content.strip() == "":
        response = await llm_with_tools.ainvoke(messages)
    
    if isinstance(response.content, str) and not response.tool_calls:
        response.content = sanitize_response(response.content)

    return {"messages": [response]}
