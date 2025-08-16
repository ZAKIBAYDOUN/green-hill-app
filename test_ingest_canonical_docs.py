import sys
from pathlib import Path

# Ensure module import path
sys.path.append(str(Path(__file__).resolve().parent))

import document_store


def test_ingest_canonical_docs_json(tmp_path, monkeypatch):
    sample_path = Path(__file__).with_name("sample_docs.json")

    captured = {}

    class FakeChroma:
        @classmethod
        def from_documents(cls, docs, embedding, persist_directory):
            captured["docs"] = docs
            return "vectordb"

    # Patch embeddings and Chroma
    monkeypatch.setattr(document_store, "_get_embeddings", lambda: "embed")
    import langchain_chroma
    monkeypatch.setattr(langchain_chroma, "Chroma", FakeChroma)

    # Run ingestion
    result = document_store.ingest_canonical_docs([str(sample_path)], persist_dir=str(tmp_path))
    assert result == "vectordb"

    docs = captured["docs"]
    assert len(docs) == 2

    expected = [
        ("finance", "tax", "Tax law analysis"),
        ("operations", "logistics", "Logistics best practices"),
    ]

    for doc, (domain, subdomain, content) in zip(docs, expected):
        assert doc.metadata["type"] == "json"
        assert doc.metadata["domain"] == domain
        assert doc.metadata["subdomain"] == subdomain
        assert doc.page_content == content
        assert doc.metadata["source"].endswith("sample_docs.json")
