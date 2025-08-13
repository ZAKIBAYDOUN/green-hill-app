# precompute_vector_store.py
import os
from document_store import ingest_canonical_docs

if __name__ == "__main__":
    # Define paths to canonical documents
    doc_paths = [
        "docs/Strategic_Plan-GreenHill_v10-pre-FINAL.docx",
        "docs/appendex.docx", 
        "docs/ex sum conclusion final.docx",
        # Add more canonical documents here as needed
        # "docs/financial_projections.xlsx",
        # "docs/regulatory_compliance.pdf",
        # "docs/market_analysis.docx",
    ]
    
    # Get vector store directory from environment or use default
    persist_dir = os.getenv("VECTOR_STORE_DIR", "vector_store")
    
    print("🔄 Starting document ingestion...")
    print(f"📁 Target directory: {persist_dir}")
    print(f"📊 Documents to process: {len(doc_paths)}")
    
    # Ingest documents and create vector store
    result = ingest_canonical_docs(doc_paths, persist_dir)
    
    if result:
        print("✅ Vector store populated successfully!")
        print(f"📍 Location: {persist_dir}")
        print("🚀 Ready for deployment!")
    else:
        print("❌ Vector store creation failed")
        print("Check that documents exist and dependencies are installed")
        
    print("\n📋 Next steps:")
    print("1. Add vector_store/ to .gitignore")
    print("2. Set VECTOR_STORE_DIR environment variable in deployment")
    print("3. Deploy with: langgraph deploy")
