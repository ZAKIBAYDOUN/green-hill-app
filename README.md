# green-hill-app

This repository hosts the Green Hill Canarias orchestrator.  Some
functionality depends on internal modules that are not included in the open
release.

## Optional dependencies

The orchestrator can leverage two modules:

* `ghc_complete` – provides the full LangGraph implementation for multi-agent
  reasoning.
* `ghc_document_system` – exposes the canonical document store.

These modules are proprietary and are not bundled in this repository.  If you
have access to them, install them into your environment (e.g. `pip install
ghc_complete ghc_document_system`) or place the modules on the Python path.

When they are missing the application runs in a degraded mode and returns
helpful error messages instead of crashing.  See `main.py` for the exact
fallback behaviour.

