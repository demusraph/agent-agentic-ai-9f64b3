import asyncio
import logging
from typing import Dict, Type, Optional
from abc import ABC, abstractmethod
from .models import TaskEvent, AgentStatus, AgentState

logger = logging.getLogger("agentic_ai")

class EventBus:
    """High-throughput in-memory event dispatcher."""
    def __init__(self, maxsize: int = 1000):
        self._queue: asyncio.Queue[TaskEvent] = asyncio.Queue(maxsize=maxsize)
        self._registry: Dict[str, "BaseAgent"] = {}

    async def publish(self, event: TaskEvent):
        await self._queue.put(event)

    def register_agent(self, agent_id: str, agent: "BaseAgent"):
        self._registry[agent_id] = agent

    async def run_worker(self):
        while True:
            event = await self._queue.get()
            try:
                agent = self._registry.get(event.agent_id)
                if agent:
                    await agent.execute(event)
                else:
                    logger.error(f"No agent registered for {event.agent_id}")
            except Exception as e:
                logger.error(f"Worker error: {e}")
            finally:
                self._queue.task_done()

class BaseAgent(ABC):
    """Abstract base class for all autonomous agents."""
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.state = AgentState(agent_id=agent_id, status=AgentStatus.PENDING)

    @abstractmethod
    async def execute(self, event: TaskEvent) -> None:
        """Core logic implementation for the agent."""
        pass

    def update_state(self, status: AgentStatus, **kwargs):
        self.state.status = status
        self.state.metadata.update(kwargs)
        logger.info(f"Agent {self.agent_id} transitioned to {status}")