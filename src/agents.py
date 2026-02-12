# src/agents.py
import os
import json
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

# --- IMPORTS FROM OUR OTHER FILES ---
from .state import AgentState
from .tools import get_search_tool
from .rag import get_retriever  # <--- THIS WAS MISSING!

# 1. Initialize the Brain (Llama-3.3-70b via Groq)
llm_logic = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
llm_creative = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7)

# --- AGENT 1: THE RESEARCHER ---
def research_node(state: AgentState):
    """
    Looks up the lead on the internet and summarizes findings.
    """
    print(f"🕵️ RESEARCHER: Looking up {state['lead_name']} at {state['company']}...")
    
    tool = get_search_tool()
    
    # We search for 2 things: The Person and The Company News
    query = f"{state['lead_name']} {state['company']} linkedin profile and recent news"
    
    try:
        results = tool.invoke(query)
        # Combine snippets into a single text block
        search_text = "\n".join([res['content'] for res in results])
    except Exception as e:
        search_text = f"Error finding data: {e}"
    
    # We save the raw search data into the state
    return {
        "linkedin_summary": search_text, 
        "recent_news": search_text 
    }

# --- AGENT 2: THE FILTER (GATEKEEPER) ---
def filter_node(state: AgentState):
    """
    Decides if the lead is worth emailing.
    CRITERIA: Must be in Tech/Software AND have recent news.
    """
    print(f"🛡️ FILTER: Analyzing {state['lead_name']}...")
    
    # 1. We inspect what the researcher actually found
    research_content = state.get('linkedin_summary', '')
    
    # If research is empty or too short, AUTOMATIC FAIL
    if len(research_content) < 50:
        return {
            "is_qualified": False, 
            "qualification_reason": "Not enough research data found."
        }

    prompt = ChatPromptTemplate.from_template(
        """
        You are a strict Sales Qualification Manager.
        Analyze the research data.
        
        LEAD: {name} from {company}
        RESEARCH: {research}
        
        STRICT CRITERIA FOR "QUALIFIED" (Must meet ALL):
        1. Company is in Software, AI, or Tech infrastructure.
        2. The research contains SPECIFIC recent news (launches, funding, hiring).
        3. The research is NOT just generic "About Us" text.
        
        NEGATIVE CONSTRAINTS (When to DISQUALIFY):
        - If the company is a restaurant, retail store, or non-tech business -> DISQUALIFY.
        - If the research says "Access Denied" or "Captcha" -> DISQUALIFY.
        - If you are unsure -> DISQUALIFY.
        
        Return ONLY JSON:
        {{
            "is_qualified": boolean,
            "reason": "Be specific. Cite the news or explain the missing info."
        }}
        """
    )
    
    chain = prompt | llm_logic | JsonOutputParser()
    
    try:
        result = chain.invoke({
            "name": state['lead_name'],
            "company": state['company'],
            "research": research_content
        })
        
        print(f"   decision: {result['is_qualified']} -> {result['reason']}")
        return {
            "is_qualified": result['is_qualified'],
            "qualification_reason": result['reason']
        }
    except Exception as e:
        print(f"❌ FILTER ERROR: {e}")
        return {"is_qualified": False, "qualification_reason": "AI Error"}

# --- AGENT 3: THE WRITER ---
def writer_node(state: AgentState):
    """
    Drafts the email using RAG (Case Studies).
    """
    print(f"✍️ WRITER: Drafting email for {state['company']}...")
    
    # A. RETRIEVE KNOWLEDGE (The Fix)
    retriever = get_retriever()
    
    # FIX: Don't send the whole bio. Just send the relevant context.
    # "OpenAI" -> matches Tech case study
    # "HubSpot" -> matches SaaS case study
    query = f"{state['company']} technology business software"
    
    best_case_study = "We have helped similar companies scale." # Default
    
    try:
        # Ask the DB
        docs = retriever.invoke(query)
        
        if docs:
            best_case_study = docs[0].page_content
            # DEBUG PRINT: Show us exactly what it found!
            print(f"   ✅ SUCCESS: Found Case Study -> '{best_case_study[:60]}...'")
        else:
            print(f"   ⚠️ WARNING: Database returned 0 results.")
            
    except Exception as e:
        # PRINT THE ERROR so we can fix it
        print(f"   ❌ RAG ERROR: {e}")

    # B. GENERATE EMAIL (The Prompt Update)
    prompt = ChatPromptTemplate.from_template(
        """
        You are a B2B Copywriter. 
        Write a short cold email to {name} from {company}.
        
        1. THE PROOF (You MUST mention this exact story):
        "{case_study}"
        
        2. THE LEAD:
        {research}
        
        INSTRUCTIONS:
        - Start by mentioning their recent news/role.
        - Transition to: "We recently helped [Company from Proof] achieve [Result from Proof]..."
        - Ask for a chat.
        - Keep it under 100 words.
        """
    )
    
    chain = prompt | llm_creative | StrOutputParser()
    
    email_content = chain.invoke({
        "name": state['lead_name'],
        "company": state['company'],
        "research": state['linkedin_summary'],
        "case_study": best_case_study
    })
    
    return {"draft_email": email_content}