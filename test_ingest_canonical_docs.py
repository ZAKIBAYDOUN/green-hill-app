import os
from pathlib import Path

from app.document_store import ingest_canonical_docs


class DummyEmbeddings:
    def embed_documents(self, texts):
        return [[0.0] * 3 for _ in texts]

    def embed_query(self, text):
        return [0.0] * 3


def test_recursive_ingest_with_domain_metadata(tmp_path, monkeypatch):
    root = tmp_path / "docs"
    (root / "alpha").mkdir(parents=True)
    (root / "alpha" / "a.txt").write_text("hello", encoding="utf-8")
    (root / "beta").mkdir()
    (root / "beta" / "b.json").write_text("{\"k\":1}", encoding="utf-8")

    store = tmp_path / "vs"
    monkeypatch.setenv("VECTORSTORE_DIR", str(store))
    monkeypatch.setattr(
        "app.document_store._get_embeddings", lambda: DummyEmbeddings()
    )

    db = ingest_canonical_docs([str(root)])
    assert db is not None
    # verify files persisted in env var directory
    assert store.exists()
    data = db.get(include=["metadatas"])
    domains = {m.get("domain") for m in data["metadatas"]}
    subdomains = {m.get("subdomain") for m in data["metadatas"]}
    assert domains == {"alpha", "beta"}
    assert subdomains == {"a", "b"}


def test_nested_folder_uses_top_level_domain(tmp_path, monkeypatch):
    """Files in nested subfolders should inherit the top-level domain."""
    root = tmp_path / "docs"
    nested_dir = root / "gamma" / "sub" / "deep"
    nested_dir.mkdir(parents=True)
    (nested_dir / "03_deep.txt").write_text("content", encoding="utf-8")

    store = tmp_path / "vs"
    monkeypatch.setenv("VECTORSTORE_DIR", str(store))
    monkeypatch.setattr(
        "app.document_store._get_embeddings", lambda: DummyEmbeddings()
    )

    db = ingest_canonical_docs([str(root)])
    assert db is not None
    metas = db.get(include=["metadatas"])["metadatas"]
    assert any(m.get("domain") == "gamma" and m.get("subdomain") == "deep" for m in metas)


def test_ingest_md_and_jsonl(tmp_path, monkeypatch):
    root = tmp_path / "docs"
    (root / "alpha").mkdir(parents=True)
    (root / "alpha" / "01_note.md").write_text("# heading", encoding="utf-8")
    (root / "beta").mkdir()
    jsonl_path = root / "beta" / "02_log.jsonl"
    jsonl_path.write_text('{"k":1}\n{"k":2}', encoding="utf-8")

    store = tmp_path / "vs"
    monkeypatch.setenv("VECTORSTORE_DIR", str(store))
    monkeypatch.setattr("app.document_store._get_embeddings", lambda: DummyEmbeddings())

    db = ingest_canonical_docs([str(root)])
    assert db is not None
    metas = db.get(include=["metadatas"])["metadatas"]
    domains = {m.get("domain") for m in metas}
    subdomains = {m.get("subdomain") for m in metas}
    assert "alpha" in domains and "beta" in domains
    assert "note" in subdomains and "log" in subdomains
