# src/tools.py
import os
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults

# Load API Keys
load_dotenv()

def get_search_tool():
    """
    Returns a Tool that can search the web.
    We set 'max_results=2' to save tokens (money).
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("❌ TAVILY_API_KEY missing in .env")
        
    # k=2 means "Give me the top 2 results only"
    return TavilySearchResults(k=2)

def search_web(query: str):
    """
    A simple wrapper function to test the tool manually.
    """
    tool = get_search_tool()
    try:
        results = tool.invoke(query)
        # Combine the snippets into one string for the AI to read
        return "\n".join([res['content'] for res in results])
    except Exception as e:
        return f"Error searching web: {e}"