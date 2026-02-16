from typing import TypedDict, List, Annotated, Optional
import operator

class AgentState(TypedDict):
    # Sender Data
    sender_name: str
    sender_company: str
    sender_product: str

    # Core Data
    lead_name: str
    company: str
    
    # Research Data
    research_snippets: Annotated[List[str], operator.add]
    research_summary: str
    
    # Qualification Data
    is_qualified: bool
    qualification_reason: str
    
    # Email Drafting Data
    draft_email: str
    critique_feedback: Optional[str]
    is_perfect: bool
    iteration_count: int