from typing import Any, Dict, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser

from .state import AgentState
from .rag import get_hyde_retriever
from .tools import get_search_tool, scrape_website
from .config import Config

def get_llm(temp: float = 0.0) -> ChatGroq:
    return ChatGroq(model=Config.LLM_MODEL, temperature=temp)

# --- PARALLEL NODE 1 ---
def news_node(state: AgentState) -> Dict[str, Any]:
    print(f"📰 Searching news for: {state['company']}...")
    search = get_search_tool()
    results: Any = search.invoke(f"latest business news {state['company']}")
    
    snippets: List[str] = []
    if isinstance(results, list):
        for res in results:
            if isinstance(res, dict) and "content" in res:
                snippets.append(str(res["content"]))
    return {"research_snippets": snippets}

# --- PARALLEL NODE 2 ---
def tech_node(state: AgentState) -> Dict[str, Any]:
    print(f"💻 Scraping website for: {state['company']}...")
    url = f"https://www.{state['company'].lower().replace(' ', '')}.com"
    content = scrape_website(url)
    return {"research_snippets": [content]}

# --- FILTER NODE ---
def filter_node(state: AgentState) -> Dict[str, Any]:
    print(f"🛡️ Filtering {state['lead_name']}...")
    snippets = state.get('research_snippets', [])
    summary = "\n".join(snippets) if snippets else "General research."

    # We use a simple string check first to avoid JSON parsing drama
    prompt = ChatPromptTemplate.from_template(
        "Based on this research: {summary}\n\n"
        "Should we reach out to {name} at {company} regarding {product}?\n"
        "Answer with 'YES' or 'NO' first, then a short reason."
    )
    
    # Get raw text response
    raw_res = (prompt | get_llm(0.1) | StrOutputParser()).invoke({
        "summary": summary,
        "name": state['lead_name'],
        "company": state['company'],
        "product": state.get('sender_product', 'our services')
    })

    # Simple Logic: If it says 'NO' (case insensitive), we disqualify. 
    # Otherwise, we go for it!
    is_qual = not raw_res.strip().upper().startswith("NO")
    
    return {
        "is_qualified": is_qual, 
        "qualification_reason": raw_res, 
        "research_summary": summary
    }

# --- WRITER NODE ---
def writer_node(state: AgentState) -> Dict[str, Any]:
    print(f"✍️ Drafting email for: {state['lead_name']}...")
    
    # Retrieve proof/case study from vector DB
    search_func = get_hyde_retriever()
    docs = search_func(state['company'], state.get('research_summary', ''))
    case_study = docs[0].page_content if docs else "We help similar companies scale."
    
    # Extract sender info with fallback defaults
    s_name = state.get('sender_name', 'John')
    s_comp = state.get('sender_company', 'AI Sales Pro')
    s_prod = state.get('sender_product', 'AI-powered lead research tools')

    prompt = ChatPromptTemplate.from_template(
        "You are a Senior Sales Executive at {sender_company}. Your name is {sender_name}. "
        "You are writing a cold email to {name} at {company} to sell {sender_product}. "
        "Context on them: {context}. "
        "Proof of our success: {proof}. "
        "CRITIQUE FEEDBACK TO FIX: {feedback}. "
        "\n\n"
        "STRICT RULES:\n"
        "1. Max 100 words.\n"
        "2. Use a professional, peer-to-peer tone.\n"
        "3. NEVER use square brackets like [Your Name] or [Company].\n"
        "4. Sign off specifically as '{sender_name}, {sender_company}'.\n"
        "5. Focus on how {sender_product} solves a specific problem found in the context."
    )
    
    email: Any = (prompt | get_llm(0.7) | StrOutputParser()).invoke({
        "sender_name": s_name,
        "sender_company": s_comp,
        "sender_product": s_prod,
        "name": state['lead_name'], 
        "company": state['company'],
        "context": state.get('research_summary', ''), 
        "proof": case_study, 
        "feedback": state.get('critique_feedback', "")
    })
    
    return {"draft_email": str(email)}
# --- CRITIC NODE ---
def critic_node(state: AgentState) -> Dict[str, Any]:
    iteration = state.get("iteration_count", 0)
    if iteration >= 1: # Stop loop after 1 rewrite
        return {"is_perfect": True, "iteration_count": iteration + 1}
        
    print(f"🧐 Critiquing draft (Attempt {iteration + 1})...")
    prompt = ChatPromptTemplate.from_template(
        "Review this cold email: {draft}. Is it natural and under 100 words? "
        "Return ONLY JSON: {{'is_perfect': bool, 'feedback': str}}"
    )
    
    try:
        res: Any = (prompt | get_llm() | JsonOutputParser()).invoke({"draft": state.get('draft_email', '')})
        is_perf = bool(res.get('is_perfect', False)) if isinstance(res, dict) else False
        feedback = str(res.get('feedback', '')) if isinstance(res, dict) else ""
    except Exception:
        is_perf, feedback = True, "Critique failed, passing as perfect."
        
    return {"is_perfect": is_perf, "critique_feedback": feedback, "iteration_count": iteration + 1}