#!/usr/bin/env python3
"""
Green Hill Canarias Orchestrator - ALIGNED CANONICAL SYSTEM
Multi-Agent Orchestrator using 9 Canonical Documents with Full Agent Autonomy

This orchestrator coordinates all 7 specialized agents with unrestricted access
to investigate, analyze, and synthesize insights from the canonical strategic documents.

Agents with Full Autonomy:
- Strategy Agent: Strategic vision and planning analysis
- Finance Agent: Financial projections and funding analysis  
- Construction Agent: Facility design and construction planning
- QMS Agent: Quality management and compliance systems
- Governance Agent: Corporate governance and management structure
- Regulation Agent: Regulatory compliance and legal framework
- IR Agent: Investor relations and business model analysis

Key Features:
- Full agent autonomy for deep investigation
- Access to 9 canonical strategic documents as specified
- Sophisticated analysis engine with 3 complexity levels
- Cross-reference analysis capabilities
- Investigation logging and strategic synthesis
- No restrictions on analysis depth or complexity
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

"""The orchestrator relies on two optional internal modules:
`ghc_complete` provides the LangGraph implementation while
`ghc_document_system` exposes a document store.  These modules are not
distributed with the open repository, so importing them may fail when the
project is executed in a clean environment.  We catch the ImportError here and
fallback to graceful degradation so that the rest of the application (and the
tests) can still run.  A short guide on how to obtain these modules is included
in the README."""

try:  # pragma: no cover - executed only when optional deps are available
    from ghc_complete import build_graph, query_documents
    HAS_GHC_COMPLETE = True
except ImportError:  # pragma: no cover - graceful fallback
    HAS_GHC_COMPLETE = False

    class _DummyGraph:
        def invoke(self, *args, **kwargs):  # pragma: no cover - simple stub
            raise RuntimeError(
                "ghc_complete module not installed. Install it to enable multi-agent analysis."
            )

    def build_graph():  # pragma: no cover - graceful fallback
        logging.warning(
            "Optional dependency 'ghc_complete' not found. Using dummy graph; features are disabled."
        )
        return _DummyGraph()

    def query_documents(*args, **kwargs):  # pragma: no cover - graceful fallback
        raise RuntimeError(
            "ghc_complete module not installed. Install it to enable document querying."
        )

try:  # pragma: no cover - executed only when optional deps are available
    from ghc_document_system import DocumentStore
    HAS_GHC_DOCUMENT_SYSTEM = True
except ImportError:  # pragma: no cover - graceful fallback
    HAS_GHC_DOCUMENT_SYSTEM = False

    class DocumentStore:  # pragma: no cover - simple stub
        def __init__(self, *args, **kwargs):
            logging.warning(
                "Optional dependency 'ghc_document_system' not found. Document access is disabled."
            )

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GreenHillOrchestrator:
    """
    Master orchestrator for Green Hill Canarias Digital Twin
    Coordinates all agents with full autonomy using canonical documents
    """
    
    def __init__(self):
        """Initialize orchestrator with aligned canonical document system"""
        # Build graph/document store (may be dummy implementations if modules missing)
        self.graph = build_graph()
        self.document_store = DocumentStore()
        self.session_log = []

        if not HAS_GHC_COMPLETE or not HAS_GHC_DOCUMENT_SYSTEM:
            logger.warning(
                "Running in degraded mode – optional GHC modules missing. See README for setup instructions."
            )

        logger.info("🎯 Green Hill Orchestrator initialized with 9 canonical documents")
        logger.info("🔬 All agents granted full autonomy for investigation and analysis")
    
    def analyze_question_complexity(self, question: str) -> str:
        """Analyze question complexity for agent routing"""
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
    
    def determine_agent_routing(self, question: str) -> List[str]:
        """Determine which agents should handle the question"""
        question_lower = question.lower()
        agents = []
        
        # Strategy agent for strategic questions
        if any(word in question_lower for word in ['strategic', 'vision', 'planning', 'business model', 'market']):
            agents.append('strategy')
        
        # Finance agent for financial questions
        if any(word in question_lower for word in ['financial', 'finance', 'funding', 'investment', 'capex', 'opex', 'revenue']):
            agents.append('finance')
        
        # Construction agent for facility questions
        if any(word in question_lower for word in ['construction', 'facility', 'building', 'infrastructure', 'timeline']):
            agents.append('construction')
        
        # QMS agent for quality questions
        if any(word in question_lower for word in ['quality', 'qms', 'compliance', 'standards', 'certification']):
            agents.append('qms')
        
        # Governance agent for governance questions
        if any(word in question_lower for word in ['governance', 'management', 'leadership', 'organization']):
            agents.append('governance')
        
        # Regulation agent for regulatory questions
        if any(word in question_lower for word in ['regulation', 'regulatory', 'legal', 'cannabis', 'licensing']):
            agents.append('regulation')
        
        # IR agent for investor questions
        if any(word in question_lower for word in ['investor', 'investment', 'returns', 'business case', 'valuation']):
            agents.append('ir')
        
        # Default to strategy if no specific domain identified
        if not agents:
            agents = ['strategy']
        
        return agents
    
    async def process_single_agent_query(self, question: str, agent_type: str) -> Dict[str, Any]:
        """Process question with a single agent using full autonomy"""
        try:
            if not HAS_GHC_COMPLETE:
                raise RuntimeError(
                    "query_documents is unavailable – install 'ghc_complete' to enable document querying."
                )

            logger.info(f"🤖 {agent_type.upper()} Agent: Processing query with full autonomy")

            result = query_documents(question, agent_type, agent_type)

            # Log the analysis
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'agent': agent_type,
                'question': question,
                'autonomy_level': result.get('agent_autonomy', 'unknown'),
                'canonical_alignment': result.get('canonical_alignment', 'unknown'),
                'investigation_capabilities': result.get('investigation_capabilities', 'unknown'),
                'analysis_authority': result.get('analysis_authority', 'unknown'),
                'success': result.get('success', False),
                'response_length': len(result.get('documents', '')),
                'sources_count': len(result.get('sources', []))
            }

            self.session_log.append(log_entry)

            return {
                'agent': agent_type,
                'success': result.get('success', False),
                'analysis': result.get('documents', ''),
                'sources': result.get('sources', []),
                'autonomy_metadata': {
                    'autonomy_level': result.get('agent_autonomy', 'unknown'),
                    'canonical_alignment': result.get('canonical_alignment', 'unknown'),
                    'investigation_capabilities': result.get('investigation_capabilities', 'unknown'),
                    'analysis_authority': result.get('analysis_authority', 'unknown')
                }
            }

        except Exception as e:
            logger.error(f"❌ Error in {agent_type} agent: {e}")
            return {
                'agent': agent_type,
                'success': False,
                'analysis': f"Error in {agent_type} analysis: {e}",
                'sources': [],
                'autonomy_metadata': {'error': str(e)}
            }
    
    async def process_multi_agent_query(self, question: str, agent_types: List[str]) -> Dict[str, Any]:
        """Process question with multiple agents using full LangGraph system"""
        try:
            if not HAS_GHC_COMPLETE:
                raise RuntimeError(
                    "build_graph is unavailable – install 'ghc_complete' to enable multi-agent analysis."
                )

            logger.info(f"🔗 Multi-Agent Analysis: {', '.join(agent_types)} with full autonomy")

            complexity = self.analyze_question_complexity(question)

            # Create initial state
            initial_state = {
                'question': question,
                'messages': [],
                'current_agent': 'strategy',
                'analysis_depth': complexity,
                'investigation_log': []
            }

            # Run through complete LangGraph system
            final_state = self.graph.invoke(
                initial_state,
                {'configurable': {'thread_id': f'multi_agent_{datetime.now().isoformat()}'}}
            )

            # Log the multi-agent analysis
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'type': 'multi_agent',
                'agents': agent_types,
                'question': question,
                'complexity': complexity,
                'final_agent': final_state.get('current_agent', 'unknown'),
                'messages_generated': len(final_state.get('messages', [])),
                'investigation_entries': len(final_state.get('investigation_log', [])),
                'success': True
            }

            self.session_log.append(log_entry)

            return {
                'type': 'multi_agent',
                'agents': agent_types,
                'success': True,
                'complexity': complexity,
                'final_state': final_state,
                'messages': final_state.get('messages', []),
                'investigation_log': final_state.get('investigation_log', []),
                'final_agent': final_state.get('current_agent', 'unknown')
            }

        except Exception as e:
            logger.error(f"❌ Error in multi-agent analysis: {e}")
            return {
                'type': 'multi_agent',
                'agents': agent_types,
                'success': False,
                'error': str(e)
            }
    
    async def orchestrate(self, question: str, mode: str = 'auto') -> Dict[str, Any]:
        """
        Master orchestration method with full agent autonomy
        
        Args:
            question: The question to analyze
            mode: 'auto', 'single', 'multi', or specific agent name
            
        Returns:
            Comprehensive analysis results with autonomy metadata
        """
        start_time = datetime.now()
        logger.info(f"🎯 ORCHESTRATING: {question}")
        logger.info(f"🔬 Mode: {mode} | Full Agent Autonomy: ENABLED")
        
        try:
            # Determine routing strategy
            if mode == 'auto':
                # Automatic agent routing based on question analysis
                relevant_agents = self.determine_agent_routing(question)
                complexity = self.analyze_question_complexity(question)
                
                if len(relevant_agents) == 1 and complexity in ['basic', 'medium']:
                    # Single agent for simple questions
                    result = await self.process_single_agent_query(question, relevant_agents[0])
                else:
                    # Multi-agent for complex or cross-domain questions
                    result = await self.process_multi_agent_query(question, relevant_agents)
                    
            elif mode == 'single':
                # Single strategy agent analysis
                result = await self.process_single_agent_query(question, 'strategy')
                
            elif mode == 'multi':
                # Full multi-agent analysis
                all_agents = ['strategy', 'finance', 'construction', 'qms', 'governance', 'regulation', 'ir']
                result = await self.process_multi_agent_query(question, all_agents)
                
            elif mode in ['strategy', 'finance', 'construction', 'qms', 'governance', 'regulation', 'ir']:
                # Specific agent analysis
                result = await self.process_single_agent_query(question, mode)
                
            else:
                raise ValueError(f"Unknown orchestration mode: {mode}")
            
            # Add orchestration metadata
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            orchestration_result = {
                'orchestration': {
                    'question': question,
                    'mode': mode,
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'processing_time_seconds': processing_time,
                    'canonical_documents': '9_strategic_plans',
                    'agent_autonomy': 'full',
                    'system_status': 'operational'
                },
                'result': result,
                'session_log_entries': len(self.session_log)
            }
            
            logger.info(f"✅ ORCHESTRATION COMPLETE | Time: {processing_time:.2f}s | Success: {result.get('success', False)}")
            
            return orchestration_result
            
        except Exception as e:
            logger.error(f"❌ ORCHESTRATION FAILED: {e}")
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            return {
                'orchestration': {
                    'question': question,
                    'mode': mode,
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'processing_time_seconds': processing_time,
                    'canonical_documents': '9_strategic_plans',
                    'agent_autonomy': 'full',
                    'system_status': 'error'
                },
                'result': {
                    'success': False,
                    'error': str(e)
                },
                'session_log_entries': len(self.session_log)
            }
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of the current orchestration session"""
        if not self.session_log:
            return {'session_summary': 'No queries processed yet'}
        
        total_queries = len(self.session_log)
        successful_queries = sum(1 for log in self.session_log if log.get('success', False))
        
        agents_used = set()
        for log in self.session_log:
            if 'agent' in log:
                agents_used.add(log['agent'])
            elif 'agents' in log:
                agents_used.update(log['agents'])
        
        return {
            'session_summary': {
                'total_queries': total_queries,
                'successful_queries': successful_queries,
                'success_rate': f"{(successful_queries/total_queries)*100:.1f}%",
                'agents_used': list(agents_used),
                'canonical_documents': '9_strategic_plans',
                'agent_autonomy': 'full',
                'system_status': 'operational'
            },
            'recent_queries': self.session_log[-5:] if len(self.session_log) > 5 else self.session_log
        }

# Main orchestrator instance
orchestrator = GreenHillOrchestrator()

# Convenience functions for different use cases
async def quick_query(question: str) -> Dict[str, Any]:
    """Quick single-agent query for simple questions"""
    return await orchestrator.orchestrate(question, mode='single')

async def comprehensive_analysis(question: str) -> Dict[str, Any]:
    """Comprehensive multi-agent analysis for complex questions"""
    return await orchestrator.orchestrate(question, mode='multi')

async def auto_orchestrate(question: str) -> Dict[str, Any]:
    """Automatic orchestration with intelligent agent routing"""
    return await orchestrator.orchestrate(question, mode='auto')

async def agent_specific_query(question: str, agent: str) -> Dict[str, Any]:
    """Query specific agent with full autonomy"""
    return await orchestrator.orchestrate(question, mode=agent)

def main():
    """Main function for testing the orchestrator"""
    import asyncio
    
    async def test_orchestrator():
        print("🎯 GREEN HILL CANARIAS ORCHESTRATOR - CANONICAL SYSTEM")
        print("🔬 Testing Full Agent Autonomy with 9 Canonical Documents")
        print("=" * 80)
        
        # Test 1: Auto orchestration
        print("\n🤖 Test 1: Auto Orchestration")
        result1 = await auto_orchestrate(
            "What is the strategic vision for Green Hill Canarias and how does it align with financial projections?"
        )
        print(f"Success: {result1['result'].get('success', False)}")
        
        # Test 2: Comprehensive analysis
        print("\n🔗 Test 2: Comprehensive Multi-Agent Analysis")
        result2 = await comprehensive_analysis(
            "Provide a complete analysis of the Green Hill Canarias project including all aspects"
        )
        print(f"Success: {result2['result'].get('success', False)}")
        
        # Test 3: Agent-specific query
        print("\n🎯 Test 3: Finance Agent Specific Query")
        result3 = await agent_specific_query(
            "What are the detailed financial projections and funding requirements?",
            "finance"
        )
        print(f"Success: {result3['result'].get('success', False)}")
        
        # Session summary
        print("\n📊 Session Summary:")
        summary = orchestrator.get_session_summary()
        print(f"Total queries: {summary['session_summary']['total_queries']}")
        print(f"Success rate: {summary['session_summary']['success_rate']}")
        print(f"Agents used: {summary['session_summary']['agents_used']}")
        
        print("\n🏆 ORCHESTRATOR TEST COMPLETE")
    
    asyncio.run(test_orchestrator())

if __name__ == "__main__":
    main()
