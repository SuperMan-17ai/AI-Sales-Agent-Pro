import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
    RAG_LLM_MODEL = os.getenv("RAG_LLM_MODEL", "llama-3.1-8b-instant")
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    CHROMA_PATH = "./chroma_db"

    @classmethod
    def validate(cls):
        if not cls.TAVILY_API_KEY:
             raise ValueError("CRITICAL: TAVILY_API_KEY is missing from .env file.")
        if not os.getenv("GROQ_API_KEY"):
             raise ValueError("CRITICAL: GROQ_API_KEY is missing from .env file.")
