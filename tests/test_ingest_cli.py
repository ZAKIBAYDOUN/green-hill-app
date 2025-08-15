import sys
import types
from pathlib import Path

import pytest

# Ensure repository root on path for importing ``app``
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ingest import ingest_docs


class DummyChroma:
    def __init__(self, docs):
        self.docs = docs

    @classmethod
    def from_documents(cls, docs, embeddings, persist_directory):
        cls.last_docs = docs
        cls.last_persist = persist_directory
        return cls(docs)


class DummyEmbeddings:
    def __init__(self, model_name=None):
        self.model_name = model_name


@pytest.fixture(autouse=True)
def stub_langchain(monkeypatch):
    # Stub the langchain_chroma and langchain_huggingface modules
    monkeypatch.setitem(sys.modules, "langchain_chroma", types.SimpleNamespace(Chroma=DummyChroma))
    monkeypatch.setitem(
        sys.modules,
        "langchain_huggingface",
        types.SimpleNamespace(HuggingFaceEmbeddings=DummyEmbeddings),
    )
    yield
    # cleanup
    DummyChroma.last_docs = None
    DummyChroma.last_persist = None


def test_ingest_md_and_jsonl_line_metadata_and_logging(tmp_path, capsys):
    md = tmp_path / "a.md"
    md.write_text("line one\nline two\n")

    jl = tmp_path / "b.jsonl"
    jl.write_text(
        '{"text": "hello", "metadata": {"idx": 1}}\n'
        'this is not json\n'
        '{"text": "world"}\n'
    )

    persist = tmp_path / "persist"
    ok = ingest_docs(str(tmp_path), str(persist))
    assert ok is True

    docs = DummyChroma.last_docs
    assert [d.page_content for d in docs] == ["line one", "line two", "hello", "world"]

    # Markdown metadata
    md_docs = [d for d in docs if d.metadata["source"] == str(md)]
    assert md_docs[0].metadata["line"] == 1
    assert md_docs[1].metadata["line"] == 2

    # JSONL metadata and custom fields
    jl_docs = [d for d in docs if d.metadata["source"] == str(jl)]
    assert jl_docs[0].metadata["line"] == 1
    assert jl_docs[0].metadata["idx"] == 1
    assert jl_docs[1].metadata["line"] == 3

    out = capsys.readouterr().out
    assert "Malformed line 2" in out
