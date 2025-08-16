from __future__ import annotations

"""Agent-facing ingestion wrapper.

This module exposes a simple function that allows agents or
front-end helpers to ingest arbitrary files into the shared vector
store. Metadata supplied via ``extra_meta`` can be attached downstream
if the underlying store supports it.
"""

import os
from typing import Any, Dict, Iterable

from app.document_store import ingest_canonical_docs


def ingest_files_with_meta(
    file_paths: Iterable[str],
    extra_meta: Dict[str, Any] | None = None,
    persist_dir: str | None = None,
):
    """Ingest the provided files into the vector store.

    Parameters
    ----------
    file_paths:
        Iterable of file system paths to ingest.
    extra_meta:
        Optional metadata to be associated with the documents. Currently
        unused but kept for API compatibility.
    persist_dir:
        Optional directory for the vector store. If not provided, the
        function will look for ``VECTORSTORE_DIR`` or ``VECTOR_STORE_DIR``
        environment variables and fall back to ``"vector_store"``.
    """
    target_dir = (
        persist_dir
        or os.getenv("VECTORSTORE_DIR")
        or os.getenv("VECTOR_STORE_DIR")
        or "vector_store"
    )
    db = ingest_canonical_docs(list(file_paths), persist_dir=target_dir)
    # Attach ``extra_meta`` to each document downstream if the store supports it
    return db
