from functools import lru_cache
from typing import List, Callable, Any
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.documents import Document
from .config import Config

@lru_cache(maxsize=1)
def get_vectorstore() -> Chroma:
    embedding_function = SentenceTransformerEmbeddings(model_name=Config.EMBEDDING_MODEL)
    return Chroma(persist_directory=Config.CHROMA_PATH, embedding_function=embedding_function)

def get_hyde_retriever() -> Callable[[str, str], List[Document]]:
    """Returns a function that performs Hypothetical Document Search."""
    
    llm_hyde = ChatGroq(model=Config.RAG_LLM_MODEL, temperature=0)
    db = get_vectorstore()
    
    hyde_prompt = ChatPromptTemplate.from_template(
        "Generate a hypothetical success story about a company similar to {company} "
        "solving challenges using AI. Use industry-specific terms. Context: {query}"
    )

    def search(company: str, query: str) -> List[Document]:
        chain = hyde_prompt | llm_hyde
        hypo_doc: Any = chain.invoke({"company": company, "query": query})
        
        # Ensure content is extracted cleanly as a string
        content = getattr(hypo_doc, "content", "")
        return db.similarity_search(str(content), k=1)
    
    return search