# 🚀 Enterprise B2B Sales AI Agent

An autonomous, multi-agent AI system built to research, qualify, and draft highly personalized cold outreach for B2B sales using LangGraph, Groq (Llama 3.3 70B), and ChromaDB.

## 🧠 System Architecture



Unlike basic linear scripts, this system utilizes a cyclic state graph with specific agent personas:
1. **Parallel Ingestion:** `news_node` (Tavily Search API) and `tech_node` (BeautifulSoup) run simultaneously to build a 360° lead profile, minimizing latency.
2. **The Gatekeeper (Filter):** A reasoning LLM evaluates the lead against the Ideal Customer Profile (ICP), instantly disqualifying poor fits to protect domain reputation.
3. **Semantic HyDE RAG:** Replaces basic keyword search by generating "Hypothetical Success Stories" to retrieve the most semantically relevant case studies from the vector database.
4. **Agentic Reflection:** A 'Critic' node audits the drafted email for token length, tone (robotic vs. human), and personalization. If it fails, it is routed back to the Writer for a rewrite.

## 🛠️ Tech Stack & Engineering Standards
* **Framework:** LangGraph (Stateful Multi-Agent Orchestration)
* **LLM:** Groq / Llama 3.3 70B (High-speed inference)
* **Memory / RAG:** ChromaDB, SentenceTransformers
* **UI:** Streamlit
* **Code Quality:** Pyright (`strict` type-checking enforced), fully type-hinted for enterprise scalability.

## 🚀 Getting Started

1. Clone the repository:
   `git clone https://github.com/YourUsername/Enterprise-Sales-AI.git`
2. Install dependencies:
   `pip install -r requirements.txt`
3. Add your keys to a `.env` file:
   `GROQ_API_KEY=your_key`
   `TAVILY_API_KEY=your_key`
4. Run the interface:
   `streamlit run app.py`

## 📈 Business Impact
* **Reduces SDR research time** from 15 minutes per lead to ~10 seconds.
* **Eliminates generic spam** by forcing deep personalization based on real-time news and scraped data.
* **Protects Sender Reputation** by actively disqualifying bad fits before drafting begins.