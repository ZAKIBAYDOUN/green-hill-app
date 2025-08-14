# app/document_store.py
import os
from typing import List, Optional, Dict, Any
import uuid
from langchain.text_splitter import RecursiveCharacterTextSplitter
from document_store import _get_embeddings as _root_get_embeddings

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

    # --- Write APIs ---
    def _ensure_store(self):
        """Ensure a Chroma store exists for upserts; create if missing."""
        if self.vectordb:
            return self.vectordb
        try:
            from langchain_chroma import Chroma
            os.makedirs(self.persist_dir, exist_ok=True)
            embeddings = _root_get_embeddings()
            self.vectordb = Chroma(
                persist_directory=self.persist_dir,
                embedding_function=embeddings,
            )
            return self.vectordb
        except Exception as e:
            print(f"Error creating vector store for upsert: {e}")
            return None

    def add_texts(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None, ids: Optional[List[str]] = None) -> bool:
        """Upsert raw texts into the vector store."""
        store = self._ensure_store()
        if not store:
            return False
        try:
            store.add_texts(texts=texts, metadatas=metadatas, ids=ids)
            return True
        except Exception as e:
            print(f"Error adding texts: {e}")
            return False

    def add_agent_outputs(self, state: Any) -> bool:
        """Upsert agent outputs from a TwinState as retrievable documents.

        Splits long content, attaches metadata for traceability.
        """
        # Collect texts from known agent outputs
        items: List[tuple[str, Dict[str, Any]]] = []
        def _pack(name: str, data: Optional[Dict[str, Any]]):
            if not data:
                return
            summary = data.get("analysis") or str(data)
            items.append((summary, {
                "source": "agent_output",
                "agent": name,
                "origin": getattr(state, "origin", None),
                "source_id": getattr(state, "source_id", None),
                "question": getattr(state, "question", None),
                "timestamp": getattr(state, "timestamp", None),
            }))

        _pack("strategy", getattr(state, "strategy_output", None))
        _pack("finance", getattr(state, "finance_output", None))
        _pack("operations", getattr(state, "operations_output", None))
        _pack("market", getattr(state, "market_output", None))
        _pack("risk", getattr(state, "risk_output", None))
        _pack("compliance", getattr(state, "compliance_output", None))
        _pack("innovation", getattr(state, "innovation_output", None))
        gh = getattr(state, "green_hill_response", None) or {}
        if gh.get("memo"):
            items.append((gh["memo"], {
                "source": "agent_output",
                "agent": "green_hill_gpt",
                "question": getattr(state, "question", None),
            }))

        if not items:
            return True

        # Chunking
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts: List[str] = []
        metas: List[Dict[str, Any]] = []
        ids: List[str] = []
        for text, meta in items:
            chunks = splitter.split_text(text)
            base_id = str(uuid.uuid4())
            for i, ch in enumerate(chunks):
                texts.append(ch)
                metas.append({**meta, "chunk": i})
                ids.append(f"agent:{base_id}:{i}")

        return self.add_texts(texts, metas, ids)


def ingest_canonical_docs(doc_paths: List[str], persist_dir: str):
    """Expose ingestion through app namespace."""
    return _ingest_canonical_docs(doc_paths, persist_dir)


def get_document_store(persist_dir: str) -> Optional[DocumentStore]:
    return DocumentStore(persist_dir)
