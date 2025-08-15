"""Compatibility layer for document store utilities.

The canonical implementation lives in :mod:`app.document_store`. This module
re-exports those helpers so existing imports from the project root continue to
work while avoiding duplicate implementations.
"""
from app.document_store import (
    DocumentStore,
    ingest_canonical_docs,
    get_document_store,
    bootstrap_store,
)

__all__ = [
    "DocumentStore",
    "ingest_canonical_docs",
    "get_document_store",
    "bootstrap_store",
]
