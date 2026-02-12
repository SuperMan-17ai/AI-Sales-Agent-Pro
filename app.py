import streamlit as st
import pandas as pd
from src.graph import app as agent_app

# Page Config
st.set_page_config(page_title="AI Sales SDR", page_icon="🚀", layout="wide")

st.title("🚀 Autonomous AI Sales Agent")
st.markdown("### Upload any CSV -> Map Columns -> Get Emails")

# 1. File Uploader
uploaded_file = st.file_uploader("Upload leads.csv", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("✅ Preview of your data:")
    st.dataframe(df.head(3))

    # --- THE FIX: DYNAMIC COLUMN MAPPING ---
    st.subheader("Step 2: Map Your Columns")
    col1, col2 = st.columns(2)
    
    with col1:
        # Ask user: "Which column contains the Person's Name?"
        name_col = st.selectbox("Select the 'Name' column:", df.columns)
        
    with col2:
        # Ask user: "Which column contains the Company Name?"
        company_col = st.selectbox("Select the 'Company' column:", df.columns)
        
    st.info(f"Using '{name_col}' for Names and '{company_col}' for Companies.")

    # 2. The "Start" Button
    if st.button("Start Outreach Agent"):
        
        progress_bar = st.progress(0)
        results = []
        status_text = st.empty()
        
        total_leads = len(df)
        
        for index, row in df.iterrows():
            # USE THE MAPPED COLUMNS (Not hardcoded names)
            lead_name = str(row[name_col])
            company = str(row[company_col])
            
            # Update UI
            status_text.text(f"⏳ Processing {index+1}/{total_leads}: {lead_name} @ {company}...")
            
            # Initial State
            initial_state = {
                "lead_name": lead_name,
                "company": company,
                "linkedin_summary": "",
                "draft_email": ""
            }
            
            try:
                # Run the Agent!
                output = agent_app.invoke(initial_state)
                
                # Check results
                is_qualified = output.get('is_qualified', False)
                reason = output.get('qualification_reason', "Unknown")
                email_draft = output.get('draft_email', "N/A")

                # Save Results
                results.append({
                    "Original_Name": lead_name,
                    "Original_Company": company,
                    "Status": "✅ Qualified" if is_qualified else "🚫 Disqualified",
                    "Reason": reason if not is_qualified else "Matches Criteria",
                    "AI_Email_Draft": email_draft if is_qualified else ""
                })
                
            except Exception as e:
                st.error(f"Error processing {lead_name}: {e}")
            
            # Update Progress
            progress_bar.progress((index + 1) / total_leads)

        # 3. Show Final Results
        status_text.text("✅ All leads processed!")
        results_df = pd.DataFrame(results)
        
        st.subheader("Generated Campaign Results")
        st.dataframe(results_df)
        
        # 4. Download Button
        csv = results_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Download Results CSV",
            csv,
            "ai_outreach_results.csv",
            "text/csv",
            key='download-csv'
        )