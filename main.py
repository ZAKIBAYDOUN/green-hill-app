# main.py
import os
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END

# Define minimal state schema
class State(TypedDict, total=False):
    question: str
    answer: str
    error: Optional[str]

def answer_question(state: State) -> State:
    """Answer questions about Green Hill Canarias - no build-time dependencies"""
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
            return {"answer": response.content}
            
        except Exception:
            # Simple fallback - no heavy dependencies
            return {
                "answer": f"""Green Hill Canarias Strategic Analysis:

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
        return {
            "error": f"Processing error: {str(e)}",
            "answer": "Unable to process request. Please try again."
        }

# Build graph with zero build-time work
def build_graph():
    """Build the graph - no document ingestion or heavy operations"""
    graph = StateGraph(State)
    graph.add_node("answer_question", answer_question)  
    graph.add_edge(START, "answer_question")
    graph.add_edge("answer_question", END)
    return graph.compile()

# Export app at module level for LangGraph Cloud
app = build_graph()
