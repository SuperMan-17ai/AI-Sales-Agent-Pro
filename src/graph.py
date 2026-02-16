from typing import Literal
from langgraph.graph import StateGraph, START, END
from .state import AgentState
from .agents import news_node, tech_node, filter_node, writer_node, critic_node

# --- THE GRAPH ORCHESTRATOR ---

# Initialize the workflow
workflow = StateGraph(AgentState)

# Define the Nodes
workflow.add_node("news_node", news_node)
workflow.add_node("tech_node", tech_node)
workflow.add_node("filter_node", filter_node)
workflow.add_node("writer_node", writer_node)
workflow.add_node("critic_node", critic_node)

# --- THE WIRING ---
# We sequence the research to ensure all data is gathered before filtering
# START -> News -> Tech -> Filter
workflow.add_edge(START, "news_node")
workflow.add_edge("news_node", "tech_node")
workflow.add_edge("tech_node", "filter_node")

# Conditional Logic for Filter
def check_qualification(state: AgentState) -> Literal["writer_node", END]:
    if state.get("is_qualified"):
        return "writer_node"
    return END

workflow.add_conditional_edges(
    "filter_node",
    check_qualification,
    {
        "writer_node": "writer_node",
        END: END
    }
)

# Writer -> Critic
workflow.add_edge("writer_node", "critic_node")

# Conditional Logic for Critic
def check_critic(state: AgentState) -> Literal["writer_node", END]:
    if state.get("is_perfect"):
        return END
    return "writer_node"

workflow.add_conditional_edges(
    "critic_node",
    check_critic,
    {
        "writer_node": "writer_node",
        END: END
    }
)

# Compile the Graph
app = workflow.compile()