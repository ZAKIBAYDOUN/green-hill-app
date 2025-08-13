#!/usr/bin/env python3
"""
Green Hill Canarias - Simple LangGraph Application
"""

import os
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage

# Simple state definition
class State(Dict[str, Any]):
    pass

# Get LLM
def get_llm():
    model = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o")
    return ChatOpenAI(model=model, temperature=0.1)

llm = get_llm()

def agent_node(state: State) -> State:
    """Simple agent that responds to queries"""
    messages = state.get("messages", [])
    if not messages:
        return {"messages": [AIMessage(content="Hello! I'm the Green Hill Canarias assistant.")]}
    
    # Get the last user message
    user_message = messages[-1]
    
    # Create a simple response
    prompt = f"""You are an AI assistant for Green Hill Canarias, a strategic business development project.
    
User query: {user_message.content}

Please provide a helpful response about Green Hill Canarias business strategy, operations, or development plans."""

    response = llm.invoke([HumanMessage(content=prompt)])
    
    return {
        "messages": state.get("messages", []) + [response]
    }

# Build simple graph
def build_graph():
    workflow = StateGraph(State)
    workflow.add_node("agent", agent_node)
    workflow.set_entry_point("agent")
    workflow.add_edge("agent", END)
    return workflow.compile()

# Create the app
app = build_graph()

# For testing
if __name__ == "__main__":
    test_state = {
        "messages": [HumanMessage(content="What is Green Hill Canarias?")]
    }
    result = app.invoke(test_state)
    print("Response:", result["messages"][-1].content)
