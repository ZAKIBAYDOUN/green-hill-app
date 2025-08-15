"""Compatibility layer exposing models from :mod:`app.models`.

The project historically imported Pydantic models from the repository root.
To keep those imports working while consolidating implementation in the
``app`` package, this module simply re-exports the canonical definitions.
"""
from app.models import AgentName, Message, TwinState

# Backwards compatibility alias
State = TwinState

__all__ = ["AgentName", "Message", "TwinState", "State"]
