# app/agents.py
from app.models import TwinState, AgentName, Message
from app.document_store import DocumentStore
from typing import Optional, Dict, Any
import os


def record_output(state: TwinState, agent: AgentName, output_key: str, output: Dict[str, Any], note: str):
    """Record agent output (dict) in state and append a brief note to history."""
    state.history.append(Message(role=agent.value, content=note))
    setattr(state, output_key, output)
    state.current_agent = agent
    return state


def _next_from_targets(state: TwinState, current: AgentName) -> Optional[AgentName]:
    """Return the next agent in the target list, normalizing aliases."""

    if not state.target_agents:
        return None

    def _normalize(agent: AgentName) -> AgentName:
        return AgentName.MARKET if agent == AgentName.MARKET_INTEL else agent

    normalized_targets = [_normalize(a) for a in state.target_agents]
    current_norm = _normalize(current)

    try:
        idx = normalized_targets.index(current_norm)
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


def media_node(state: TwinState, doc_store: DocumentStore) -> TwinState:
    q = state.question or ""
    ctx = doc_store.query(f"media assets branding {q}")
    analysis = enhance_with_llm(f"Media strategy and asset guidance for: {q}", ctx)
    output = {
        "asset_pipeline": "Placeholder",
        "analysis": analysis,
        "context_used": len((ctx or "").split("\n\n")),
    }
    record_output(state, AgentName.MEDIA, "media_output", output, "Media guidance completed")
    state.next_agent = _next_from_targets(state, AgentName.MEDIA)
    return state


def qms_node(state: TwinState, doc_store: DocumentStore) -> TwinState:
    q = state.question or ""
    ctx = doc_store.query(f"quality management system {q}")
    analysis = enhance_with_llm(f"QMS and SOP alignment for: {q}", ctx)
    output = {
        "audit_focus": "Placeholder",
        "analysis": analysis,
        "context_used": len((ctx or "").split("\n\n")),
    }
    record_output(state, AgentName.QMS, "qms_output", output, "QMS review completed")
    state.next_agent = _next_from_targets(state, AgentName.QMS)
    return state


def governance_node(state: TwinState, doc_store: DocumentStore) -> TwinState:
    q = state.question or ""
    ctx = doc_store.query(f"governance decision policy {q}")
    analysis = enhance_with_llm(f"Governance alignment for: {q}", ctx)
    output = {
        "policy_considerations": "Placeholder",
        "analysis": analysis,
        "context_used": len((ctx or "").split("\n\n")),
    }
    record_output(state, AgentName.GOVERNANCE, "governance_output", output, "Governance review completed")
    state.next_agent = _next_from_targets(state, AgentName.GOVERNANCE)
    return state


def aemps_node(state: TwinState, doc_store: DocumentStore) -> TwinState:
    q = state.question or ""
    ctx = doc_store.query(f"AEMPS EU-GMP {q}")
    analysis = enhance_with_llm(f"AEMPS readiness assessment for: {q}", ctx)
    output = {
        "readiness_level": "Placeholder",
        "analysis": analysis,
        "context_used": len((ctx or "").split("\n\n")),
    }
    record_output(state, AgentName.AEMPS, "aemps_output", output, "AEMPS readiness assessed")
    state.next_agent = _next_from_targets(state, AgentName.AEMPS)
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
    med = state.media_output or {}
    qms = state.qms_output or {}
    gov = state.governance_output or {}
    aem = state.aemps_output or {}

    parts = [
        f"🎯 Strategy ({strat.get('context_used', 0)} ctx): {strat.get('strategic_focus', 'N/A')} | {strat.get('timeline', '')}",
        f"💰 Finance ({fin.get('context_used', 0)} ctx): ROI {fin.get('roi_projection', 'N/A')} | CAPEX {fin.get('capex_estimate', 'N/A')}",
        f"⚙️ Operations ({ops.get('context_used', 0)} ctx): {ops.get('implementation_schedule', 'N/A')}",
        f"📊 Market ({mkt.get('context_used', 0)} ctx): {mkt.get('growth_projection', 'N/A')} | {mkt.get('market_opportunity', 'N/A')}",
        f"⚠️ Risk ({rsk.get('context_used', 0)} ctx): {rsk.get('risk_assessment', 'N/A')}",
        f"📋 Compliance ({cmp_.get('context_used', 0)} ctx): {cmp_.get('timeline', 'N/A')} | {cmp_.get('regulatory_framework', 'N/A')}",
        f"💡 Innovation ({inn.get('context_used', 0)} ctx): roadmap with {len(inn.get('initiatives', []))} initiatives",
        f"🎥 Media ({med.get('context_used', 0)} ctx): {med.get('asset_pipeline', 'N/A')}",
        f"🧪 QMS ({qms.get('context_used', 0)} ctx): {qms.get('audit_focus', 'N/A')}",
        f"🧭 Governance ({gov.get('context_used', 0)} ctx): {gov.get('policy_considerations', 'N/A')}",
        f"🏛️ AEMPS ({aem.get('context_used', 0)} ctx): {aem.get('readiness_level', 'N/A')}",
    ]

    state.final_answer = (
        f"# Green Hill Canarias Digital Twin\n\n"
        f"Question: {q}\n\n"
        f"Summary:\n- " + "\n- ".join(parts)
    )
    state.finalize = True
    state.history.append(Message(role="System", content="Final synthesis completed"))
    # Learning & alignment logging
    try:
        import json, datetime
        if state.metadata.get("decision"):
            record = {
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "agent": state.current_agent.value if state.current_agent else "finalize",
                "input_summary": state.question,
                "decision": state.metadata.get("decision"),
                "rationale": state.metadata.get("rationale", ""),
                "evidence_refs": state.metadata.get("evidence_refs", []),
                "outcomes": state.metadata.get("outcomes", []),
                "followups": state.metadata.get("followups", []),
            }
            with open("data/governance/decision_register.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(record) + "\n")
            with open("data/governance/weekly_learning.md", "a", encoding="utf-8") as fh:
                fh.write(f"- {record['timestamp']}: {record['decision']}\n")
        if state.metadata.get("capa_issue"):
            capa = {
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "source_agent": state.current_agent.value if state.current_agent else "finalize",
                "issue": state.metadata.get("capa_issue"),
                "root_cause": state.metadata.get("root_cause", ""),
                "corrective": state.metadata.get("corrective", ""),
                "preventive": state.metadata.get("preventive", ""),
                "status": state.metadata.get("status", "open"),
                "owner": state.metadata.get("owner", "unassigned"),
            }
            with open("data/compliance/capa_log.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(capa) + "\n")
    except Exception:
        pass
    # Optional: archive outputs into vector store for future retrieval
    if os.getenv("ARCHIVE_AGENT_OUTPUTS", "1").lower() in {"1", "true", "yes"}:
        try:
            doc_store.add_agent_outputs(state)
        except Exception:
            pass
    return state


def green_hill_node(state: TwinState, doc_store: DocumentStore) -> TwinState:
    """Optional GreenHillGPT step that synthesizes an investor-facing memo using LLM.

    Uses GREEN_HILL_CHAT_MODEL if set, else OPENAI_CHAT_MODEL. Falls back gracefully.
    """
    # Build compact context from prior outputs
    strat = state.strategy_output or {}
    fin = state.finance_output or {}
    ops = state.operations_output or {}
    mkt = state.market_output or {}
    rsk = state.risk_output or {}
    cmp_ = state.compliance_output or {}
    inn = state.innovation_output or {}

    retrieved = state.context.get("retrieved_docs", [])

    system_prompt = (
        "You are Green Hill Canarias Investor Assistant. Produce a crisp, factual, and "
        "investor-ready memo. Merge domain agent insights without repeating. Include a "
        "short executive summary, key metrics, risks, and next steps."
    )

    user_prompt = (
        f"Question: {state.question}\n\n"
        f"Strategy: {strat}\nFinance: {fin}\nOperations: {ops}\n"
        f"Market: {mkt}\nRisk: {rsk}\nCompliance: {cmp_}\nInnovation: {inn}\n\n"
        f"Top context: {retrieved[:3]}"
    )

    content = None
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage, SystemMessage

        model = os.getenv("GREEN_HILL_CHAT_MODEL") or os.getenv("OPENAI_CHAT_MODEL", "gpt-4o")
        llm = ChatOpenAI(model=model, temperature=0.2)
        resp = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
        content = resp.content
    except Exception as e:
        content = (
            "Investor memo (LLM unavailable):\n"
            "- Summary: Multi-agent analysis complete.\n"
            f"- Key ROI: {fin.get('roi_projection', 'N/A')} | CAPEX: {fin.get('capex_estimate', 'N/A')}\n"
            f"- Risks: {', '.join(rsk.get('primary_risks', [])) or 'N/A'}\n"
            f"- Next: {inn.get('initiatives', ['Prioritize planning'])[0]}\n"
        )

    state.green_hill_response = {"memo": content}
    state.history.append(Message(role="GreenHillGPT", content="Investor memo prepared"))
    # If there is no queued next agent, finalize here
    state.next_agent = None
    if not state.final_answer:
        state.final_answer = content
    state.finalize = True
    # Optional: archive outputs including memo
    if os.getenv("ARCHIVE_AGENT_OUTPUTS", "1").lower() in {"1", "true", "yes"}:
        try:
            doc_store.add_agent_outputs(state)
        except Exception:
            pass
    return state
