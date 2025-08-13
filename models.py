"""
Models for Green Hill Canarias Agent System
Defines State, Message and AgentName classes per specification
"""

from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum


class AgentName(str, Enum):
    """Agent names in the Green Hill Canarias system"""
    strategy = "Strategy"
    finance = "Finance"
    construction = "Construction"
    qms = "QMS"
    governance = "Governance"
    regulation = "Regulation"
    ir = "IR"

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"AgentName.{self.name}"


class Message(BaseModel):
    """Message structure for agent communication"""
    role: str = Field(description="Message sender role")
    content: str = Field(description="Message content")


class State(BaseModel):
    """Global state object for the Green Hill Canarias system"""
    question: str = Field(..., description="Business task or question")
    context: Dict = Field(default_factory=dict, description="Context information")
    history: List[Message] = Field(default_factory=list, description="Message history")
    notes: List[str] = Field(default_factory=list, description="Agent notes")
    plan: Optional[Dict] = Field(None, description="Strategic plan")
    financials: Optional[Dict] = Field(None, description="Financial data")
    schedule: Optional[Dict] = Field(None, description="Construction schedule")
    capex_breakdown: Optional[Dict] = Field(None, description="CAPEX breakdown")
    quality_gaps: Optional[List[str]] = Field(None, description="Quality gaps")
    controls: Optional[Dict] = Field(None, description="Control systems")
    decision_log: Optional[List[Dict]] = Field(None, description="Decision log")
    owners: Optional[Dict] = Field(None, description="Responsibility owners")
    regulatory_actions: Optional[List[Dict]] = Field(None, description="Regulatory actions")
    memo: Optional[str] = Field(None, description="Investor memo")
    deck_outline: Optional[List[str]] = Field(None, description="Presentation outline")
    current_agent: Optional[AgentName] = Field(None, description="Current agent")
    next_agent: Optional[AgentName] = Field(None, description="Next agent")
    finalize: bool = Field(False, description="Finalization flag")
    decisions: List[Dict] = Field(default_factory=list, description="Decisions made")
    final_answer: Optional[str] = Field(None, description="Final answer")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    sources_used: List[str] = Field(default_factory=list, description="Sources used")
    processing_mode: str = Field("comprehensive", description="Processing mode")

    class Config:
        """Pydantic configuration"""
        arbitrary_types_allowed = True
    content: str = Field(description="Message content")

    def __str__(self) -> str:
        return f"{self.role}: {self.content[:100]}..."

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
