# app/models.py
from typing import Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field

class AgentName(str, Enum):
    STRATEGY = "Strategy"
    OPERATIONS = "Operations" 
    FINANCE = "Finance"
    MARKET_INTEL = "MarketIntel"
    RISK = "Risk"
    COMPLIANCE = "Compliance"
    INNOVATION = "Innovation"

class Message(BaseModel):
    role: str
    content: str

class TwinState(BaseModel):
    question: str = Field(..., description="User's question or task")
    context: Dict = Field(default_factory=dict, description="Global context")
    history: List[Message] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)
    
    # Outputs for each agent
    strategy_output: Optional[str] = None
    operations_output: Optional[str] = None
    finance_output: Optional[str] = None
    market_output: Optional[str] = None
    risk_output: Optional[str] = None
    compliance_output: Optional[str] = None
    innovation_output: Optional[str] = None
    
    # Control flags
    current_agent: Optional[AgentName] = None
    next_agent: Optional[AgentName] = None
    finalize: bool = False
    final_answer: Optional[str] = None
    errors: List[str] = Field(default_factory=list)
    
    class Config:
        # Allow dict-like access for LangGraph compatibility
        extra = "allow"
        arbitrary_types_allowed = True
    
    def to_dict(self) -> dict:
        """Convert to dict for LangGraph state"""
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, data: dict) -> "TwinState":
        """Create from dict for LangGraph state"""
        return cls(**data)
