# app/ghc_twin.py
import os
from typing import List
from langgraph.graph import StateGraph, START, END
from app.models import TwinState, AgentName
from app.document_store import get_document_store
from app.agents import (
    strategy_node,
    finance_node,
    operations_node,
    market_intel_node as market_node,
    risk_node,
    compliance_node,
    innovation_node,
    green_hill_node,
    finalize_node,
)


def classify_request(state: TwinState) -> List[AgentName]:
    # Simple role-based classification; extend with keywords as needed
    st = (state.source_type or "public").lower()
    if st == "master":
        return [
            AgentName.STRATEGY, AgentName.FINANCE, AgentName.OPERATIONS,
            AgentName.MARKET, AgentName.RISK, AgentName.COMPLIANCE, AgentName.INNOVATION,
            AgentName.GREEN_HILL,
        ]
    if st in {"shareholder", "investor"}:
        return [AgentName.STRATEGY, AgentName.FINANCE, AgentName.MARKET, AgentName.RISK, AgentName.GREEN_HILL]
    if st in {"supplier", "provider"}:
        return [AgentName.OPERATIONS, AgentName.COMPLIANCE]
    if st == "public":
        return [AgentName.MARKET, AgentName.STRATEGY]
    if st == "ocs_feed":
        return [AgentName.OPERATIONS, AgentName.COMPLIANCE]
    if st == "web_source":
        return [AgentName.MARKET, AgentName.RISK]
    return []


def digital_twin(state: TwinState) -> TwinState:
    # Validate input
    if not state.question:
        state.finalize = True
        state.final_answer = (
            'Error: Missing "question". Send {"question": "..."} along with source_type.'
        )
        return state

    # Load vector store and attach context
    persist_dir = os.getenv("VECTOR_STORE_DIR", "vector_store")
    store = get_document_store(persist_dir)
    if store and store.is_available():
        ctx = store.query(state.question, k=5)
        state.context["retrieved_docs"] = ctx.split("\n\n") if ctx else []
    else:
        state.context["retrieved_docs"] = ["No vector store available"]

    # Classify
    targets = classify_request(state)
    state.target_agents = targets
    if not targets:
        state.finalize = True
        state.final_answer = (
            "No suitable agents selected. Provide a clearer source_type or question."
        )
        return state

    # First hop
    state.next_agent = targets[0]
    return state


def router(state: TwinState):
    if state.finalize:
        return END
    m = {
        AgentName.STRATEGY: "strategy",
        AgentName.FINANCE: "finance",
        AgentName.OPERATIONS: "operations",
        AgentName.MARKET: "market",
        AgentName.RISK: "risk",
        AgentName.COMPLIANCE: "compliance",
        AgentName.INNOVATION: "innovation",
    AgentName.GREEN_HILL: "green_hill",
    }
    # If no explicit next agent but not finalized, go to finalize node
    if state.next_agent is None and not state.finalize:
        return "finalize"
    return m.get(state.next_agent, END)


def build_graph():
    g = StateGraph(TwinState)
    # Initialize a single document store instance
    persist_dir = os.getenv("VECTOR_STORE_DIR", "vector_store")
    store = get_document_store(persist_dir)
    # Nodes
    g.add_node("digital_twin", digital_twin)
    g.add_node("strategy", lambda s: strategy_node(s, store))
    g.add_node("finance", lambda s: finance_node(s, store))
    g.add_node("operations", lambda s: operations_node(s, store))
    g.add_node("market", lambda s: market_node(s, store))
    g.add_node("risk", lambda s: risk_node(s, store))
    g.add_node("compliance", lambda s: compliance_node(s, store))
    g.add_node("innovation", lambda s: innovation_node(s, store))
    g.add_node("green_hill", lambda s: green_hill_node(s, store))
    g.add_node("finalize", lambda s: finalize_node(s, store))

    # Edges
    g.add_edge(START, "digital_twin")
    route_map = {
        "strategy": "strategy",
        "finance": "finance",
        "operations": "operations",
        "market": "market",
        "risk": "risk",
        "compliance": "compliance",
        "innovation": "innovation",
    "green_hill": "green_hill",
        "finalize": "finalize",
        END: END,
    }
    g.add_conditional_edges("digital_twin", router, route_map)
    g.add_conditional_edges("strategy", router, route_map)
    g.add_conditional_edges("finance", router, route_map)
    g.add_conditional_edges("operations", router, route_map)
    g.add_conditional_edges("market", router, route_map)
    g.add_conditional_edges("risk", router, route_map)
    g.add_conditional_edges("compliance", router, route_map)
    g.add_conditional_edges("innovation", router, route_map)
    g.add_conditional_edges("green_hill", router, route_map)

    return g.compile()
app = build_graph()
