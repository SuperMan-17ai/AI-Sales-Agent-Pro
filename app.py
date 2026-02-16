import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file BEFORE importing the graph
load_dotenv()

from src.graph import app as agent_app

st.set_page_config(page_title="Pro Sales AI", page_icon="🚀", layout="wide")
st.title("🚀 Autonomous Sales AI (Industry Grade)")

# 🚨 THE FIX: Add a sidebar for the user's identity
st.sidebar.header("🎯 Your Campaign Details")
sender_name = st.sidebar.text_input("Your Name:", "John Doe")
sender_company = st.sidebar.text_input("Your Company:", "AI Workflow Solutions")
sender_product = st.sidebar.text_area("What are you selling?", "AI agents that reduce SDR research time.")

uploaded_file = st.file_uploader("Upload leads.csv", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    col1, col2 = st.columns(2)
    
    with col1:
        # Defaults to the 1st column
        name_col = st.selectbox("Name Column:", df.columns, index=0)
        
    with col2:
        # Defaults to the 2nd column
        default_company_idx = 1 if len(df.columns) > 1 else 0
        company_col = st.selectbox("Company Column:", df.columns, index=default_company_idx)

    if st.button("Start Agents"):
        progress = st.progress(0)
        results = []
        log_txt = st.empty()
        
        for i, (index, row) in enumerate(df.iterrows()):
            lead_name = str(row[name_col])
            company = str(row[company_col])
            
            log_txt.text(f"⏳ Processing {i + 1}/{len(df)}: {lead_name} @ {company}...")
            
            initial_state = {
                "sender_name": sender_name,
                "sender_company": sender_company,
                "sender_product": sender_product,
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
            
            output = agent_app.invoke(initial_state) # type: ignore
            
            is_qual = output.get('is_qualified', False)
            results.append({
                "Name": lead_name,
                "Company": company,
                "Status": "✅ Yes" if is_qual else "🚫 No",
                "Reason": output.get('qualification_reason', ''),
                "Draft": output.get('draft_email', '') if is_qual else ""
            })
            
            progress.progress((i + 1) / len(df))

        log_txt.text("✅ All leads processed!")
        final_df = pd.DataFrame(results)
        st.dataframe(final_df)
        
        csv = final_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, "results.csv", "text/csv")