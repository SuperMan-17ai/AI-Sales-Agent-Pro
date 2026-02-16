# main.py
import pandas as pd
from src.graph import app

def run():
    print("🚀 STARTING AI SALES AGENT...")
    
    # 1. Load the Leads
    try:
        leads = pd.read_csv("data/leads.csv")
        print(f"📄 Loaded {len(leads)} leads from CSV.")
    except FileNotFoundError:
        print("❌ ERROR: data/leads.csv not found. Please create it.")
        return

    # 2. Process Each Lead
    for index, row in leads.iterrows():
        lead_name = row['name']
        company = row['company']
        
        print(f"\n--- PROCESSING: {lead_name} ({company}) ---")
        
        # Initialize the state with basic info
        initial_state = {
            "sender_name": "AI Sales Agent",
            "sender_company": "Automated Systems",
            "sender_product": "AI Sales Solutions",
            "lead_name": lead_name,
            "company": company,
            "research_snippets": [],
            "research_summary": "",
            "is_qualified": False,
            "qualification_reason": "",
            "draft_email": "",
            "critique_feedback": None,
            "is_perfect": False,
            "iteration_count": 0
        }
        
        # Run the Graph!
        try:
            result = app.invoke(initial_state)
            
            # Print the Result
            if result['is_qualified']:
                print(f"✅ QUALIFIED! Draft Email:\n")
                print("-" * 40)
                print(result['draft_email'])
                print("-" * 40)
            else:
                print(f"🚫 DISQUALIFIED: {result['qualification_reason']}")
                
        except Exception as e:
            print(f"❌ ERROR processing {lead_name}: {e}")

if __name__ == "__main__":
    run()