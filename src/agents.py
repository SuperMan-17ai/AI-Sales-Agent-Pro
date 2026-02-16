from typing import Any, Dict, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser

from .state import AgentState
from .rag import get_hyde_retriever
from .tools import get_search_tool, scrape_website

def get_llm(temp: float = 0.0) -> ChatGroq:
    return ChatGroq(model="llama-3.3-70b-versatile", temperature=temp)

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
    snippets = state.get('research_snippets', [])
    summary = "\n".join(snippets) if snippets else "No data."
    
    print(f"🛡️ Filtering: {state['lead_name']}...")
    prompt = ChatPromptTemplate.from_template(
        "Should we sell B2B AI software to {name} at {company}? Context: {summary}. "
        "Return ONLY JSON: {{'is_qualified': bool, 'reason': str}}"
    )
    
    try:
        res: Any = (prompt | get_llm() | JsonOutputParser()).invoke({
            "name": state['lead_name'], 
            "company": state['company'], 
            "summary": summary
        })
        is_qual = bool(res.get('is_qualified', False)) if isinstance(res, dict) else False
        reason = str(res.get('reason', 'Parse error')) if isinstance(res, dict) else "Error"
    except Exception as e:
        is_qual, reason = False, f"Error: {e}"
        
    return {"is_qualified": is_qual, "qualification_reason": reason, "research_summary": summary}

# --- WRITER NODE ---
def writer_node(state: AgentState) -> Dict[str, Any]:
    print(f"✍️ Drafting email for: {state['lead_name']}...")
    search_func = get_hyde_retriever()
    docs = search_func(state['company'], state.get('research_summary', ''))
    case_study = docs[0].page_content if docs else "We help similar companies scale."
    
    # 🚨 THE FIX: Give the AI your identity and ban placeholders!
    prompt = ChatPromptTemplate.from_template(
        "Write a cold email from {sender_name} at {sender_company}. We sell {sender_product}. "
        "Write to {name}. Context: {context}. PROOF: {proof}. "
        "FEEDBACK TO FIX: {feedback}. Max 100 words. "
        "RULE: NEVER use placeholders like [Company Name] or [Your Name]. Write the actual text."
    )
    email: Any = (prompt | get_llm(0.7) | StrOutputParser()).invoke({
        "sender_name": state.get('sender_name', 'Sales Rep'),
        "sender_company": state.get('sender_company', 'Our AI Company'),
        "sender_product": state.get('sender_product', 'B2B AI Automation'),
        "name": state['lead_name'], 
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