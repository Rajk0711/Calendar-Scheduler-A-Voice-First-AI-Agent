import os
import datetime
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, SystemMessage
from .tools import list_events, create_event, update_event, delete_event, check_availability, get_daily_schedule
from dotenv import load_dotenv

load_dotenv()

# Define State
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    google_api_key=os.environ.get("GEMINI_API_KEY"),
    temperature=0
)

# Bind Tools
tools = [list_events, create_event, update_event, delete_event, check_availability, get_daily_schedule]
llm_with_tools = llm.bind_tools(tools)

# System Prompt
SYSTEM_PROMPT = f"""You are a helpful AI scheduling assistant. 
Current time: {datetime.datetime.now().isoformat()}.

RULES:
1. **Check Availability First**: Always check availability using 'check_availability' or 'list_events' before booking.
2. **Conflict Resolution**: If a slot is busy, DO NOT give up. Suggest the next best available time.
3. **Complex Time Parsing**: 
   - If the user says "after my flight", use 'list_events' to find the flight first, then calculate the time.
   - If the user says "next week", ask for a specific day or check the whole week.
4. **Ambiguity**: Ask clarifying questions if the request is vague (e.g., "sometime late").
5. **Confirmation**: Always confirm the details (Summary, Date, Time) before calling 'create_event'.
"""

# Define Nodes
def chatbot(state: AgentState):
    messages = state["messages"]
    # Prepend system message if not present (or just let the model handle it via context)
    # Ideally, we add it to the list if it's the first turn, but for simplicity:
    if not isinstance(messages[0], SystemMessage):
         messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
    
    response = llm_with_tools.invoke(messages)
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
