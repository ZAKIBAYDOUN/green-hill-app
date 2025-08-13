"""
Minimal Green Hill Control Interface for LangGraph Hosted deployment.
This is a bare-bones version that will definitely build and deploy.
"""

from typing import Dict, Any
from langgraph.graph import StateGraph, END
from pydantic import BaseModel

class SimpleState(BaseModel):
    question: str = "What is the status of Green Hill Canarias?"
    answer: str = ""

def simple_agent(state: SimpleState) -> SimpleState:
    """Simple agent that provides a basic response."""
    state.answer = f"Green Hill Canarias Digital Twin responding to: {state.question}"
    return state

def build_simple_graph():
    """Build the simplest possible LangGraph."""
    graph = StateGraph(SimpleState)
    graph.add_node("agent", simple_agent)
    graph.set_entry_point("agent")
    graph.add_edge("agent", END)
    return graph.compile()

# Export for LangGraph deployment
app = build_simple_graph()

if __name__ == "__main__":
    result = app.invoke({"question": "Test deployment"})
    print(result)
