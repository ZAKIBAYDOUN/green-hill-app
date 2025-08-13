# main.py
import os
import requests
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END

# Define expanded state schema for multi-agent system
class TwinState(TypedDict, total=False):
    question: str
    # Agent outputs
    strategy_output: Optional[str]
    operations_output: Optional[str]
    finance_output: Optional[str]
    market_output: Optional[str]
    risk_output: Optional[str]
    compliance_output: Optional[str]
    innovation_output: Optional[str]
    # Orchestrator outputs
    digital_twin_analysis: Optional[str]
    green_hill_gpt_response: Optional[str]
    final_answer: Optional[str]
    # System
    error: Optional[str]
    config: Optional[dict]

def digital_twin_orchestrator(state: TwinState) -> TwinState:
    """Digital Twin orchestrator - coordinates all agents and external calls"""
    question = state.get("question")
    if not question:
        return {"error": "Missing 'question' in state"}
    
    config = state.get("config", {})
    enable_green_hill_gpt = config.get("enable_green_hill_gpt", False)
    
    # Initialize analysis with question context
    analysis = f"Digital Twin Analysis for: {question}\n\n"
    
    # Collect agent outputs
    strategy = state.get("strategy_output", "")
    operations = state.get("operations_output", "")
    finance = state.get("finance_output", "")
    market = state.get("market_output", "")
    risk = state.get("risk_output", "")
    compliance = state.get("compliance_output", "")
    innovation = state.get("innovation_output", "")
    
    if any([strategy, operations, finance, market, risk, compliance, innovation]):
        analysis += "🔍 AGENT SYNTHESIS:\n"
        if strategy:
            analysis += f"📈 Strategy: {strategy}\n"
        if operations:
            analysis += f"⚙️ Operations: {operations}\n"
        if finance:
            analysis += f"💰 Finance: {finance}\n"
        if market:
            analysis += f"📊 Market: {market}\n"
        if risk:
            analysis += f"⚠️ Risk: {risk}\n"
        if compliance:
            analysis += f"📋 Compliance: {compliance}\n"
        if innovation:
            analysis += f"💡 Innovation: {innovation}\n"
        analysis += "\n"
    
    # Call Green Hill GPT if enabled
    green_hill_response = ""
    if enable_green_hill_gpt:
        try:
            green_hill_response = call_green_hill_gpt(question)
            analysis += f"🌟 GREEN HILL GPT INSIGHTS:\n{green_hill_response}\n\n"
        except Exception as e:
            analysis += f"⚠️ Green Hill GPT call failed: {str(e)}\n\n"
    
    # Synthesize final recommendation
    analysis += "🎯 DIGITAL TWIN RECOMMENDATION:\n"
    analysis += "Based on multi-agent analysis and strategic positioning, "
    analysis += "Green Hill Canarias should focus on integrated growth strategies "
    analysis += "that leverage sustainable innovation and market opportunities.\n"
    
    return {
        "digital_twin_analysis": analysis,
        "green_hill_gpt_response": green_hill_response,
        "final_answer": analysis
    }

def call_green_hill_gpt(question: str) -> str:
    """Call external Green Hill GPT endpoint for continuous testing"""
    # Placeholder for Green Hill GPT API integration
    # Replace with actual endpoint when available
    GREEN_HILL_URL = os.getenv("GREEN_HILL_GPT_URL", "")
    API_KEY = os.getenv("GREEN_HILL_API_KEY", "")
    
    if not GREEN_HILL_URL:
        return "Green Hill GPT endpoint not configured"
    
    try:
        payload = {"question": question}
        headers = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}
        response = requests.post(GREEN_HILL_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json().get("answer", "No response from Green Hill GPT")
    except Exception as e:
        return f"Green Hill GPT call failed: {str(e)}"

# Individual Agent Nodes
def strategy_agent(state: TwinState) -> TwinState:
    """Strategic planning and long-term vision analysis"""
    question = state.get("question", "")
    
    analysis = """Strategic Analysis: Evaluating long-term positioning and competitive advantages. 
    Focus areas: Market expansion, partnership opportunities, sustainable growth models, 
    brand positioning in Atlantic region."""
    
    return {"strategy_output": analysis}

def operations_agent(state: TwinState) -> TwinState:
    """Operational efficiency and process optimization"""
    question = state.get("question", "")
    
    analysis = """Operations Analysis: Assessing operational workflows and efficiency metrics. 
    Focus areas: Process automation, resource optimization, supply chain management, 
    infrastructure scalability."""
    
    return {"operations_output": analysis}

def finance_agent(state: TwinState) -> TwinState:
    """Financial planning and investment analysis"""
    question = state.get("question", "")
    
    analysis = """Financial Analysis: Evaluating investment opportunities and fiscal health. 
    Focus areas: ROI optimization, funding strategies, cost-benefit analysis, 
    financial risk management."""
    
    return {"finance_output": analysis}

def market_intel_agent(state: TwinState) -> TwinState:
    """Market research and competitive intelligence"""
    question = state.get("question", "")
    
    analysis = """Market Intelligence: Analyzing market trends and competitive landscape. 
    Focus areas: Consumer behavior, market penetration, competitive positioning, 
    emerging opportunities in Canary Islands market."""
    
    return {"market_output": analysis}

def risk_agent(state: TwinState) -> TwinState:
    """Risk assessment and mitigation strategies"""
    question = state.get("question", "")
    
    analysis = """Risk Analysis: Identifying and evaluating potential risks and mitigation strategies. 
    Focus areas: Market volatility, regulatory changes, operational risks, 
    climate and environmental factors."""
    
    return {"risk_output": analysis}

def compliance_agent(state: TwinState) -> TwinState:
    """Regulatory compliance and legal analysis"""
    question = state.get("question", "")
    
    analysis = """Compliance Analysis: Ensuring adherence to regulatory requirements. 
    Focus areas: Spanish/EU regulations, Canary Islands special tax regime, 
    environmental compliance, data protection standards."""
    
    return {"compliance_output": analysis}

def innovation_agent(state: TwinState) -> TwinState:
    """Innovation and technology advancement"""
    question = state.get("question", "")
    
    analysis = """Innovation Analysis: Exploring technological advancement opportunities. 
    Focus areas: Digital transformation, sustainability technologies, 
    AI/automation integration, green energy solutions."""
    
    return {"innovation_output": analysis}

def answer_question(state: TwinState) -> TwinState:
    """Answer questions about Green Hill Canarias - fallback for simple queries"""
    question = state.get("question")
    if not question:
        return {"error": "Missing 'question' in state"}
    
    try:
        # Try to use OpenAI if available, fallback gracefully
        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import HumanMessage
            
            model = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o") 
            llm = ChatOpenAI(model=model, temperature=0.1)
            
            prompt = f"""You are an AI assistant for Green Hill Canarias, a strategic business development project in the Canary Islands.

Question: {question}

Provide insights on Green Hill Canarias covering:
- Strategic business development
- Sustainable growth opportunities  
- Innovation initiatives
- Market positioning

Give actionable recommendations."""

            response = llm.invoke([HumanMessage(content=prompt)])
            return {"final_answer": response.content}
            
        except Exception:
            # Simple fallback - no heavy dependencies
            return {
                "final_answer": f"""Green Hill Canarias Strategic Analysis:

Question: {question}

Green Hill Canarias is a strategic business development project in the Canary Islands focused on:

🎯 Strategic Vision: Sustainable growth and innovation hub
💡 Innovation Focus: Technology integration and digital transformation  
🌱 Sustainability: Environmental responsibility and green initiatives
📈 Business Development: Market expansion and strategic partnerships
🏗️ Infrastructure: Modern facilities and smart construction
💰 Financial Strategy: Sustainable funding and investment attraction

This project represents a comprehensive approach to business development in the Atlantic region, combining strategic planning with operational excellence.

For detailed analysis of specific aspects, please ensure API configuration is complete."""
            }
            
    except Exception as e:
        return {"error": f"Failed to process question: {str(e)}"}

# Create the multi-agent graph
def create_multi_agent_graph():
    """Create the full multi-agent graph with digital twin orchestrator"""
    
    # Initialize the graph with expanded state
    graph = StateGraph(TwinState)
    
    # Add all agent nodes
    graph.add_node("digital_twin", digital_twin_orchestrator)
    graph.add_node("strategy", strategy_agent)
    graph.add_node("operations", operations_agent) 
    graph.add_node("finance", finance_agent)
    graph.add_node("market_intel", market_intel_agent)
    graph.add_node("risk", risk_agent)
    graph.add_node("compliance", compliance_agent)
    graph.add_node("innovation", innovation_agent)
    
    # Define the flow:
    # START → all agents in parallel → digital_twin → END
    graph.add_edge(START, "strategy")
    graph.add_edge(START, "operations")
    graph.add_edge(START, "finance")
    graph.add_edge(START, "market_intel")
    graph.add_edge(START, "risk")
    graph.add_edge(START, "compliance")
    graph.add_edge(START, "innovation")
    
    # All agents feed into digital twin for synthesis
    graph.add_edge("strategy", "digital_twin")
    graph.add_edge("operations", "digital_twin")
    graph.add_edge("finance", "digital_twin")
    graph.add_edge("market_intel", "digital_twin")
    graph.add_edge("risk", "digital_twin")
    graph.add_edge("compliance", "digital_twin")
    graph.add_edge("innovation", "digital_twin")
    
    # Digital twin provides final output
    graph.add_edge("digital_twin", END)
    
    return graph.compile()

def create_simple_graph():
    """Create simple single-node graph for basic deployment"""
    graph = StateGraph(TwinState)
    graph.add_node("answer_question", answer_question)
    graph.add_edge(START, "answer_question")
    graph.add_edge("answer_question", END)
    return graph.compile()

# Determine which graph to use based on environment
deployment_mode = os.getenv("DEPLOYMENT_MODE", "simple")

if deployment_mode == "multi_agent":
    app = create_multi_agent_graph()
else:
    app = create_simple_graph()
