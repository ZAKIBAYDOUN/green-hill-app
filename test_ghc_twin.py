# test_ghc_twin.py
"""
Updated smoke tests for the app/ architecture
"""
import os
import sys
sys.path.append('/workspaces/green-hill-app')

from app.models import TwinState, AgentName, Message
from app.ghc_twin import app, intake_node
import re


def test_minimal_invoke_investor():
    state = TwinState(question="What is the ROI for EU-GMP compliance?", source_type="investor")
    result = app.invoke(state)
    assert result["finalize"] is True
    assert result.get("final_answer")


def test_agent_enums_values():
    assert AgentName.STRATEGY.value == "strategy"
    assert AgentName.FINANCE.value == "finance"
    assert AgentName.OPERATIONS.value == "operations"
    assert AgentName.MARKET.value == "market"
    assert AgentName.RISK.value == "risk"
    assert AgentName.COMPLIANCE.value == "compliance"
    assert AgentName.INNOVATION.value == "innovation"
    assert AgentName.GREEN_HILL.value == "green_hill_gpt"


def test_intake_records_user_question():
    state = TwinState(question="Hello")
    out = intake_node(state)
    assert out.history[0].role == "User"
    assert out.history[0].content == "Hello"
    assert out.history[1].role == "System"


def test_market_intel_alias_routes_to_market():
    state = TwinState(question="Market?", target_agent=AgentName.MARKET_INTEL)
    result = app.invoke(state)
    assert result["finalize"] is True
    assert result.get("market_output")


def test_final_summary_has_context_counts():
    state = TwinState(question="ROI?", source_type="public")
    result = app.invoke(state)
    assert re.search(r"🎯 Strategy \(\d+ ctx\)", result["final_answer"])


def test_digital_twin_uses_shared_store(monkeypatch):
    import importlib
    import app.ghc_twin as ghc_twin

    calls = 0

    class DummyStore:
        def __init__(self):
            self.queries = 0

        def is_available(self):
            return True

        def query(self, text, k=5):
            self.queries += 1
            return "ctx"

        def add_agent_outputs(self, state):
            return True

    def fake_get_store(persist_dir):
        nonlocal calls
        calls += 1
        return DummyStore()

    importlib.reload(ghc_twin)
    monkeypatch.setattr(ghc_twin, "get_document_store", fake_get_store)
    graph = ghc_twin.build_graph()
    state = TwinState(question="hi", source_type="public")
    result = graph.invoke(state)
    assert calls == 1
    assert result["context"]["retrieved_docs"] == ["ctx"]


if __name__ == "__main__":
    # Simple runner
    try:
        test_minimal_invoke_investor()
        test_agent_enums_values()
        print("OK")
        sys.exit(0)
    except AssertionError as e:
        print(f"FAIL: {e}")
        sys.exit(1)
