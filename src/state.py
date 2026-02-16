from typing import TypedDict, List, Annotated, Optional
import operator

class AgentState(TypedDict):
    # Sender Data (NEW)
    sender_name: str
    sender_company: str
    sender_product: str

    # Core Data
    lead_name: str
    company: str
    
    # ... (keep the rest of your state exactly the same) ...
    research_snippets: Annotated[List[str], operator.add]
    research_summary: str
    is_qualified: bool
    qualification_reason: str
    draft_email: str
    critique_feedback: Optional[str]
    is_perfect: bool
    iteration_count: int