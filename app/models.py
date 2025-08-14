from typing import Dict, List, Optional, Literal
from enum import Enum
from pydantic import BaseModel, Field


class AgentName(str, Enum):
    STRATEGY = "strategy"
    OPERATIONS = "operations"
    FINANCE = "finance"
    MARKET = "market"
    RISK = "risk"
    COMPLIANCE = "compliance"
    INNOVATION = "innovation"
    GREEN_HILL = "green_hill_gpt"


class Message(BaseModel):
    role: str
    content: str


class TwinState(BaseModel):
    # Who/what asked the question
    source_type: Literal[
        "master","shareholder","investor","supplier","provider","public",
        "ocs_feed","web_source","media_upload"
    ] = "public"
    origin: Optional[str] = None
    source_id: Optional[str] = None

    # What is being asked or submitted
    question: Optional[str] = None
    content_type: Optional[Literal["text","structured_data","binary","mixed"]] = None
    payload_ref: Optional[str] = None

    # Meta
    priority: Literal["high","normal","low"] = "normal"
    timestamp: Optional[str] = None
    related_docs: List[str] = []

    # Context and history
    context: Dict = Field(default_factory=dict)
    history: List[Message] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)

    # Derived classification and next routing
    target_agents: List[AgentName] = []
    current_agent: Optional[AgentName] = None
    next_agent: Optional[AgentName] = None
    finalize: bool = False

    # Agents’ outputs
    strategy_output: Optional[Dict] = None
    operations_output: Optional[Dict] = None
    finance_output: Optional[Dict] = None
    market_output: Optional[Dict] = None
    risk_output: Optional[Dict] = None
    compliance_output: Optional[Dict] = None
    innovation_output: Optional[Dict] = None
    green_hill_response: Optional[Dict] = None

    # Final answer and errors
    final_answer: Optional[str] = None
    errors: List[str] = []

    class Config:
        extra = "allow"
        arbitrary_types_allowed = True
