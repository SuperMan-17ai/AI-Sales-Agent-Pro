# src/rag.py
import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
# FIXED IMPORT:
from langchain_core.documents import Document

# 1. Setup the Embedding Model (Free, Local, Fast)
# This converts text into numbers (Vectors)
print("⏳ Loading Embedding Model... (This happens once)")
embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# 2. Define Your "Success Stories" (The Knowledge Base)
case_studies = [
    Document(
        page_content="Case Study: FinTech Automation. We helped a NeoBank called 'PayFast' automate their customer support using AI Agents. Result: Reduced ticket resolution time by 80% and saved $50k/month.",
        metadata={"industry": "FinTech", "type": "Support"}
    ),
    Document(
        page_content="Case Study: SaaS Sales Outreach. We built an AI SDR for 'CloudScale', a B2B SaaS company. Result: The agent booked 45 meetings in the first week, generating $120k in pipeline.",
        metadata={"industry": "SaaS", "type": "Sales"}
    ),
    Document(
        page_content="Case Study: Healthcare Data Entry. We implemented an OCR agent for 'MediCare' to read patient PDF forms. Result: Eliminated manual data entry errors and processed 500 forms/day.",
        metadata={"industry": "Healthcare", "type": "Operations"}
    )
]

# 3. Initialize the Vector Database (ChromaDB)
DB_PATH = "./chroma_db"

def initialize_knowledge_base():
    """
    Run this ONCE to save your case studies to disk.
    """
    print("💾 Creating Vector Database...")
    db = Chroma.from_documents(
        documents=case_studies,
        embedding=embedding_function,
        persist_directory=DB_PATH
    )
    print("✅ Knowledge Base Saved!")
    return db

def get_retriever():
    """
    Returns the tool that allows the Agent to search this database.
    """
    db = Chroma(
        persist_directory=DB_PATH,
        embedding_function=embedding_function
    )
    # k=1 means "Give me the SINGLE best matching case study"
    return db.as_retriever(search_kwargs={"k": 1})

# Run this block only if you execute specificially "python src/rag.py"
if __name__ == "__main__":
    initialize_knowledge_base()