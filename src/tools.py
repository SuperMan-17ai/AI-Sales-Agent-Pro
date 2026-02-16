import os
import requests  # type: ignore
from bs4 import BeautifulSoup  # type: ignore
from langchain_community.tools.tavily_search import TavilySearchResults

# ... rest of your code stays exactly the same ...

def get_search_tool() -> TavilySearchResults:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("CRITICAL: TAVILY_API_KEY is missing from .env file.")
    return TavilySearchResults(api_key=api_key)

def scrape_website(url: str) -> str:
    """Scrapes a website safely and returns clean text."""
    try:
        # Prevent hanging forever with a 10-second timeout
        response = requests.get(url, timeout=10)
        response.raise_for_status() # Check for 404/500 errors
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Strip out code, keep only text
        for script in soup(["script", "style"]):
            script.extract()
            
        text = " ".join(soup.get_text().split())
        return text[:2000] # Return max 2000 chars to save tokens
    except Exception as e:
        return f"Scraping failed for {url}: {str(e)}"