"""Compatibility shim for the Green Hill Canarias digital twin graph.

The implementation resides in :mod:`app.ghc_twin`. Re-export the public API so
legacy imports from the repository root remain functional.
"""
from app.ghc_twin import *  # noqa: F401,F403
