#!/usr/bin/env python3
"""
Green Hill Canarias LangGraph Application
Multi-Agent RAG system for strategic document analysis
"""

import logging
import os
from typing import Dict, Any, Optional, List, Annotated
from datetime import datetime

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph.message import add_messages

from models import AgentState
from document_store import get_retriever

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize LLM
def get_llm():
    model = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o")
    return ChatOpenAI(model=model, temperature=0.1)

class GreenHillAgent:
    """Base agent for Green Hill Canarias system"""
    
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.llm = get_llm()
        self.retriever = get_retriever()
    
    async def process(self, state: AgentState) -> Dict[str, Any]:
        """Process user query with document retrieval"""
        try:
            messages = state.get("messages", [])
            if not messages:
                return {"messages": [AIMessage(content="No query provided")]}
            
            user_query = messages[-1].content if messages else ""
            
            # Retrieve relevant documents
            docs = []
            if hasattr(self.retriever, 'get_relevant_documents'):
                docs = self.retriever.get_relevant_documents(user_query)
            
            # Create context from documents
            context = "\n\n".join([doc.page_content for doc in docs[:3]])
            
            # Generate agent-specific prompt
            prompt = f"""You are a {self.agent_type} agent for Green Hill Canarias.
            
User Query: {user_query}

Relevant Context:
{context}

Provide a comprehensive analysis based on your expertise in {self.agent_type} and the available context.
Focus on actionable insights and strategic recommendations."""

            # Generate response
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            return {
                "messages": [response],
                "agent_type": self.agent_type,
                "context_used": len(docs)
            }
            
        except Exception as e:
            logger.error(f"Error in {self.agent_type} agent: {str(e)}")
            return {
                "messages": [AIMessage(content=f"Error processing request: {str(e)}")],
                "agent_type": self.agent_type
            }

# Agent instances
strategy_agent = GreenHillAgent("Strategy")
finance_agent = GreenHillAgent("Finance") 
construction_agent = GreenHillAgent("Construction")
governance_agent = GreenHillAgent("Governance")

# Agent processing functions
async def strategy_node(state: AgentState) -> AgentState:
    result = await strategy_agent.process(state)
    return {**state, **result}

async def finance_node(state: AgentState) -> AgentState:
    result = await finance_agent.process(state)
    return {**state, **result}

async def construction_node(state: AgentState) -> AgentState:
    result = await construction_agent.process(state)
    return {**state, **result}

async def governance_node(state: AgentState) -> AgentState:
    result = await governance_agent.process(state)
    return {**state, **result}

def route_query(state: AgentState) -> str:
    """Route query to appropriate agent based on content"""
    messages = state.get("messages", [])
    if not messages:
        return "strategy"
    
    query = messages[-1].content.lower()
    
    if any(word in query for word in ["finance", "budget", "cost", "funding", "investment"]):
        return "finance"
    elif any(word in query for word in ["construction", "building", "facility", "infrastructure"]):
        return "construction"
    elif any(word in query for word in ["governance", "management", "organization", "leadership"]):
        return "governance"
    else:
        return "strategy"

# Build the graph
def build_graph():
    """Build the LangGraph workflow"""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("strategy", strategy_node)
    workflow.add_node("finance", finance_node)
    workflow.add_node("construction", construction_node)
    workflow.add_node("governance", governance_node)
    
    # Set entry point
    workflow.set_entry_point("strategy")
    
    # Add conditional routing
    workflow.add_conditional_edges(
        "strategy",
        route_query,
        {
            "strategy": END,
            "finance": "finance",
            "construction": "construction", 
            "governance": "governance"
        }
    )
    
    # End other agents
    workflow.add_edge("finance", END)
    workflow.add_edge("construction", END)
    workflow.add_edge("governance", END)
    
    return workflow.compile()

# Create the app
app = build_graph()

# Main execution function
async def main():
    """Main execution function for testing"""
    test_query = "What is the strategic vision for Green Hill Canarias?"
    
    initial_state = {
        "messages": [HumanMessage(content=test_query)],
        "agent_type": "strategy"
    }
    
    result = await app.ainvoke(initial_state)
    print("Response:", result["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())
