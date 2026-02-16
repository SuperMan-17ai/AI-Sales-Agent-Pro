from typing import List, Callable
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.documents import Document

def get_hyde_retriever() -> Callable[[str, str], List[Document]]:
    """Returns a function that performs Hypothetical Document Search."""
    
    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    llm_hyde = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    db = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function)
    
    hyde_prompt = ChatPromptTemplate.from_template(
        "Generate a hypothetical success story about a company similar to {company} "
        "solving challenges using AI. Use industry-specific terms. Context: {query}"
    )

    def search(company: str, query: str) -> List[Document]:
        chain = hyde_prompt | llm_hyde
        hypo_doc = chain.invoke({"company": company, "query": query})
        
        # Ensure content is extracted cleanly as a string
        content = getattr(hypo_doc, "content", "")
        return db.similarity_search(str(content), k=1)
    
    return search