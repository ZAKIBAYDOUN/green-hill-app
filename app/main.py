# app/main.py
from langgraph.graph import StateGraph, END
from .models import TwinState, AgentName
from .agents import (
    strategy_node, operations_node, finance_node, market_intel_node,
    risk_node, compliance_node, innovation_node, finalize_node
)
from .document_store import DocumentStore
from typing import Dict, Callable, Any
import os

def create_agent_wrapper(agent_func: Callable, doc_store: DocumentStore):
    """Wrap agent functions to inject document store"""
    def wrapper(state: TwinState) -> TwinState:
        return agent_func(state, doc_store)
    return wrapper

def router_logic(state: TwinState) -> str:
    """Route to next agent or finalize"""
    if state.finalize:
        return END
    
    if state.next_agent is None:
        return "finalize"
    
    return state.next_agent.value

def create_app() -> StateGraph:
    """Create the Green Hill Digital Twin LangGraph application"""
    
    # Initialize document store
    doc_store = DocumentStore()
    
    # Create the state graph
    workflow = StateGraph(TwinState)
    
    # Add all agent nodes with document store injection
    workflow.add_node("strategy", create_agent_wrapper(strategy_node, doc_store))
    workflow.add_node("operations", create_agent_wrapper(operations_node, doc_store))
    workflow.add_node("finance", create_agent_wrapper(finance_node, doc_store))
    workflow.add_node("market_intel", create_agent_wrapper(market_intel_node, doc_store))
    workflow.add_node("risk", create_agent_wrapper(risk_node, doc_store))
    workflow.add_node("compliance", create_agent_wrapper(compliance_node, doc_store))
    workflow.add_node("innovation", create_agent_wrapper(innovation_node, doc_store))
    workflow.add_node("finalize", create_agent_wrapper(finalize_node, doc_store))
    
    # Set entry point
    workflow.set_entry_point("strategy")
    
    # Add edges with routing logic
    workflow.add_conditional_edges(
        "strategy",
        router_logic,
        {
            "operations": "operations",
            "finalize": "finalize",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "operations", 
        router_logic,
        {
            "finance": "finance",
            "finalize": "finalize",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "finance",
        router_logic,
        {
            "market_intel": "market_intel", 
            "finalize": "finalize",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "market_intel",
        router_logic,
        {
            "risk": "risk",
            "finalize": "finalize", 
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "risk",
        router_logic,
        {
            "compliance": "compliance",
            "finalize": "finalize",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "compliance",
        router_logic,
        {
            "innovation": "innovation",
            "finalize": "finalize",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "innovation", 
        router_logic,
        {
            "finalize": "finalize",
            END: END
        }
    )
    
    workflow.add_edge("finalize", END)
    
    return workflow.compile()

# Create the main application
app = create_app()

def simple_mode_handler(question: str) -> Dict[str, Any]:
    """Handle simple mode queries with basic response"""
    return {
        "question": question,
        "answer": f"""# Green Hill Canarias - Strategic Response

**Question:** {question}

**Analysis:** This query involves strategic business development opportunities in the Canary Islands. Green Hill Canarias focuses on sustainable growth, innovation, and leveraging the unique advantages of the Atlantic region.

**Key Considerations:**
- Strategic positioning in the Atlantic business corridor
- Sustainable development and environmental responsibility  
- Innovation and technology integration
- Local partnerships and community engagement
- Regulatory compliance and business optimization

**Recommendation:** For detailed multi-domain analysis including strategy, operations, finance, market intelligence, risk assessment, compliance, and innovation perspectives, please enable multi-agent mode.

---
*Response from Green Hill Canarias Simple Mode*"""
    }

def run_query(question: str) -> Dict[str, Any]:
    """Main entry point for processing queries"""
    
    deployment_mode = os.getenv("DEPLOYMENT_MODE", "simple")
    
    if deployment_mode == "simple":
        return simple_mode_handler(question)
    
    elif deployment_mode == "multi_agent":
        # Run the full multi-agent workflow
        initial_state = TwinState(question=question)
        result = app.invoke(initial_state)
        
        return {
            "question": question,
            "answer": result["final_answer"],
            "agent_outputs": {
                "strategy": result.get("strategy_output"),
                "operations": result.get("operations_output"), 
                "finance": result.get("finance_output"),
                "market_intel": result.get("market_output"),
                "risk": result.get("risk_output"),
                "compliance": result.get("compliance_output"),
                "innovation": result.get("innovation_output")
            },
            "conversation_history": [msg.dict() for msg in result["history"]]
        }
    
    else:
        raise ValueError(f"Unknown deployment mode: {deployment_mode}")

# Export for LangGraph Cloud
__all__ = ["app", "run_query"]
