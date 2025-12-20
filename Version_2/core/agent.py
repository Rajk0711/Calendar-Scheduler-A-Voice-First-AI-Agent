import os
import datetime
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, SystemMessage
from core.tools import (
    list_events, 
    create_event, 
    update_event, 
    delete_event, 
    get_event_details, 
    list_calendars, 
    check_availability, 
    find_available_slots, 
    send_email_notification
)
from dotenv import load_dotenv

load_dotenv()

# Define State
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# --- Google Gemini Configuration (Commented Out) ---
# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.0-flash",
#     google_api_key=os.environ.get("GEMINI_API_KEY"),
#     temperature=0
# )

# --- DeepSeek V3.2 Configuration (via Hugging Face router) ---
# Using ChatOpenAI wrapper with the router endpoint
llm = ChatOpenAI(
    model="deepseek-ai/DeepSeek-V3.2",
    openai_api_key=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
    openai_api_base="https://router.huggingface.co/v1",
    max_tokens=1024,
    temperature=0.2,
)

# Bind Tools
tools = [
    list_events, 
    create_event, 
    update_event, 
    delete_event, 
    get_event_details, 
    list_calendars, 
    check_availability, 
    find_available_slots, 
    send_email_notification
]
llm_with_tools = llm.bind_tools(tools)

# System Prompt
SYSTEM_PROMPT = f"""You are a professional AI Scheduling Agent (Version 2.0). 
Current time: {datetime.datetime.now().isoformat()}.

CAPABILITIES:
- Manage the user's primary and secondary Google Calendars.
- Check real-time availability and suggest optimal meeting slots.
- Create, update, and delete events with high accuracy.
- Send email notifications and summaries.

RULES:
1. **Always Check First**: Use 'check_availability' or 'find_available_slots' before proposing or booking a time.
2. **Conflict Resolution**: If a slot is taken, use 'find_available_slots' to offer 2-3 alternatives.
3. **Primary Calendar**: default to the 'primary' calendar unless the user specifies otherwise.
4. **Time Zone**: Assume the user's local time unless specified.
5. **Precision**: When updating or deleting, search for the event first to get the correct 'event_id'.
6. **Politeness**: Be concise, professional, and helpful.
"""

# Define Nodes
def chatbot(state: AgentState):
    messages = state["messages"]
    if not any(isinstance(m, SystemMessage) for m in messages):
         messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
    
    response = llm_with_tools.invoke(messages)
    # Post‑process the LLM output to make voice‑friendly time strings
    # Remove ":00" and ensure AM/PM is kept (e.g., "9:00 AM" → "9 AM")
    import re
    def _clean_time(text: str) -> str:
        # Replace patterns like "9:00 AM" or "12:00" with "9 AM" / "12"
        return re.sub(r"(\d{1,2}):00\s*(AM|PM)?", lambda m: f"{m.group(1)} {m.group(2) or ''}".strip(), text)
    if hasattr(response, "content"):
        response.content = _clean_time(response.content)
    return {"messages": [response]}

from langgraph.prebuilt import ToolNode
tool_node = ToolNode(tools)

# Define Graph
graph_builder = StateGraph(AgentState)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START, "chatbot")

# Conditional Edge
def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

graph_builder.add_conditional_edges("chatbot", should_continue, ["tools", END])
graph_builder.add_edge("tools", "chatbot")

# Compile
agent_executor = graph_builder.compile()
