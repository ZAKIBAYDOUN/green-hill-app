import json
import sys
import types
from pathlib import Path

import pytest
from langchain.docstore.document import Document

from app import document_store


class DummyTextLoader:
    def __init__(self, path: str):
        self.path = path

    def load(self):
        with open(self.path, "r", encoding="utf-8") as f:
            text = f.read()
        return [Document(page_content=text, metadata={"source": self.path})]


def setup_stubs(monkeypatch):
    # Stub out langchain_community document loaders
    loaders = types.SimpleNamespace(
        PyPDFLoader=DummyTextLoader,
        Docx2txtLoader=DummyTextLoader,
        UnstructuredExcelLoader=DummyTextLoader,
        TextLoader=DummyTextLoader,
    )
    monkeypatch.setitem(sys.modules, "langchain_community.document_loaders", loaders)

    # Stub out Chroma to capture documents passed in
    class DummyChroma:
        def __init__(self, docs):
            self.docs = docs

        @classmethod
        def from_documents(cls, docs, embeddings, persist_directory):
            return cls(docs)

    monkeypatch.setitem(sys.modules, "langchain_chroma", types.SimpleNamespace(Chroma=DummyChroma))
    monkeypatch.setattr(document_store, "_get_embeddings", lambda: None)
    return DummyChroma


def test_ingests_md_and_jsonl(monkeypatch, tmp_path):
    DummyChroma = setup_stubs(monkeypatch)

    md_path = tmp_path / "sample.md"
    md_path.write_text("# Title\n\ncontent", encoding="utf-8")

    jsonl_path = tmp_path / "sample.jsonl"
    lines = [
        {"text": "line one", "domain": "alpha", "subdomain": "a"},
        {"text": "line two", "domain": "beta", "subdomain": "b"},
    ]
    jsonl_path.write_text("\n".join(json.dumps(l) for l in lines), encoding="utf-8")

    db = document_store.ingest_canonical_docs([str(md_path), str(jsonl_path)], persist_dir=str(tmp_path / "store"))

    assert isinstance(db, DummyChroma)
    assert len(db.docs) == 3

    sources = [d.metadata.get("source") for d in db.docs]
    assert str(md_path) in sources
    md_docs = [d for d in db.docs if d.metadata.get("source") == str(md_path)]
    assert md_docs[0].metadata["type"] == "md"

    jsonl_docs = [d for d in db.docs if d.metadata.get("source") == str(jsonl_path)]
    assert len(jsonl_docs) == 2
    assert jsonl_docs[0].metadata["domain"] == "alpha"
    assert jsonl_docs[0].metadata["subdomain"] == "a"
    assert jsonl_docs[0].metadata["type"] == "jsonl"
    assert jsonl_docs[1].metadata["domain"] == "beta"
    assert jsonl_docs[1].metadata["subdomain"] == "b"
    assert jsonl_docs[1].metadata["type"] == "jsonl"
