from typing import TypedDict, List, Annotated, Optional
import operator

class AgentState(TypedDict):
    # Core Data
    lead_name: str
    company: str
    
    # Research Data - 'Annotated' tells LangGraph how to merge parallel tasks
    research_snippets: Annotated[List[str], operator.add]
    research_summary: str
    
    # Gatekeeper Logic
    is_qualified: bool
    qualification_reason: str
    
    # Writer & Reflection Loop
    draft_email: str
    critique_feedback: Optional[str]
    is_perfect: bool
    iteration_count: int