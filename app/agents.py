# app/agents.py
from .models import TwinState, AgentName, Message
from .document_store import DocumentStore
from typing import Optional
import os

def record(state: TwinState, agent: AgentName, output_key: str, content: str):
    """Record agent output in state and history"""
    state.history.append(Message(role=agent.value, content=content))
    setattr(state, output_key, content)
    state.current_agent = agent
    return state

def enhance_with_llm(prompt: str, context: str = "") -> str:
    """Enhance agent analysis with LLM if available"""
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage, SystemMessage
        
        model = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
        llm = ChatOpenAI(model=model, temperature=0.1)
        
        system_prompt = """You are a domain expert for Green Hill Canarias, a strategic business development project in the Canary Islands. Provide concise, actionable insights."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Context: {context}\n\nQuery: {prompt}")
        ]
        
        response = llm.invoke(messages)
        return response.content
        
    except Exception as e:
        # Graceful fallback
        return f"Analysis: {prompt}\n\nContext: {context}\n\n[LLM enhancement unavailable: {str(e)}]"

def strategy_node(state: TwinState, doc_store: DocumentStore) -> TwinState:
    """Strategic planning and long-term vision analysis"""
    question = state.question
    
    # Get document context
    doc_context = doc_store.query(f"strategy planning vision {question}")
    
    # Generate analysis
    prompt = f"Analyze strategic opportunities and positioning for: {question}"
    analysis = enhance_with_llm(prompt, doc_context)
    
    output = f"""🎯 STRATEGIC ANALYSIS

Question: {question}

{analysis}

Focus Areas:
• Market expansion and positioning in Atlantic region
• Strategic partnerships and alliance opportunities  
• Competitive advantages and differentiation
• Long-term vision and growth roadmap
• Brand positioning and market presence

Strategic Context: {doc_context[:200]}..."""
    
    record(state, AgentName.STRATEGY, "strategy_output", output)
    state.next_agent = AgentName.OPERATIONS
    return state

def operations_node(state: TwinState, doc_store: DocumentStore) -> TwinState:
    """Operational efficiency and process optimization"""
    question = state.question
    
    doc_context = doc_store.query(f"operations processes efficiency {question}")
    prompt = f"Analyze operational requirements and optimization for: {question}"
    analysis = enhance_with_llm(prompt, doc_context)
    
    output = f"""⚙️ OPERATIONS ANALYSIS

Question: {question}

{analysis}

Focus Areas:
• Process automation and workflow optimization
• Resource allocation and efficiency metrics
• Supply chain and logistics management
• Infrastructure scalability and capacity planning
• Quality management and operational excellence

Operational Context: {doc_context[:200]}..."""
    
    record(state, AgentName.OPERATIONS, "operations_output", output)
    state.next_agent = AgentName.FINANCE
    return state

def finance_node(state: TwinState, doc_store: DocumentStore) -> TwinState:
    """Financial planning and investment analysis"""
    question = state.question
    
    doc_context = doc_store.query(f"finance investment funding {question}")
    prompt = f"Analyze financial implications and investment opportunities for: {question}"
    analysis = enhance_with_llm(prompt, doc_context)
    
    output = f"""💰 FINANCIAL ANALYSIS

Question: {question}

{analysis}

Focus Areas:
• ROI optimization and investment strategies
• Funding mechanisms and capital structure
• Cost-benefit analysis and financial modeling
• Risk-adjusted returns and financial projections
• Cash flow management and liquidity planning

Financial Context: {doc_context[:200]}..."""
    
    record(state, AgentName.FINANCE, "finance_output", output)
    state.next_agent = AgentName.MARKET_INTEL
    return state

def market_intel_node(state: TwinState, doc_store: DocumentStore) -> TwinState:
    """Market research and competitive intelligence"""
    question = state.question
    
    doc_context = doc_store.query(f"market research competition canary islands {question}")
    prompt = f"Analyze market opportunities and competitive landscape for: {question}"
    analysis = enhance_with_llm(prompt, doc_context)
    
    output = f"""📊 MARKET INTELLIGENCE

Question: {question}

{analysis}

Focus Areas:
• Market size, growth potential, and trends
• Competitive landscape and positioning
• Customer segments and value propositions
• Market entry strategies and barriers
• Canary Islands specific market dynamics

Market Context: {doc_context[:200]}..."""
    
    record(state, AgentName.MARKET_INTEL, "market_output", output)
    state.next_agent = AgentName.RISK
    return state

def risk_node(state: TwinState, doc_store: DocumentStore) -> TwinState:
    """Risk assessment and mitigation strategies"""
    question = state.question
    
    doc_context = doc_store.query(f"risk assessment mitigation {question}")
    prompt = f"Analyze risks and mitigation strategies for: {question}"
    analysis = enhance_with_llm(prompt, doc_context)
    
    output = f"""⚠️ RISK ANALYSIS

Question: {question}

{analysis}

Focus Areas:
• Market and operational risk assessment
• Regulatory and compliance risks
• Financial and liquidity risks
• Environmental and climate considerations
• Strategic and competitive risks

Risk Context: {doc_context[:200]}..."""
    
    record(state, AgentName.RISK, "risk_output", output)
    state.next_agent = AgentName.COMPLIANCE
    return state

def compliance_node(state: TwinState, doc_store: DocumentStore) -> TwinState:
    """Regulatory compliance and legal analysis"""
    question = state.question
    
    doc_context = doc_store.query(f"compliance regulatory legal spain eu {question}")
    prompt = f"Analyze compliance and regulatory requirements for: {question}"
    analysis = enhance_with_llm(prompt, doc_context)
    
    output = f"""📋 COMPLIANCE ANALYSIS

Question: {question}

{analysis}

Focus Areas:
• Spanish and EU regulatory requirements
• Canary Islands special economic zone benefits
• Environmental and sustainability compliance
• Data protection and privacy regulations
• Industry-specific compliance obligations

Compliance Context: {doc_context[:200]}..."""
    
    record(state, AgentName.COMPLIANCE, "compliance_output", output)
    state.next_agent = AgentName.INNOVATION
    return state

def innovation_node(state: TwinState, doc_store: DocumentStore) -> TwinState:
    """Innovation and technology advancement"""
    question = state.question
    
    doc_context = doc_store.query(f"innovation technology digital transformation {question}")
    prompt = f"Analyze innovation opportunities and technology applications for: {question}"
    analysis = enhance_with_llm(prompt, doc_context)
    
    output = f"""💡 INNOVATION ANALYSIS

Question: {question}

{analysis}

Focus Areas:
• Digital transformation opportunities
• Emerging technology applications
• Innovation ecosystem and partnerships
• Sustainability and green technology
• AI and automation integration

Innovation Context: {doc_context[:200]}..."""
    
    record(state, AgentName.INNOVATION, "innovation_output", output)
    state.next_agent = None  # Signal to finalize
    return state

def finalize_node(state: TwinState, doc_store: DocumentStore) -> TwinState:
    """Compose final answer from all agent outputs"""
    
    # Collect all outputs
    outputs = [
        ("🎯 Strategic Analysis", state.strategy_output),
        ("⚙️ Operations Analysis", state.operations_output), 
        ("💰 Financial Analysis", state.finance_output),
        ("📊 Market Intelligence", state.market_output),
        ("⚠️ Risk Analysis", state.risk_output),
        ("📋 Compliance Analysis", state.compliance_output),
        ("💡 Innovation Analysis", state.innovation_output)
    ]
    
    # Build comprehensive response
    final_response = f"""# Green Hill Canarias Digital Twin Analysis

**Question:** {state.question}

## Executive Summary
Based on comprehensive multi-agent analysis across strategy, operations, finance, market intelligence, risk, compliance, and innovation domains:

"""
    
    # Add each agent's contribution
    for title, output in outputs:
        if output:
            # Extract key insights (first few lines)
            lines = output.split('\n')
            key_insights = '\n'.join(lines[2:6]) if len(lines) > 2 else output[:300]
            final_response += f"### {title}\n{key_insights}\n\n"
    
    # Add synthesis
    final_response += """## Integrated Recommendations

The Digital Twin analysis reveals interconnected opportunities across all business domains. Success depends on:

1. **Strategic Alignment**: Leveraging Canary Islands' unique positioning
2. **Operational Excellence**: Building scalable, efficient processes  
3. **Financial Sustainability**: Ensuring robust ROI and funding strategies
4. **Market Leadership**: Capitalizing on competitive advantages
5. **Risk Management**: Proactive mitigation of identified risks
6. **Regulatory Compliance**: Full adherence to applicable regulations
7. **Innovation Culture**: Continuous technology and process advancement

## Next Steps
Detailed implementation planning should prioritize high-impact, low-risk initiatives while building capabilities for more complex strategic moves.

---
*Analysis generated by Green Hill Canarias Digital Twin System*"""
    
    state.final_answer = final_response
    state.finalize = True
    
    # Record the synthesis
    record(state, AgentName.STRATEGY, "final_synthesis", final_response)
    
    return state
