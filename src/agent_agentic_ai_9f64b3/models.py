from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, Optional
from uuid import uuid4, UUID
from datetime import datetime
from enum import Enum

class AgentStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskEvent(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    task_id: UUID = Field(default_factory=uuid4)
    agent_id: str
    payload: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    priority: int = Field(default=0, ge=0, le=10)

class AgentState(BaseModel):
    agent_id: str
    status: AgentStatus
    last_update: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)