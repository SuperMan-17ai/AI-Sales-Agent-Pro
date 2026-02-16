from typing import Literal, Any
from langgraph.graph import StateGraph, START  # <-- Removed END from here!
from .state import AgentState
from .agents import news_node, tech_node, filter_node, writer_node, critic_node

def filter_router(state: AgentState) -> Literal["writer", "__end__"]:
    if state.get("is_qualified"):
        return "writer"
    return "__end__"

def critic_router(state: AgentState) -> Literal["writer", "__end__"]:
    if state.get("is_perfect"):
        return "__end__"
    return "writer"

def build_graph() -> Any:
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("news", news_node)
    workflow.add_node("tech", tech_node)
    workflow.add_node("filter", filter_node)
    workflow.add_node("writer", writer_node)
    workflow.add_node("critic", critic_node)

    # Parallel Start
    workflow.add_edge(START, "news")
    workflow.add_edge(START, "tech")

    # Merge into Filter
    workflow.add_edge("news", "filter")
    workflow.add_edge("tech", "filter")

    # Gatekeeper Logic
    workflow.add_conditional_edges("filter", filter_router)
    
    # Reflection Loop Logic
    workflow.add_edge("writer", "critic")
    workflow.add_conditional_edges("critic", critic_router)

    return workflow.compile()

app = build_graph()