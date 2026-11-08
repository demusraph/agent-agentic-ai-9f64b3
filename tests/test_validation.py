import unittest
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import ValidationError
from src.agent_agentic_ai_9f64b3.models import TaskEvent, AgentStatus, AgentState

class TestValidation(unittest.TestCase):
    """Exhaustive validation suite for Agentic AI data models."""

    def test_task_event_valid_creation(self):
        """Test successful instantiation of TaskEvent with valid data."""
        data = {
            "agent_id": "test-agent-001",
            "payload": {"action": "compute", "value": 42},
            "priority": 5
        }
        event = TaskEvent(**data)
        self.assertEqual(event.agent_id, "test-agent-001")
        self.assertEqual(event.priority, 5)
        self.assertIsInstance(event.task_id, UUID)
        self.assertIsInstance(event.created_at, datetime)

    def test_task_event_missing_required_fields(self):
        """Test that missing required fields raises ValidationError."""
        with self.assertRaises(ValidationError):
            TaskEvent(payload={})  # agent_id is missing

    def test_task_event_priority_too_high(self):
        """Test that priority > 10 raises ValidationError."""
        with self.assertRaises(ValidationError):
            TaskEvent(agent_id="a1", payload={}, priority=11)

    def test_task_event_priority_negative(self):
        """Test that negative priority raises ValidationError."""
        with self.assertRaises(ValidationError):
            TaskEvent(agent_id="a1", payload={}, priority=-1)

    def test_task_event_immutability(self):
        """Test that TaskEvent is frozen (model_config frozen=True)."""
        event = TaskEvent(agent_id="a1", payload={})
        with self.assertRaises(Exception):
            event.agent_id = "hacked"

    def test_agent_state_valid_transition(self):
        """Test AgentState initialization and status enum."""
        state = AgentState(agent_id="worker-1", status=AgentStatus.PENDING)
        self.assertEqual(state.status, AgentStatus.PENDING)
        
        state.status = AgentStatus.RUNNING
        self.assertEqual(state.status, "running")

    def test_agent_state_invalid_status(self):
        """Test that invalid status string raises ValidationError."""
        with self.assertRaises(ValidationError):
            AgentState(agent_id="w1", status="invalid_status")

    def test_task_event_payload_flexibility(self):
        """Test that payload accepts various dictionary structures."""
        complex_payload = {"nested": {"list": [1, 2, 3]}, "flag": True}
        event = TaskEvent(agent_id="a1", payload=complex_payload)
        self.assertEqual(event.payload["nested"]["list"], [1, 2, 3])
        self.assertTrue(event.payload["flag"])

    def test_task_event_uuid_generation(self):
        """Test that task_id is auto-generated if not provided."""
        event1 = TaskEvent(agent_id="a1", payload={})
        event2 = TaskEvent(agent_id="a1", payload={})
        self.assertNotEqual(event1.task_id, event2.task_id)

    def test_agent_state_metadata_default(self):
        """Test that metadata defaults to an empty dictionary."""
        state = AgentState(agent_id="a1", status=AgentStatus.PENDING)
        self.assertEqual(state.metadata, {})
        
        state.metadata["key"] = "value"
        self.assertEqual(state.metadata["key"], "value")

if __name__ == "__main__":
    unittest.main()