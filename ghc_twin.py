# ghc_twin.py
from langgraph.graph import StateGraph, START, END
from models import TwinState, AgentName, Message
from document_store import get_document_store
import os
import requests

# Node helper: record history and update state
def record(state: TwinState, agent: AgentName, content: str, **kwargs) -> TwinState:
    """Record agent activity in state and history"""
    state.history.append(Message(role=agent.value, content=content))
    state.notes.append(f"{agent.value}: OK")
    
    # Update agent output
    for k, v in kwargs.items():
        setattr(state, f"{agent.value.lower()}_output", v)
    
    state.current_agent = agent
    # CEO feedback log of inputs/outputs per agent
    try:
        state.ceo_feedbacks.append({
            "agent": agent.value,
            "content": content,
            "outputs": {k: v for k, v in kwargs.items()}
        })
    except Exception:
        # Never break flow on logging
        pass
    return state

# Digital twin entrypoint: query vector store for context
def digital_twin_node(state: TwinState) -> TwinState:
    """Digital Twin orchestrator - retrieves context and routes to first agent"""
    # Defensive: ensure a question exists
    if not getattr(state, "question", None):
        state.errors.append("Missing 'question' in state")
        state.finalize = True
        state.final_answer = "Error: Missing 'question' in state. Hint: Pass {\"question\": \"...\"} as input payload"
        return state

    try:
        persist_dir = os.getenv("VECTOR_STORE_DIR", "vector_store")
        vectordb = get_document_store(persist_dir)
        
        if vectordb:
            # Query vector store for relevant context
            docs = vectordb.similarity_search(state.question, k=5)
            state.context["retrieved_docs"] = [d.page_content for d in docs]
            state.context["sources"] = [d.metadata.get("source", "unknown") for d in docs]
            print(f"📚 Retrieved {len(docs)} relevant document chunks")
        else:
            # Fallback if no vector store available
            state.context["retrieved_docs"] = ["No vector store available - using baseline knowledge"]
            state.context["sources"] = ["baseline"]
            print("⚠️ No vector store available, using baseline knowledge")
        # Determine first hop based on orchestration mode / source_type
        if state.orchestration_mode == "direct" and state.target_agent:
            state.next_agent = state.target_agent
        else:
            # role-aware default
            role = (state.source_type or "").lower()
            if role in {"master", "shareholder", "investor"}:
                state.next_agent = AgentName.strategy
            elif role in {"supplier", "provider"}:
                state.next_agent = AgentName.operations
            elif role == "public":
                state.next_agent = AgentName.compliance
            else:
                state.next_agent = AgentName.strategy
        
    except Exception as e:
        state.errors.append(f"Digital Twin initialization error: {e}")
        state.context["retrieved_docs"] = ["Error retrieving documents"]
        state.next_agent = AgentName.strategy
    
    return state

# Individual agent nodes
def strategy_node(state: TwinState) -> TwinState:
    """Strategy Agent - strategic planning and long-term vision"""
    context_docs = "\n".join(state.context.get("retrieved_docs", []))
    
    # Placeholder strategic analysis
    output = {
        "strategic_focus": "EU-GMP compliance with ROI optimization",
        "timeline": "9-month implementation plan", 
        "roi_target": ">20%",
        "key_initiatives": [
            "Regulatory compliance alignment",
            "Market positioning in Canary Islands",
            "Strategic partnerships development"
        ],
        "context_used": len(state.context.get("retrieved_docs", [])),
        "analysis": f"Strategic analysis based on query: {state.question}. Context: {context_docs[:200]}..."
    }
    
    state = record(state, AgentName.strategy, "Strategic analysis completed", strategy_output=output)
    state.next_agent = AgentName.finance
    return state

def finance_node(state: TwinState) -> TwinState:
    """Finance Agent - financial modeling and investment analysis"""
    context_docs = "\n".join(state.context.get("retrieved_docs", []))
    
    output = {
        "roi_projection": "24%",
        "capex_estimate": 3_200_000,
        "revenue_model": "Sustainable growth with Atlantic market focus",
        "funding_strategy": "Mixed equity and strategic partnerships",
        "financial_milestones": [
            "T+3: Initial funding secured",
            "T+6: First revenue streams",
            "T+9: Target ROI achieved"
        ],
        "context_used": len(state.context.get("retrieved_docs", [])),
        "analysis": f"Financial modeling for: {state.question}. Context: {context_docs[:200]}..."
    }
    
    state = record(state, AgentName.finance, "Financial modeling completed", finance_output=output)
    state.next_agent = AgentName.operations
    return state

def operations_node(state: TwinState) -> TwinState:
    """Operations Agent - operational planning and execution"""
    context_docs = "\n".join(state.context.get("retrieved_docs", []))
    
    output = {
        "implementation_schedule": "Phased approach: T0 → T+9 months",
        "resource_allocation": "Cross-functional teams with external expertise",
        "operational_framework": "Agile methodology with quarterly reviews",
        "key_deliverables": [
            "Infrastructure setup (T+2)",
            "Process optimization (T+5)", 
            "Full operational capacity (T+9)"
        ],
        "context_used": len(state.context.get("retrieved_docs", [])),
        "analysis": f"Operations planning for: {state.question}. Context: {context_docs[:200]}..."
    }
    
    state = record(state, AgentName.operations, "Operations planning completed", operations_output=output)
    state.next_agent = AgentName.market
    return state

def market_node(state: TwinState) -> TwinState:
    """Market Agent - market intelligence and competitive analysis"""
    context_docs = "\n".join(state.context.get("retrieved_docs", []))
    
    output = {
        "market_opportunity": "Atlantic corridor positioning with EU connectivity",
        "growth_projection": "CAGR 12% in target segments",
        "competitive_landscape": "First-mover advantage in specialized markets",
        "market_entry_strategy": [
            "Local partnerships in Canary Islands",
            "EU market expansion through strategic positioning",
            "Innovation-driven differentiation"
        ],
        "context_used": len(state.context.get("retrieved_docs", [])),
        "analysis": f"Market intelligence for: {state.question}. Context: {context_docs[:200]}..."
    }
    
    state = record(state, AgentName.market, "Market intelligence gathered", market_output=output)
    state.next_agent = AgentName.risk
    return state

def risk_node(state: TwinState) -> TwinState:
    """Risk Agent - risk assessment and mitigation strategies"""
    context_docs = "\n".join(state.context.get("retrieved_docs", []))
    
    output = {
        "risk_assessment": "Medium risk with high mitigation potential",
        "primary_risks": [
            "Regulatory changes",
            "Market volatility", 
            "Implementation delays"
        ],
        "mitigation_strategies": [
            "Proactive compliance monitoring",
            "Diversified market approach",
            "Agile project management"
        ],
        "contingency_plans": "Risk-adjusted timeline with buffer periods",
        "context_used": len(state.context.get("retrieved_docs", [])),
        "analysis": f"Risk analysis for: {state.question}. Context: {context_docs[:200]}..."
    }
    
    state = record(state, AgentName.risk, "Risk analysis completed", risk_output=output)
    state.next_agent = AgentName.compliance
    return state

def compliance_node(state: TwinState) -> TwinState:
    """Compliance Agent - regulatory compliance and legal framework"""
    context_docs = "\n".join(state.context.get("retrieved_docs", []))
    
    output = {
        "regulatory_framework": "EU-GMP compliance with Spanish national requirements",
        "compliance_actions": [
            "SOPs review and update",
            "Internal audit within 60 days",
            "Regulatory submission preparation"
        ],
        "legal_considerations": "Canary Islands special economic zone benefits",
        "timeline": "Compliance certification within 6 months",
        "context_used": len(state.context.get("retrieved_docs", [])),
        "analysis": f"Compliance analysis for: {state.question}. Context: {context_docs[:200]}..."
    }
    
    state = record(state, AgentName.compliance, "Compliance framework outlined", compliance_output=output)
    state.next_agent = AgentName.innovation
    return state

def innovation_node(state: TwinState) -> TwinState:
    """Innovation Agent - technology advancement and R&D"""
    context_docs = "\n".join(state.context.get("retrieved_docs", []))
    
    output = {
        "innovation_roadmap": "Technology-driven sustainable development",
        "key_initiatives": [
            "AI-driven process optimization",
            "Sustainable technology integration", 
            "Digital transformation acceleration"
        ],
        "r_and_d_focus": "Green technology and automation",
        "innovation_partnerships": "Academic and industry collaborations",
        "context_used": len(state.context.get("retrieved_docs", [])),
        "analysis": f"Innovation planning for: {state.question}. Context: {context_docs[:200]}..."
    }
    
    state = record(state, AgentName.innovation, "Innovation roadmap prepared", innovation_output=output)
    
    # Optionally call external Green Hill GPT
    if os.getenv("GREEN_HILL_URL") and os.getenv("GREEN_HILL_KEY"):
        try:
            payload = {"question": state.question}
            headers = {"Authorization": f"Bearer {os.getenv('GREEN_HILL_KEY')}"}
            response = requests.post(os.getenv("GREEN_HILL_URL"), json=payload, headers=headers)
            state.green_hill_response = response.json()
            print("🤖 Green Hill GPT consultation completed")
        except Exception as e:
            state.errors.append(f"Green Hill GPT error: {e}")
            print(f"⚠️ Green Hill GPT unavailable: {e}")
    
    # Finalize the comprehensive analysis
    state.finalize = True
    
    # Compose final answer from all agent outputs
    strat = state.strategy_output or {}
    fin = state.finance_output or {}
    ops = state.operations_output or {}
    mkt = state.market_output or {}
    rsk = state.risk_output or {}
    cmp_ = state.compliance_output or {}
    inn = state.innovation_output or {}

    parts = [
        f"🎯 **Strategy**: {strat.get('strategic_focus', 'N/A')}",
        f"💰 **Finance**: ROI {fin.get('roi_projection', 'N/A')}, CAPEX €{fin.get('capex_estimate', 'N/A') if isinstance(fin.get('capex_estimate', 'N/A'), int) else fin.get('capex_estimate', 'N/A')}",
        f"⚙️ **Operations**: {ops.get('implementation_schedule', 'N/A')}",
        f"📊 **Market**: {mkt.get('growth_projection', 'N/A')} growth in {mkt.get('market_opportunity', 'target markets')}",
        f"⚠️ **Risk**: {rsk.get('risk_assessment', 'N/A')} with mitigation strategies",
        f"📋 **Compliance**: {cmp_.get('timeline', 'N/A')} for {cmp_.get('regulatory_framework', 'framework')}",
        f"💡 **Innovation**: {inn.get('r_and_d_focus', 'N/A')} with {len(inn.get('key_initiatives', []))} key initiatives"
    ]
    
    if state.green_hill_response:
        parts.append(f"🤖 **Green Hill GPT**: External consultation completed")
    
    state.final_answer = f"""# Green Hill Canarias Digital Twin Analysis

**Query**: {state.question}

## Executive Summary
Comprehensive multi-agent analysis across all business domains:

{chr(10).join(parts)}

## Integrated Recommendations
The Digital Twin analysis reveals a strategic opportunity with strong fundamentals across all evaluated dimensions. Success factors include regulatory alignment, financial sustainability, operational excellence, market positioning, risk management, compliance adherence, and innovation leadership.

**Sources**: {len(state.context.get('retrieved_docs', []))} document chunks analyzed
**Agents**: 7 specialized agents consulted
**Analysis**: Complete multi-domain assessment

---
*Generated by Green Hill Canarias Digital Twin System*"""
    
    return state

# Optional Green Hill GPT node (can be routed to directly or after agents)
def green_hill_node(state: TwinState) -> TwinState:
    """Green Hill GPT integration node (placeholder unless GREEN_HILL_URL/KEY set)"""
    state = record(state, AgentName.green_hill, "Green Hill GPT consultation starting")
    if os.getenv("GREEN_HILL_URL") and os.getenv("GREEN_HILL_KEY"):
        try:
            payload = {"question": state.question}
            headers = {"Authorization": f"Bearer {os.getenv('GREEN_HILL_KEY')}"}
            response = requests.post(os.getenv("GREEN_HILL_URL"), json=payload, headers=headers, timeout=30)
            state.green_hill_response = response.json()
            state.notes.append("Green Hill GPT responded")
        except Exception as e:
            state.errors.append(f"Green Hill GPT error: {e}")
    else:
        state.notes.append("GREEN_HILL_URL/KEY not set; skipped external call")

    # If previous agents have filled outputs, compose a final answer; else provide minimal reply
    if not state.finalize:
        parts = [
            f"🎯 **Strategy**: {state.strategy_output.get('strategic_focus', 'N/A') if state.strategy_output else 'N/A'}",
            f"💰 **Finance**: {state.finance_output.get('roi_projection', 'N/A') if state.finance_output else 'N/A'}",
            f"⚙️ **Operations**: {state.operations_output.get('implementation_schedule', 'N/A') if state.operations_output else 'N/A'}",
        ]
        state.final_answer = (state.final_answer or "") + ("\n\n" if state.final_answer else "") + "\n".join(parts)
        if state.green_hill_response:
            state.final_answer += "\n\n🤖 Green Hill GPT: consultation completed."
        state.finalize = True
    return state

# Start router: choose CEO orchestrator vs direct agent
def start_router(state: TwinState):
    if state.orchestration_mode == "direct" and state.target_agent:
        return state.target_agent.name.lower()
    return "digital_twin"

# Router defines next node or end
def router(state: TwinState):
    """Route to next agent or end processing"""
    if state.finalize:
        return END
    
    # Agent routing map
    return {
        AgentName.strategy: "strategy",
        AgentName.finance: "finance", 
        AgentName.operations: "operations",
        AgentName.market: "market",
        AgentName.risk: "risk",
        AgentName.compliance: "compliance",
        AgentName.innovation: "innovation",
        AgentName.green_hill: "green_hill",
    }.get(state.next_agent, END)

# Build the graph
def build_graph():
    """Build the Digital Twin LangGraph"""
    graph = StateGraph(TwinState)
    
    # Add nodes
    graph.add_node("digital_twin", digital_twin_node)
    graph.add_node("strategy", strategy_node)
    graph.add_node("finance", finance_node)
    graph.add_node("operations", operations_node)
    graph.add_node("market", market_node)
    graph.add_node("risk", risk_node)
    graph.add_node("compliance", compliance_node)
    graph.add_node("innovation", innovation_node)
    # GreenHillGPT integration node (optional route)
    graph.add_node("green_hill", green_hill_node)

    # Define edges
    # Conditional START routing: CEO (digital_twin) or direct agent
    # Unified routing map for all conditional edges
    route_map = {
        "strategy": "strategy",
        "finance": "finance",
        "operations": "operations",
        "market": "market",
        "risk": "risk",
        "compliance": "compliance",
        "innovation": "innovation",
    "green_hill": "green_hill",
        "digital_twin": "digital_twin",
        END: END,
    }
    graph.add_conditional_edges(START, start_router, route_map)

    # Route conditionally from orchestrator and between agents
    graph.add_conditional_edges("digital_twin", router, route_map)
    graph.add_conditional_edges("strategy", router, route_map)
    graph.add_conditional_edges("finance", router, route_map)
    graph.add_conditional_edges("operations", router, route_map)
    graph.add_conditional_edges("market", router, route_map)
    graph.add_conditional_edges("risk", router, route_map)
    graph.add_conditional_edges("compliance", router, route_map)
    graph.add_conditional_edges("innovation", router, route_map)

    return graph.compile()

# Expose app for LangGraph deployment
app = build_graph()

if __name__ == "__main__":
    # Test the digital twin locally
    test_state = TwinState(question="What is the strategic plan for sustainable growth in the Canary Islands?")
    result = app.invoke(test_state)
    print(result.final_answer)
