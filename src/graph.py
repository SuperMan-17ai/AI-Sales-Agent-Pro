# src/graph.py
import json
from langgraph.graph import StateGraph, END
from .state import AgentState
from .agents import research_node, filter_node, writer_node

# 1. Initialize the Graph with our State
workflow = StateGraph(AgentState)

# 2. Add the Nodes (The Workers)
workflow.add_node("researcher", research_node)
workflow.add_node("filter", filter_node)
workflow.add_node("writer", writer_node)

# 3. Define the Edges (The Logic Flow)
# START -> Researcher
workflow.set_entry_point("researcher")

# Researcher -> Filter (Always move forward, never look back)
workflow.add_edge("researcher", "filter")

# Filter -> Conditional Logic
def filter_router(state: AgentState):
    """
    Decides where to go after the Filter Node.
    """
    # Force boolean check (handle strings just in case)
    qualified = state.get('is_qualified')
    
    if qualified is True:
        return "writer"  # Go to Writer
    else:
        return END       # Stop completely (Save money)

# Add the conditional edge
workflow.add_conditional_edges(
    "filter",           # From this node
    filter_router,      # Using this logic function
    {                   # Mapping results to destinations
        "writer": "writer",
        END: END
    }
)

# Writer -> END (Done)
workflow.add_edge("writer", END)

# 4. Compile the Application
app = workflow.compile()