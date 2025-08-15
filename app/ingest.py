# app/ingest.py
"""Simple document ingestion helpers.

This module previously relied entirely on LangChain loaders and text splitting
utilities which require hefty optional dependencies.  For the purposes of the
tests in this kata we support lightweight Markdown and JSONL ingestion without
those extras.  When the optional dependencies are available we will also ingest
PDF/Word/Excel documents using the original approach.
"""

import json
import os
import glob
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Document:
    """Minimal stand-in for ``langchain``'s Document class."""

    page_content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


def _load_md(path: str) -> List[Document]:
    docs: List[Document] = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            docs.append(Document(line, {"source": path, "line": i}))
    return docs


def _load_jsonl(path: str) -> List[Document]:
    docs: List[Document] = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                print(f"Malformed line {i} in {path}")
                continue
            text = obj.get("text", "")
            meta = obj.get("metadata", {}) or {}
            docs.append(Document(text, {"source": path, "line": i, **meta}))
    return docs


def ingest_docs(source_dir: str, persist_dir: str, embed_model: str = None):
    """Ingest documents from source directory into a vector store."""

    docs: List[Document] = []

    # --- Lightweight formats: Markdown and JSONL ---
    for path in glob.glob(os.path.join(source_dir, "*.md")):
        docs.extend(_load_md(path))
    for path in glob.glob(os.path.join(source_dir, "*.jsonl")):
        docs.extend(_load_jsonl(path))

    # --- Optional heavy formats via LangChain loaders ---
    loaded_docs: List[Any] = []
    try:
        from langchain_community.document_loaders import (
            PyPDFLoader, Docx2txtLoader, UnstructuredExcelLoader
        )

        loaders = []
        supported_extensions = {
            "*.pdf": PyPDFLoader,
            "*.docx": Docx2txtLoader,
            "*.xlsx": UnstructuredExcelLoader,
            "*.xls": UnstructuredExcelLoader,
        }

        for pattern, loader_class in supported_extensions.items():
            for file_path in glob.glob(os.path.join(source_dir, pattern)):
                try:
                    loaders.append(loader_class(file_path))
                    print(f"Found: {file_path}")
                except Exception as e:  # pragma: no cover - loader failures
                    print(f"Failed to load {file_path}: {e}")

        for loader in loaders:
            try:
                loaded_docs.extend(loader.load())
            except Exception as e:  # pragma: no cover - loader failures
                print(f"Failed to process {loader}: {e}")

    except ImportError:
        # The heavy loaders are optional; absence is fine for tests.
        pass

    if loaded_docs:
        try:
            from langchain.text_splitter import RecursiveCharacterTextSplitter

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                separators=["\n\n", "\n", ". ", " ", ""],
            )
            docs.extend(splitter.split_documents(loaded_docs))
        except Exception as e:  # pragma: no cover - optional dependency
            print(f"Failed to split documents: {e}")
            docs.extend(loaded_docs)

    if not docs:
        print(f"No supported documents found in {source_dir}")
        return False

    try:
        from langchain_chroma import Chroma
        from langchain_huggingface import HuggingFaceEmbeddings
    except ImportError as e:
        print(f"Missing dependencies for ingestion: {e}")
        return False

    model_name = embed_model or "sentence-transformers/all-MiniLM-L6-v2"
    embed_func = HuggingFaceEmbeddings(model_name=model_name)

    os.makedirs(persist_dir, exist_ok=True)
    Chroma.from_documents(docs, embed_func, persist_directory=persist_dir)

    print(f"✅ Ingested {len(docs)} documents into {persist_dir}")
    return True

def list_documents(source_dir: str) -> List[str]:
    """List supported documents in source directory"""
    patterns = ["*.pdf", "*.docx", "*.xlsx", "*.xls"]
    files = []
    
    for pattern in patterns:
        files.extend(glob.glob(os.path.join(source_dir, pattern)))
    
    return sorted(files)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Ingest documents into vector store")
    parser.add_argument("--source", type=str, required=True, 
                       help="Directory containing documents")
    parser.add_argument("--out", type=str, required=True,
                       help="Output directory for vector store") 
    parser.add_argument("--model", type=str, default=None,
                       help="Embedding model name")
    parser.add_argument("--list", action="store_true",
                       help="List documents without ingesting")
    
    args = parser.parse_args()
    
    if args.list:
        files = list_documents(args.source)
        print(f"Found {len(files)} documents:")
        for f in files:
            print(f"  {f}")
    else:
        success = ingest_docs(args.source, args.out, args.model)
        if success:
            print("\n🎯 Next steps:")
            print(f"1. Set VECTOR_STORE_DIR={args.out}")
            print("2. Deploy with vector store available")
            print("3. Test document queries")
        else:
            print("❌ Ingestion failed")
            exit(1)
