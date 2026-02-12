# src/state.py
from typing import TypedDict, List

class AgentState(TypedDict):
    """
    This is the 'Shared Brain' of our Agent.
    Every node (Researcher, Filter, Writer) will read/write to this dictionary.
    """
    
    # 1. Input Data (From your CSV)
    lead_name: str
    company: str
    role: str
    email: str
    
    # 2. Research Data (Added by the Research Node)
    linkedin_summary: str   # What we found on their profile
    recent_news: str        # Latest news about their company
    
    # 3. Decision Data (Added by the Filter Node)
    is_qualified: bool      # True/False (Did they pass our checks?)
    qualification_reason: str # Why did we pass/fail them?
    
    # 4. Strategy Data (Added by the RAG Node)
    relevant_case_study: str # The best case study we found in our DB
    
    # 5. Output Data (Added by the Writer Node)
    draft_email: str        # The final email content
    critique_feedback: str  # (Optional) If we add an 'Editor' agent later