import unittest
import asyncio
from uuid import uuid4
from datetime import datetime
from pydantic import ValidationError
from src.agent_agentic_ai_9f64b3.models import TaskEvent
from src.agent_agentic_ai_9f64b3.core import EventBus, BaseAgent, AgentStatus

class MockAgent(BaseAgent):
    async def execute(self, event: TaskEvent) -> None:
        self.update_state(AgentStatus.COMPLETED)

class TestBoundaries(unittest.TestCase):
    def setUp(self):
        self.bus = EventBus(maxsize=5)

    def test_priority_lower_boundary(self):
        """Test priority at the minimum allowed value (0)."""
        event = TaskEvent(agent_id="test", payload={"data": 1}, priority=0)
        self.assertEqual(event.priority, 0)

    def test_priority_upper_boundary(self):
        """Test priority at the maximum allowed value (10)."""
        event = TaskEvent(agent_id="test", payload={"data": 1}, priority=10)
        self.assertEqual(event.priority, 10)

    def test_priority_out_of_bounds_negative(self):
        """Test that negative priority raises ValidationError."""
        with self.assertRaises(ValidationError):
            TaskEvent(agent_id="test", payload={}, priority=-1)

    def test_priority_out_of_bounds_high(self):
        """Test that priority > 10 raises ValidationError."""
        with self.assertRaises(ValidationError):
            TaskEvent(agent_id="test", payload={}, priority=11)

    def test_event_bus_capacity_limit(self):
        """Test event bus behavior at max capacity."""
        async def run_test():
            for i in range(5):
                await self.bus.publish(TaskEvent(agent_id="a", payload={}))
            self.assertTrue(self.bus._queue.full())
        asyncio.run(run_test())

    def test_empty_payload_handling(self):
        """Test task creation with empty dictionary payload."""
        event = TaskEvent(agent_id="test", payload={})
        self.assertEqual(event.payload, {})

    def test_identical_agent_registration(self):
        """Test overwriting an agent in the registry."""
        agent1 = MockAgent("id1")
        agent2 = MockAgent("id1")
        self.bus.register_agent("id1", agent1)
        self.bus.register_agent("id1", agent2)
        self.assertEqual(self.bus._registry["id1"], agent2)

    def test_non_existent_agent_execution(self):
        """Test worker behavior when agent is not registered."""
        event = TaskEvent(agent_id="ghost", payload={})
        # Should not raise exception, handled by try-except in worker
        async def run_test():
            await self.bus.publish(event)
            await self.bus.run_worker()
        # We use a timeout to break the infinite loop
        try:
            asyncio.wait_for(run_test(), timeout=0.1)
        except asyncio.TimeoutError:
            pass

    def test_agent_state_transition(self):
        """Test state transition logic with metadata."""
        agent = MockAgent("test")
        agent.update_state(AgentStatus.RUNNING, progress=50)
        self.assertEqual(agent.state.status, AgentStatus.RUNNING)
        self.assertEqual(agent.state.metadata["progress"], 50)

    def test_uuid_uniqueness(self):
        """Test that TaskEvent generates unique IDs by default."""
        e1 = TaskEvent(agent_id="a", payload={})
        e2 = TaskEvent(agent_id="a", payload={})
        self.assertNotEqual(e1.task_id, e2.task_id)

if __name__ == "__main__":
    unittest.main()