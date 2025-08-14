"""
Models for Green Hill Canarias Agent System
Defines State, Message and AgentName classes per GPT-5 Pro specification
"""

from typing import Dict, List, Any, Optional, Union, Annotated
from pydantic import BaseModel, Field
from enum import Enum
from langgraph.graph.message import add_messages


class AgentName(str, Enum):
    """Agent names in the Green Hill Canarias system"""
    strategy = "Strategy"
    operations = "Operations"
    finance = "Finance"
    market = "Market"
    risk = "Risk"
    compliance = "Compliance"
    innovation = "Innovation"
    green_hill = "GreenHillGPT"

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"AgentName.{self.name}"


# LangGraph compatible state
class AgentState(BaseModel):
    """State for LangGraph agents"""
    messages: Annotated[list, add_messages] = Field(default_factory=list)
    agent_type: Optional[str] = None
    context_used: Optional[int] = None
    
    class Config:
        arbitrary_types_allowed = True


class Message(BaseModel):
    """Message structure for agent communication"""
    role: str = Field(description="Message sender role")
    content: str = Field(description="Message content")

    def __str__(self) -> str:
        return f"{self.role}: {self.content[:100]}..."


class TwinState(BaseModel):
    """State for Green Hill Canarias Digital Twin"""
    # Make question optional to avoid validation errors when callers omit it
    question: Optional[str] = Field(default=None, description="User query or business task")
    context: Dict = Field(default_factory=dict)
    history: List[Message] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)

    # Audience / intake metadata (role-aware routing)
    source_type: Optional[str] = Field(default=None, description="Requester role: master|shareholder|investor|supplier|provider|public")
    source_id: Optional[str] = Field(default=None, description="Optional requester identifier")
    priority: str = Field(default="normal", description="Priority: high|normal|low")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for routing/audit")

    # Agent outputs (optional at start)
    strategy_output: Optional[Dict] = None
    operations_output: Optional[Dict] = None
    finance_output: Optional[Dict] = None
    market_output: Optional[Dict] = None
    risk_output: Optional[Dict] = None
    compliance_output: Optional[Dict] = None
    innovation_output: Optional[Dict] = None
    green_hill_response: Optional[Dict] = None

    # Flow control
    current_agent: Optional[AgentName] = None
    next_agent: Optional[AgentName] = None
    orchestration_mode: str = Field(default="ceo", description="Routing mode: 'ceo' or 'direct'")
    target_agent: Optional[AgentName] = Field(default=None, description="Direct mode target agent")
    finalize: bool = False

    # Feedback channel to CEO/orchestrator from agents
    ceo_feedbacks: List[Dict[str, Any]] = Field(default_factory=list)

    # Final output / error fields
    final_answer: Optional[str] = None
    errors: List[str] = Field(default_factory=list)

    class Config:
        """Pydantic configuration"""
        arbitrary_types_allowed = True


# Legacy State for backward compatibility
class State(TwinState):
    """Legacy state - kept for compatibility"""
    pass

    def __repr__(self) -> str:
        return f"Message(role='{self.role}', content='{self.content[:50]}...')"


class State(BaseModel):
    """Comprehensive state for Green Hill Canarias agent system"""
    
    # Primary input
    question: str = Field(default="", description="Main question or query")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    
    # Communication and history
    history: List[Message] = Field(default_factory=list, description="Message history")
    notes: List[str] = Field(default_factory=list, description="Notes and observations")
    
    # Intermediate artifacts
    plan: Optional[Dict] = None
    financials: Optional[Dict] = None
    schedule: Optional[Dict] = None
    capex_breakdown: Optional[Dict] = None
    quality_gaps: Optional[List[str]] = None
    controls: Optional[Dict] = None
    decision_log: Optional[List[Dict]] = None
    owners: Optional[Dict] = None
    regulatory_actions: Optional[List[Dict]] = None
    memo: Optional[str] = None
    deck_outline: Optional[List[str]] = None
    
    # Flow control
    current_agent: Optional[AgentName] = None
    next_agent: Optional[AgentName] = None
    finalize: bool = False
    
    # Final result & errors  
    decisions: List[Dict] = Field(default_factory=list)
    final_answer: Optional[str] = None
    errors: List[str] = Field(default_factory=list)
    
    # Legacy compatibility
    messages: List[Dict] = Field(default_factory=list)
    analysis_depth: str = "medium"
    investigation_log: List[Dict] = Field(default_factory=list)
    # Artefactos de agentes
    plan: Optional[Dict[str, Any]] = Field(default=None, description="Plan estratégico")
    financials: Optional[Dict[str, Any]] = Field(default=None, description="Análisis financiero")
    schedule: Optional[Dict[str, Any]] = Field(default=None, description="Cronograma de construcción")
    capex_breakdown: Optional[Dict[str, Any]] = Field(default=None, description="Desglose CAPEX")
    
    # QMS y Gobernanza
    quality_gaps: Optional[List[str]] = Field(default=None, description="Brechas de calidad identificadas")
    controls: Optional[Dict[str, Any]] = Field(default=None, description="Controles de calidad")
    decision_log: Optional[List[Dict[str, Any]]] = Field(default=None, description="Registro de decisiones")
    owners: Optional[Dict[str, Any]] = Field(default=None, description="Propietarios de decisiones")
    
    # Regulación e IR
    regulatory_actions: Optional[List[Dict[str, Any]]] = Field(default=None, description="Acciones regulatorias")
    memo: Optional[str] = Field(default=None, description="Memo interno")
    deck_outline: Optional[List[str]] = Field(default=None, description="Esquema de presentación")
    
    # Control de flujo
    current_agent: Optional[AgentName] = Field(default=None, description="Agente actual")
    next_agent: Optional[AgentName] = Field(default=None, description="Siguiente agente")
    processing_mode: str = Field(default="standard", description="Modo de procesamiento: standard, fast, or detailed")
    finalize: bool = Field(default=False, description="Bandera de finalización")
    
    # Salidas y tracking
    decisions: List[Dict[str, Any]] = Field(default_factory=list, description="Todas las decisiones tomadas")
    sources_used: List[str] = Field(default_factory=list, description="Fuentes de documentos utilizadas")
    final_answer: Optional[str] = Field(default=None, description="Respuesta final comprehensive")
    errors: List[str] = Field(default_factory=list, description="Errores encontrados")

    def __str__(self) -> str:
        agent_info = f"Agent: {self.current_agent}" if self.current_agent else "No agent"
        status = "Finalized" if self.finalize else "In progress"
        return f"State({agent_info}, {status}, {len(self.errors)} errors)"

    def __repr__(self) -> str:
        return (f"State(question='{self.question[:30]}...', "
                f"current_agent={self.current_agent}, "
                f"finalize={self.finalize})")

    class Config:
        """Configuración de Pydantic"""
        use_enum_values = True
        arbitrary_types_allowed = True
        json_encoders = {
            AgentName: lambda v: v.value if v else None
        }
