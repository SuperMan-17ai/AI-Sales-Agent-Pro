import sys

print("⏳ Testing imports... (This might take 5-10 seconds)")

try:
    import langchain
    print(f"✅ LangChain is ready (v{langchain.__version__})")
    
    import langgraph
    print("✅ LangGraph is ready")
    
    import chromadb
    print(f"✅ ChromaDB is ready (v{chromadb.__version__})")
    
    from langchain_groq import ChatGroq
    print("✅ Groq Connector is ready")
    
    print("\n🎉 SUCCESS: All systems go! You are ready to build the Agent.")
    
except ImportError as e:
    print(f"\n❌ IMPORT ERROR: {e}")
    print("Try running: pip install -r requirements.txt")
except Exception as e:
    print(f"\n❌ SYSTEM ERROR: {e}")