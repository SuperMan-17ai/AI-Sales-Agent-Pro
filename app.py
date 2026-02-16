import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file BEFORE importing the graph
load_dotenv()

from src.graph import app as agent_app

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AI Sales Agent Pro",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR PROFESSIONAL AESTHETIC ---
# Uses a clean, modern color palette: Slate #2C3E50, Emerald #2ECC71, Cloud #ECF0F1
st.markdown("""
<style>
    /* Main Background & Text */
    .stApp {
        background-color: #F8F9FA;
        color: #212529;
    }
    
    /* Headers & Titles */
    h1, h2, h3 {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #2C3E50;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E9ECEF;
    }
    
    /* Cards / Containers */
    .stCard {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    /* Success/Error Messages */
    .stSuccess {
        background-color: #D4EDDA;
        color: #155724;
    }
    .stError {
        background-color: #F8D7DA;
        color: #721C24;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #2C3E50;
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1A252F;
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
st.markdown("""
<div style="text-align: center; padding: 40px 0;">
    <h1 style="font-size: 3rem; margin-bottom: 10px;">🤖 AI Sales Agent Pro</h1>
    <p style="font-size: 1.2rem; color: #7F8C8D;">Automated Research & Outreach at Scale</p>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.header("🎯 Campaign Settings")
    
    with st.expander("👤 Sender Information", expanded=True):
        sender_name = st.text_input("Name", "John Doe")
        sender_company = st.text_input("Company", "Acme Corp")
        sender_product = st.text_area("Value Proposition", "We help companies scale their sales using AI agents.")
    
    st.markdown("---")
    uploaded_file = st.file_uploader("📂 Upload Leads (CSV)", type=["csv"], help="Must contain 'name' and 'company' columns.")

# --- MAIN APP LOGIC ---
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    # --- METRICS DASHBOARD (TOP) ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Leads", len(df))
    col2.metric("Est. Time", f"~{len(df) * 30 // 60} mins")
    col3.metric("Status", "Ready to Start")
    
    st.markdown("---")
    
    # --- COLUMN MAPPING ---
    c1, c2 = st.columns(2)
    with c1:
        name_col = st.selectbox("Select 'Name' Column", df.columns, index=0)
    with c2:
        default_company_idx = 1 if len(df.columns) > 1 else 0
        company_col = st.selectbox("Select 'Company' Column", df.columns, index=default_company_idx)
    
    # --- ACTION BUTTON ---
    if st.button("🚀 Launch AI Agents", use_container_width=True):
        st.write("---")
        progress_bar = st.progress(0)
        status_text = st.empty()
        results = []
        
        # Create a container for live results
        results_container = st.container()
        
        for i, (index, row) in enumerate(df.iterrows()):
            lead_name = str(row[name_col])
            company = str(row[company_col])
            
            # Update status
            status_text.markdown(f"**🔄 Processing ({i+1}/{len(df)}):** `{lead_name} @ {company}`")
            
            # --- AGENT EXECUTION ---
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
            
            try:
                output = agent_app.invoke(initial_state) # type: ignore
                is_qual = output.get('is_qualified', False)
                reason = output.get('qualification_reason', 'N/A')
                draft = output.get('draft_email', '')
            except Exception as e:
                is_qual = False
                reason = f"Error: {str(e)}"
                draft = ""
            
            # --- SAVE RESULT ---
            result_entry = {
                "Name": lead_name,
                "Company": company,
                "Qualified": "✅ Yes" if is_qual else "🚫 No",
                "Reason": reason,
                "Draft Email": draft
            }
            results.append(result_entry)
            
            # --- LIVE DISPLAY ---
            with results_container:
                with st.chat_message("assistant" if is_qual else "user", avatar="✅" if is_qual else "🛑"):
                    st.markdown(f"**{lead_name}** - {result_entry['Qualified']}")
                    if is_qual:
                        with st.expander("📧 View Draft Email"):
                            st.text(draft)
                    else:
                        st.caption(f"Reason: {reason}")
            
            # Update Progress
            progress_bar.progress((i + 1) / len(df))
        
        status_text.markdown("### ✅ Processing Complete!")
        
        # --- RESULTS & DOWNLOAD ---
        final_df = pd.DataFrame(results)
        
        st.markdown("---")
        st.header("📊 Campaign Results")
        
        # Summary Metrics
        qualified_count = len(final_df[final_df["Qualified"] == "✅ Yes"])
        m1, m2 = st.columns(2)
        m1.metric("Qualified Leads", qualified_count, delta=f"{qualified_count/len(df):.1%}")
        m2.metric("Disqualified", len(df) - qualified_count)
        
        # Dataframe
        st.dataframe(final_df, use_container_width=True)
        
        # Download Button
        csv = final_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Results CSV",
            data=csv,
            file_name="ai_agent_results.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True
        )

else:
    # Empty State
    st.info("👆 Please upload a CSV file to begin.")
    
    # Demo Data Expander
    with st.expander("Need a sample file?"):
        st.markdown("""
        Create a CSV with these columns:
        - **name**: Lead Name
        - **company**: Company Name
        
        Example:
        ```csv
        name,company
        Elon Musk,Tesla
        Jensen Huang,Nvidia
        ```
        """)