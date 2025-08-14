# app/document_store.py
import os
from typing import List, Optional

# Delegate ingestion/loading to the root document_store module
from document_store import ingest_canonical_docs as _ingest_canonical_docs
from document_store import get_document_store as _get_document_store


class DocumentStore:
    """Thin wrapper over Chroma vector store with a simple query() API."""

    def __init__(self, persist_dir: str):
        self.persist_dir = persist_dir
        self.vectordb = _get_document_store(persist_dir)

    def is_available(self) -> bool:
        return self.vectordb is not None

    def query(self, text: str, k: int = 5) -> str:
        if not self.vectordb:
            return "No vector store available"
        try:
            docs = self.vectordb.similarity_search(text, k=k)
            return "\n\n".join(d.page_content for d in docs)
        except Exception as e:
            return f"Vector store query failed: {e}"


def ingest_canonical_docs(doc_paths: List[str], persist_dir: str):
    """Expose ingestion through app namespace."""
    return _ingest_canonical_docs(doc_paths, persist_dir)


def get_document_store(persist_dir: str) -> Optional[DocumentStore]:
    return DocumentStore(persist_dir)
