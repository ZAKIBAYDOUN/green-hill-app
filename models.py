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
    
    # Agent artifacts
    plan: Optional[Dict[str, Any]] = Field(default=None, description="Strategic plan")
    financials: Optional[Dict[str, Any]] = Field(default=None, description="Financial analysis")
    schedule: Optional[Dict[str, Any]] = Field(default=None, description="Construction schedule")
    capex_breakdown: Optional[Dict[str, Any]] = Field(default=None, description="CAPEX breakdown")
    
    # QMS and Governance
    quality_gaps: Optional[List[str]] = Field(default=None, description="Quality gaps identified")
    controls: Optional[Dict[str, Any]] = Field(default=None, description="Quality controls")
    decision_log: Optional[List[Dict[str, Any]]] = Field(default=None, description="Decision log")
    owners: Optional[Dict[str, Any]] = Field(default=None, description="Decision owners")
    
    # Regulation and IR
    regulatory_actions: Optional[List[Dict[str, Any]]] = Field(default=None, description="Regulatory actions")
    memo: Optional[str] = Field(default=None, description="Internal memo")
    deck_outline: Optional[List[str]] = Field(default=None, description="Presentation outline")
    
    # Flow control
    current_agent: Optional[AgentName] = Field(default=None, description="Current agent")
    next_agent: Optional[AgentName] = Field(default=None, description="Next agent")
    processing_mode: str = Field(default="standard", description="Processing mode: standard, fast, or detailed")
    finalize: bool = Field(default=False, description="Finalization flag")
    
    # Outputs and tracking
    decisions: List[Dict[str, Any]] = Field(default_factory=list, description="All decisions made")
    sources_used: List[str] = Field(default_factory=list, description="Document sources used")
    final_answer: Optional[str] = Field(default=None, description="Final comprehensive answer")
    errors: List[str] = Field(default_factory=list, description="Errors encountered")
    
    # Legacy compatibility
    messages: List[Dict] = Field(default_factory=list, description="Legacy message list")
    analysis_depth: str = Field(default="medium", description="Analysis depth level")
    investigation_log: List[Dict] = Field(default_factory=list, description="Investigation log")

    def __str__(self) -> str:
        agent_info = f"Agent: {self.current_agent}" if self.current_agent else "No agent"
        status = "Finalized" if self.finalize else "In progress"
        return f"State({agent_info}, {status}, {len(self.errors)} errors)"

    def __repr__(self) -> str:
        return (f"State(question='{self.question[:30]}...', "
                f"current_agent={self.current_agent}, "
                f"finalize={self.finalize})")

    class Config:
        """Pydantic configuration"""
        use_enum_values = True
        arbitrary_types_allowed = True
        json_encoders = {
            AgentName: lambda v: v.value if v else None
        }