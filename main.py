#!/usr/bin/env python3
"""
Green Hill Canarias Main Entry Point - Fixed Version
Main orchestrator using the actual available modules and structure

This script coordinates the Green Hill Canarias digital twin system
using the existing LangGraph architecture in the .langgraph_api directory.
"""

import logging
import asyncio
import os
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

# Add the .langgraph_api directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.langgraph_api'))

try:
    from app.ghc_twin import build_graph
    from app.models import TwinState, AgentName, Message
    from app.document_store import get_document_store
except ImportError as e:
    logging.error(f"Import error: {e}")
    logging.error("Make sure the .langgraph_api directory structure is correct")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GreenHillOrchestrator:
    """
    Master orchestrator for Green Hill Canarias Digital Twin
    Uses the existing LangGraph architecture
    """
    
    def __init__(self, vector_store_dir: Optional[str] = None):
        """Initialize orchestrator with document store"""
        self.vector_store_dir = vector_store_dir or os.getenv("VECTORSTORE_DIR", "vector_store")
        self.document_store = get_document_store(self.vector_store_dir)
        self.graph = build_graph()
        self.session_log = []
        
        logger.info("🎯 Green Hill Orchestrator initialized")
        logger.info(f"📁 Vector store directory: {self.vector_store_dir}")
        logger.info(f"📚 Document store available: {self.document_store.is_available() if self.document_store else False}")
    
    def analyze_question_complexity(self, question: str) -> str:
        """Analyze question complexity for processing"""
        question_lower = question.lower()
        
        # High complexity indicators
        high_indicators = [
            'comprehensive', 'detailed analysis', 'in-depth', 'complex',
            'multi-faceted', 'strategic implications', 'cross-functional',
            'integrated analysis', 'synthesis', 'comprehensive review'
        ]
        
        # Medium complexity indicators  
        medium_indicators = [
            'analyze', 'evaluate', 'assess', 'compare', 'investigate',
            'examine', 'review', 'considerations', 'implications'
        ]
        
        if any(indicator in question_lower for indicator in high_indicators):
            return 'high'
        elif any(indicator in question_lower for indicator in medium_indicators):
            return 'medium'
        else:
            return 'basic'
    
    def determine_source_type(self, question: str) -> str:
        """Determine source type based on question context"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['master', 'comprehensive', 'complete']):
            return 'master'
        elif any(word in question_lower for word in ['investor', 'shareholder', 'investment']):
            return 'investor'
        elif any(word in question_lower for word in ['supplier', 'provider', 'vendor']):
            return 'supplier'
        elif any(word in question_lower for word in ['operations', 'ocs', 'compliance']):
            return 'ocs_feed'
        elif any(word in question_lower for word in ['web', 'online', 'market']):
            return 'web_source'
        else:
            return 'public'
    
    async def process_query(self, question: str, source_type: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Process a query using the LangGraph system"""
        try:
            start_time = datetime.now()
            logger.info(f"🤖 Processing query: {question[:100]}...")
            
            # Determine source type if not provided
            if not source_type:
                source_type = self.determine_source_type(question)
            
            # Create initial state
            initial_state = TwinState(
                question=question,
                source_type=source_type,
                timestamp=start_time.isoformat(),
                **kwargs
            )
            
            # Run through LangGraph system
            final_state = self.graph.invoke(initial_state.model_dump())
            
            # Convert back to TwinState for processing
            result_state = TwinState(**final_state)
            
            # Log the analysis
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            log_entry = {
                'timestamp': start_time.isoformat(),
                'question': question,
                'source_type': source_type,
                'processing_time_seconds': processing_time,
                'success': not result_state.errors,
                'final_agent': result_state.current_agent.value if result_state.current_agent else None,
                'errors': result_state.errors
            }
            
            self.session_log.append(log_entry)
            
            # Format response
            response = {
                'orchestration': {
                    'question': question,
                    'source_type': source_type,
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'processing_time_seconds': processing_time,
                    'system_status': 'operational'
                },
                'result': {
                    'success': not result_state.errors,
                    'final_answer': result_state.final_answer,
                    'errors': result_state.errors,
                    'agents_involved': [agent.value for agent in result_state.target_agents],
                    'outputs': {
                        'strategy': result_state.strategy_output,
                        'finance': result_state.finance_output,
                        'operations': result_state.operations_output,
                        'market': result_state.market_output,
                        'risk': result_state.risk_output,
                        'compliance': result_state.compliance_output,
                        'innovation': result_state.innovation_output,
                        'green_hill': result_state.green_hill_response
                    }
                },
                'session_log_entries': len(self.session_log)
            }
            
            logger.info(f"✅ Query processed successfully | Time: {processing_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error processing query: {e}")
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            return {
                'orchestration': {
                    'question': question,
                    'source_type': source_type or 'unknown',
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'processing_time_seconds': processing_time,
                    'system_status': 'error'
                },
                'result': {
                    'success': False,
                    'error': str(e),
                    'final_answer': f"Error processing query: {e}"
                },
                'session_log_entries': len(self.session_log)
            }
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of the current orchestration session"""
        if not self.session_log:
            return {'session_summary': 'No queries processed yet'}
        
        total_queries = len(self.session_log)
        successful_queries = sum(1 for log in self.session_log if log.get('success', False))
        avg_processing_time = sum(log.get('processing_time_seconds', 0) for log in self.session_log) / total_queries
        
        return {
            'session_summary': {
                'total_queries': total_queries,
                'successful_queries': successful_queries,
                'success_rate': f"{(successful_queries/total_queries)*100:.1f}%",
                'average_processing_time': f"{avg_processing_time:.2f}s",
                'document_store_available': self.document_store.is_available() if self.document_store else False,
                'system_status': 'operational'
            },
            'recent_queries': self.session_log[-5:] if len(self.session_log) > 5 else self.session_log
        }

# Global orchestrator instance
orchestrator = None

def get_orchestrator(vector_store_dir: Optional[str] = None) -> GreenHillOrchestrator:
    """Get or create the global orchestrator instance"""
    global orchestrator
    if orchestrator is None:
        orchestrator = GreenHillOrchestrator(vector_store_dir)
    return orchestrator

# Convenience functions for different use cases
async def query_system(question: str, source_type: str = "public", **kwargs) -> Dict[str, Any]:
    """Query the Green Hill system with a question"""
    orch = get_orchestrator()
    return await orch.process_query(question, source_type, **kwargs)

async def master_query(question: str, **kwargs) -> Dict[str, Any]:
    """Comprehensive master-level query"""
    return await query_system(question, "master", **kwargs)

async def investor_query(question: str, **kwargs) -> Dict[str, Any]:
    """Investor-focused query"""
    return await query_system(question, "investor", **kwargs)

async def operations_query(question: str, **kwargs) -> Dict[str, Any]:
    """Operations-focused query"""
    return await query_system(question, "ocs_feed", **kwargs)

def main():
    """Main function for testing the orchestrator"""
    async def test_orchestrator():
        print("🎯 GREEN HILL CANARIAS ORCHESTRATOR - FIXED VERSION")
        print("🔬 Testing with Real LangGraph Architecture")
        print("=" * 80)
        
        # Test 1: Basic query
        print("\n🤖 Test 1: Basic Public Query")
        result1 = await query_system("What is Green Hill Canarias?")
        print(f"Success: {result1['result'].get('success', False)}")
        if result1['result'].get('final_answer'):
            print(f"Answer: {result1['result']['final_answer'][:200]}...")
        
        # Test 2: Master query
        print("\n🔗 Test 2: Master-Level Comprehensive Query")
        result2 = await master_query("Provide a comprehensive analysis of the Green Hill Canarias project")
        print(f"Success: {result2['result'].get('success', False)}")
        print(f"Agents involved: {result2['result'].get('agents_involved', [])}")
        
        # Test 3: Investor query
        print("\n🎯 Test 3: Investor Query")
        result3 = await investor_query("What are the investment opportunities and financial projections?")
        print(f"Success: {result3['result'].get('success', False)}")
        
        # Session summary
        print("\n📊 Session Summary:")
        summary = get_orchestrator().get_session_summary()
        print(f"Total queries: {summary['session_summary']['total_queries']}")
        print(f"Success rate: {summary['session_summary']['success_rate']}")
        print(f"Document store available: {summary['session_summary']['document_store_available']}")
        
        print("\n🏆 ORCHESTRATOR TEST COMPLETE")
    
    asyncio.run(test_orchestrator())

if __name__ == "__main__":
    main()