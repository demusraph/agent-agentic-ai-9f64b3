import unittest
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any

from agent_agentic_ai_9f64b3.models import TaskEvent, AgentStatus, AgentState
from agent_agentic_ai_9f64b3.core import EventBus, BaseAgent

class MockAgent(BaseAgent):
    def __init__(self, agent_id: str):
        super().__init__(agent_id)
        self.processed_events = []

    async def execute(self, event: TaskEvent) -> None:
        self.processed_events.append(event)
        self.update_state(AgentStatus.COMPLETED, last_task=str(event.task_id))

class TestCoreEngine(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.bus = EventBus(maxsize=10)

    def test_task_event_creation(self):
        """Verify TaskEvent model initialization and constraints."""
        event = TaskEvent(agent_id="test_agent", payload={"key": "value"}, priority=5)
        self.assertEqual(event.agent_id, "test_agent")
        self.assertEqual(event.payload["key"], "value")
        self.assertEqual(event.priority, 5)
        self.assertIsInstance(event.task_id, uuid.UUID)

    def test_agent_state_initialization(self):
        """Verify BaseAgent state defaults."""
        agent = MockAgent("agent_001")
        self.assertEqual(agent.state.status, AgentStatus.PENDING)
        self.assertEqual(agent.state.agent_id, "agent_001")

    async def test_event_bus_registration(self):
        """Verify agent registration in EventBus."""
        agent = MockAgent("agent_001")
        self.bus.register_agent("agent_001", agent)
        self.assertIn("agent_001", self.bus._registry)
        self.assertEqual(self.bus._registry["agent_001"], agent)

    async def test_event_dispatch_and_processing(self):
        """Verify end-to-end event dispatching to a registered agent."""
        agent = MockAgent("agent_001")
        self.bus.register_agent("agent_001", agent)
        
        event = TaskEvent(agent_id="agent_001", payload={"cmd": "run"})
        await self.bus.publish(event)
        
        # Run worker for one iteration
        task = asyncio.create_task(self.bus.run_worker())
        await asyncio.sleep(0.1)
        
        self.assertEqual(len(agent.processed_events), 1)
        self.assertEqual(agent.processed_events[0].task_id, event.task_id)
        self.assertEqual(agent.state.status, AgentStatus.COMPLETED)
        task.cancel()

    def test_task_event_priority_validation(self):
        """Verify Pydantic validation for priority constraints."""
        with self.assertRaises(ValueError):
            TaskEvent(agent_id="a", payload={}, priority=11)
        with self.assertRaises(ValueError):
            TaskEvent(agent_id="a", payload={}, priority=-1)

    def test_agent_state_transition(self):
        """Verify state transition logic in BaseAgent."""
        agent = MockAgent("agent_001")
        agent.update_state(AgentStatus.RUNNING, progress=50)
        self.assertEqual(agent.state.status, AgentStatus.RUNNING)
        self.assertEqual(agent.state.metadata["progress"], 50)

    async def test_event_bus_queue_full(self):
        """Verify EventBus handles maxsize correctly."""
        bus = EventBus(maxsize=1)
        await bus.publish(TaskEvent(agent_id="a", payload={}))
        # This should not block if we don't await it, but we test the queue size
        self.assertEqual(bus._queue.qsize(), 1)

    def test_uuid_uniqueness(self):
        """Verify task IDs are unique."""
        e1 = TaskEvent(agent_id="a", payload={})
        e2 = TaskEvent(agent_id="a", payload={})
        self.assertNotEqual(e1.task_id, e2.task_id)

    async def test_worker_error_handling(self):
        """Verify worker continues even if an agent fails."""
        class FailingAgent(BaseAgent):
            async def execute(self, event):
                raise ValueError("Simulated failure")
        
        agent = FailingAgent("fail_agent")
        self.bus.register_agent("fail_agent", agent)
        await self.bus.publish(TaskEvent(agent_id="fail_agent", payload={}))
        
        task = asyncio.create_task(self.bus.run_worker())
        await asyncio.sleep(0.1)
        self.assertEqual(self.bus._queue.qsize(), 0)
        task.cancel()

    def test_agent_metadata_persistence(self):
        """Verify metadata dictionary updates correctly."""
        agent = MockAgent("agent_001")
        agent.update_state(AgentStatus.RUNNING, key1="val1")
        agent.update_state(AgentStatus.RUNNING, key2="val2")
        self.assertEqual(agent.state.metadata["key1"], "val1")
        self.assertEqual(agent.state.metadata["key2"], "val2")