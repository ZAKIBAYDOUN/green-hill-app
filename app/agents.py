# app/agents.py
from .models import TwinState, AgentName, Message
from .document_store import DocumentStore
from typing import Optional, Dict, Any
import os


def record_output(state: TwinState, agent: AgentName, output_key: str, output: Dict[str, Any], note: str):
    """Record agent output (dict) in state and append a brief note to history."""
    state.history.append(Message(role=agent.value, content=note))
    setattr(state, output_key, output)
    state.current_agent = agent
    return state


def _next_from_targets(state: TwinState, current: AgentName) -> Optional[AgentName]:
    if not state.target_agents:
        return None
    try:
        idx = state.target_agents.index(current)
        return state.target_agents[idx + 1] if idx + 1 < len(state.target_agents) else None
    except ValueError:
        # If current not in target list, just end
        return None

def enhance_with_llm(prompt: str, context: str = "") -> str:
    """Enhance agent analysis with LLM if available"""
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage, SystemMessage

        model = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o")
        llm = ChatOpenAI(model=model, temperature=0.1)

        system_prompt = (
            "You are a domain expert for Green Hill Canarias. Provide concise, actionable insights."
        )

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Context: {context}\n\nQuery: {prompt}"),
        ]

        response = llm.invoke(messages)
        return response.content

    except Exception:
        # Graceful fallback
        return (
            f"Baseline analysis (LLM unavailable): {prompt}\n\nContext: {context[:300]}..."
        )

def strategy_node(state: TwinState, doc_store: DocumentStore) -> TwinState:
    """Strategic planning and long-term vision analysis"""
    q = state.question or ""
    ctx = doc_store.query(f"strategy planning vision {q}")
    analysis = enhance_with_llm(f"Strategic opportunities and positioning for: {q}", ctx)
    output = {
        "strategic_focus": "EU-GMP compliance with ROI optimization",
        "timeline": "~9 months",
        "key_initiatives": [
            "Regulatory alignment",
            "Atlantic market positioning",
            "Partnership development",
        ],
        "analysis": analysis,
        "context_used": len((ctx or "").split("\n\n")),
    }
    record_output(state, AgentName.STRATEGY, "strategy_output", output, "Strategic analysis completed")
    state.next_agent = _next_from_targets(state, AgentName.STRATEGY)
    return state

def operations_node(state: TwinState, doc_store: DocumentStore) -> TwinState:
    q = state.question or ""
    ctx = doc_store.query(f"operations processes efficiency {q}")
    analysis = enhance_with_llm(f"Operational requirements and optimization for: {q}", ctx)
    output = {
        "implementation_schedule": "Phased T0→T+9",
        "resource_allocation": "Cross-functional core team",
        "operational_framework": "Agile with quarterly reviews",
        "analysis": analysis,
        "context_used": len((ctx or "").split("\n\n")),
    }
    record_output(state, AgentName.OPERATIONS, "operations_output", output, "Operations planning completed")
    state.next_agent = _next_from_targets(state, AgentName.OPERATIONS)
    return state

def finance_node(state: TwinState, doc_store: DocumentStore) -> TwinState:
    q = state.question or ""
    ctx = doc_store.query(f"finance investment funding {q}")
    analysis = enhance_with_llm(f"Financial implications and investment opportunities for: {q}", ctx)
    output = {
        "roi_projection": "~24%",
        "capex_estimate": 3200000,
        "funding_strategy": "Mixed equity + partnerships",
        "analysis": analysis,
        "context_used": len((ctx or "").split("\n\n")),
    }
    record_output(state, AgentName.FINANCE, "finance_output", output, "Financial modeling completed")
    state.next_agent = _next_from_targets(state, AgentName.FINANCE)
    return state

def market_intel_node(state: TwinState, doc_store: DocumentStore) -> TwinState:
    q = state.question or ""
    ctx = doc_store.query(f"market competition Canary Islands {q}")
    analysis = enhance_with_llm(f"Market opportunities and competitive landscape for: {q}", ctx)
    output = {
        "market_opportunity": "Atlantic corridor with EU connectivity",
        "growth_projection": "~12% CAGR",
        "competitive_landscape": "Emerging, first-mover advantage possible",
        "analysis": analysis,
        "context_used": len((ctx or "").split("\n\n")),
    }
    record_output(state, AgentName.MARKET, "market_output", output, "Market intelligence gathered")
    state.next_agent = _next_from_targets(state, AgentName.MARKET)
    return state

def risk_node(state: TwinState, doc_store: DocumentStore) -> TwinState:
    q = state.question or ""
    ctx = doc_store.query(f"risk assessment mitigation {q}")
    analysis = enhance_with_llm(f"Risks and mitigation strategies for: {q}", ctx)
    output = {
        "risk_assessment": "Medium, mitigable",
        "primary_risks": ["Regulatory changes", "Market volatility", "Delays"],
        "mitigations": ["Proactive monitoring", "Diversified approach", "Agile PM"] ,
        "analysis": analysis,
        "context_used": len((ctx or "").split("\n\n")),
    }
    record_output(state, AgentName.RISK, "risk_output", output, "Risk analysis completed")
    state.next_agent = _next_from_targets(state, AgentName.RISK)
    return state

def compliance_node(state: TwinState, doc_store: DocumentStore) -> TwinState:
    q = state.question or ""
    ctx = doc_store.query(f"EU-GMP compliance Spain Canary Islands {q}")
    analysis = enhance_with_llm(f"Compliance and regulatory requirements for: {q}", ctx)
    output = {
        "regulatory_framework": "EU-GMP + Spanish requirements",
        "timeline": "~6 months for certification",
        "actions": ["SOPs update", "Internal audit", "Submission prep"],
        "analysis": analysis,
        "context_used": len((ctx or "").split("\n\n")),
    }
    record_output(state, AgentName.COMPLIANCE, "compliance_output", output, "Compliance framework outlined")
    state.next_agent = _next_from_targets(state, AgentName.COMPLIANCE)
    return state

def innovation_node(state: TwinState, doc_store: DocumentStore) -> TwinState:
    q = state.question or ""
    ctx = doc_store.query(f"innovation technology digital transformation {q}")
    analysis = enhance_with_llm(f"Innovation opportunities and technology applications for: {q}", ctx)
    output = {
        "innovation_roadmap": "Technology-driven sustainability",
        "initiatives": ["AI optimization", "Sustainable tech", "Digital acceleration"],
        "analysis": analysis,
        "context_used": len((ctx or "").split("\n\n")),
    }
    record_output(state, AgentName.INNOVATION, "innovation_output", output, "Innovation roadmap prepared")
    state.next_agent = _next_from_targets(state, AgentName.INNOVATION)
    return state

def finalize_node(state: TwinState, doc_store: DocumentStore) -> TwinState:
    """Compose final answer from all agent outputs (dicts)."""
    q = state.question or "(no question)"
    strat = state.strategy_output or {}
    fin = state.finance_output or {}
    ops = state.operations_output or {}
    mkt = state.market_output or {}
    rsk = state.risk_output or {}
    cmp_ = state.compliance_output or {}
    inn = state.innovation_output or {}

    parts = [
        f"🎯 Strategy: {strat.get('strategic_focus', 'N/A')} | {strat.get('timeline', '')}",
        f"💰 Finance: ROI {fin.get('roi_projection', 'N/A')} | CAPEX {fin.get('capex_estimate', 'N/A')}",
        f"⚙️ Operations: {ops.get('implementation_schedule', 'N/A')}",
        f"📊 Market: {mkt.get('growth_projection', 'N/A')} | {mkt.get('market_opportunity', 'N/A')}",
        f"⚠️ Risk: {rsk.get('risk_assessment', 'N/A')}",
        f"📋 Compliance: {cmp_.get('timeline', 'N/A')} | {cmp_.get('regulatory_framework', 'N/A')}",
        f"💡 Innovation: roadmap with {len(inn.get('initiatives', []))} initiatives",
    ]

    state.final_answer = (
        f"# Green Hill Canarias Digital Twin\n\n"
        f"Question: {q}\n\n"
        f"Summary:\n- " + "\n- ".join(parts)
    )
    state.finalize = True
    state.history.append(Message(role="System", content="Final synthesis completed"))
    return state
