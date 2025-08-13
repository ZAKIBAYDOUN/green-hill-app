# app/document_store.py
import os
from typing import List, Optional

DEFAULT_EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

class DocumentStore:
    """Vector store wrapper with graceful fallbacks"""
    
    def __init__(self, persist_dir: str = "./chroma_db"):
        self.persist_dir = persist_dir
        self.vector_store = None
        self._availability = None
        
        # Try to initialize vector store
        try:
            self._initialize_vector_store()
        except Exception as e:
            print(f"Warning: Vector store initialization failed: {e}")
            print("Document store will use fallback mode")
    
    def _initialize_vector_store(self):
