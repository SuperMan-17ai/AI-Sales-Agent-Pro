import operator
from typing import Annotated, Any, Dict, List, TypedDict
from langgraph.graph import StateGraph, START, END

# --- 1. THE SHARED MEMORY (AGENT STATE) ---
class AgentState(TypedDict):
    # User Input Data
    sender_name: str
    sender_company: str
    sender_product: str
    lead_name: str
    company: str
    
    # Research & Logic Data
    # Annotated[List, operator.add] allows parallel nodes to append to this list
    research_snippets: Annotated[List[str], operator.add]
    research_summary: str
    is_qualified: bool
    qualification_reason: str
    draft_email: str
    iteration_count: int

# --- 2. THE AGENT NODES (FUNCTIONS) ---

def news_node(state: AgentState) -> Dict[str, Any]:
    print(f"📡 News Node: Searching for recent {state['company']} updates...")
    # Your Tavily Search Logic here
    new_info = [f"Found news about {state['company']} expansion."]
    return {"research_snippets": new_info}

def tech_node(state: AgentState) -> Dict[str, Any]:
    print(f"💻 Tech Node: Scraping {state['company']} website...")
    # Your BeautifulSoup Scraper Logic here
    tech_info = [f"{state['company']} is using modern tech stacks."]
    return {"research_snippets": tech_info}

def filter_node(state: AgentState) -> Dict[str, Any]:
    """Currently bypassed for testing, but registered in the system."""
    return {"is_qualified": True, "qualification_reason": "Testing Mode: Auto-Pass"}

def writer_node(state: AgentState) -> Dict[str, Any]:
    print(f"✍️ Writer Node: Drafting email for {state['lead_name']}...")
    # Logic: Combines all research_snippets into a personalized draft
    full_context = " ".join(state['research_snippets'])
    email = f"Hi {state['lead_name']}, I saw that {state['company']} is {full_context}..."
    return {"draft_email": email}

# --- 3. THE GRAPH ORCHESTRATOR (THE MAP) ---

# Initialize the workflow
workflow = StateGraph(AgentState)

# Define the Nodes
workflow.add_node("news_node", news_node)
workflow.add_node("tech_node", tech_node)
workflow.add_node("filter_node", filter_node)
workflow.add_node("writer_node", writer_node)

# --- THE "BYPASS" WIRING ---
# Start both research agents at the SAME time (Parallelism)
workflow.add_edge(START, "news_node")
workflow.add_edge(START, "tech_node")

# Both research agents feed directly into the Writer (Skipping Filter)
workflow.add_edge("news_node", "writer_node")
workflow.add_edge("tech_node", "writer_node")

# End the process after the draft is written
workflow.add_edge("writer_node", END)

# Compile the Graph
app = workflow.compile()