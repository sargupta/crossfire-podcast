"""
Tests for Managed Session Service
Tests session creation, context management, and archival
"""

import pytest
import asyncio
from pathlib import Path
import sys
import json
import os
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent))

from managed_session_service import (  # noqa: E402
    ManagedSessionService,
    DebateContext,
)


class TestDebateContext:
    """Test DebateContext dataclass"""

    def test_debate_context_creation(self):
        """Test creating debate context"""
        context = DebateContext(
            session_id="test123",
            topic="Test Topic",
            current_turn=0,
            debate_history=[],
            participants=["agent1", "agent2"],
            created_at="2024-01-01T00:00:00",
            updated_at="2024-01-01T00:00:00",
            metadata={"key": "value"},
        )

        assert context.session_id == "test123"
        assert context.topic == "Test Topic"
        assert context.current_turn == 0
        assert len(context.debate_history) == 0
        assert len(context.participants) == 2


class TestManagedSessionService:
    """Test managed session service"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        return ManagedSessionService(project_id="test-project")

    @pytest.fixture(autouse=True)
    def cleanup_sessions(self):
        """Cleanup sessions directory after each test"""
        yield
        if os.path.exists("sessions"):
            shutil.rmtree("sessions")

    def test_service_initialization(self, service):
        """Test service initializes correctly"""
        assert service.project_id == "test-project"
        assert service.location == "us-central1"
        assert service.sessions == {}

    def test_service_custom_location(self):
        """Test service with custom location"""
        service = ManagedSessionService(
            project_id="test", location="europe-west1"
        )
        assert service.location == "europe-west1"

    @pytest.mark.asyncio
    async def test_create_session_basic(self, service):
        """Test creating a basic session"""
        context = await service.create_session(topic="Test Topic")

        assert context.session_id.startswith("debate_")
        assert context.topic == "Test Topic"
        assert context.current_turn == 0
        assert len(context.debate_history) == 0
        assert len(context.participants) == 5  # Default participants
        assert "shakti" in context.participants

    @pytest.mark.asyncio
    async def test_create_session_custom_participants(self, service):
        """Test creating session with custom participants"""
        participants = ["agent1", "agent2", "agent3"]
        context = await service.create_session(
            topic="Custom Topic", participants=participants
        )

        assert context.participants == participants
        assert len(context.participants) == 3

    @pytest.mark.asyncio
    async def test_create_session_stores_in_sessions(self, service):
        """Test that created session is stored"""
        context = await service.create_session(topic="Test")

        assert context.session_id in service.sessions
        assert service.sessions[context.session_id] == context

    @pytest.mark.asyncio
    async def test_get_session_exists(self, service):
        """Test getting existing session"""
        created = await service.create_session(topic="Test")
        retrieved = await service.get_session(created.session_id)

        assert retrieved == created
        assert retrieved.session_id == created.session_id

    @pytest.mark.asyncio
    async def test_get_session_not_exists(self, service):
        """Test getting non-existent session"""
        result = await service.get_session("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_update_context_basic(self, service):
        """Test updating session context"""
        session = await service.create_session(topic="Test")

        turn_data = {"speaker": "shakti", "text": "Hello", "turn": 1}

        updated = await service.update_context(session.session_id, turn_data)

        assert updated.current_turn == 1
        assert len(updated.debate_history) == 1
        assert updated.debate_history[0]["speaker"] == "shakti"
        assert updated.debate_history[0]["text"] == "Hello"
        assert "timestamp" in updated.debate_history[0]

    @pytest.mark.asyncio
    async def test_update_context_multiple_turns(self, service):
        """Test updating with multiple turns"""
        session = await service.create_session(topic="Test")

        await service.update_context(
            session.session_id, {"speaker": "agent1", "text": "Turn 1", "turn": 1}
        )
        await service.update_context(
            session.session_id, {"speaker": "agent2", "text": "Turn 2", "turn": 2}
        )

        updated = await service.get_session(session.session_id)
        assert updated.current_turn == 2
        assert len(updated.debate_history) == 2

    @pytest.mark.asyncio
    async def test_update_context_with_quality_scores(self, service):
        """Test updating with quality scores"""
        session = await service.create_session(topic="Test")

        turn_data = {
            "speaker": "agent1",
            "text": "Response",
            "turn": 1,
            "quality_scores": {"coherence": 0.95, "safety": 0.92},
        }

        await service.update_context(session.session_id, turn_data)

        updated = await service.get_session(session.session_id)
        assert "quality_scores" in updated.debate_history[0]
        assert updated.debate_history[0]["quality_scores"]["coherence"] == 0.95

    @pytest.mark.asyncio
    async def test_update_context_invalid_session(self, service):
        """Test updating non-existent session raises error"""
        with pytest.raises(ValueError, match="Session not found"):
            await service.update_context(
                "invalid_id", {"speaker": "test", "text": "test", "turn": 1}
            )

    @pytest.mark.asyncio
    async def test_get_history_full(self, service):
        """Test getting full history"""
        session = await service.create_session(topic="Test")

        await service.update_context(
            session.session_id, {"speaker": "a1", "text": "T1", "turn": 1}
        )
        await service.update_context(
            session.session_id, {"speaker": "a2", "text": "T2", "turn": 2}
        )

        history = await service.get_history(session.session_id)

        assert len(history) == 2
        assert history[0]["speaker"] == "a1"
        assert history[1]["speaker"] == "a2"

    @pytest.mark.asyncio
    async def test_get_history_last_n(self, service):
        """Test getting last N turns"""
        session = await service.create_session(topic="Test")

        for i in range(5):
            await service.update_context(
                session.session_id,
                {"speaker": f"agent{i}", "text": f"Turn {i}", "turn": i},
            )

        history = await service.get_history(session.session_id, last_n=2)

        assert len(history) == 2
        assert history[0]["speaker"] == "agent3"
        assert history[1]["speaker"] == "agent4"

    @pytest.mark.asyncio
    async def test_get_history_invalid_session(self, service):
        """Test getting history for non-existent session"""
        history = await service.get_history("invalid")
        assert history == []

    @pytest.mark.asyncio
    async def test_close_session_success(self, service):
        """Test closing session successfully"""
        session = await service.create_session(topic="Test")
        await service.update_context(
            session.session_id, {"speaker": "test", "text": "test", "turn": 1}
        )

        result = await service.close_session(session.session_id)

        assert result["status"] == "closed"
        assert result["session_id"] == session.session_id
        assert result["total_turns"] == 1
        assert "archive_file" in result

        # Verify session removed from active sessions
        assert session.session_id not in service.sessions

        # Verify archive file created
        assert os.path.exists(result["archive_file"])

    @pytest.mark.asyncio
    async def test_close_session_creates_archive(self, service):
        """Test that closing session creates valid archive file"""
        session = await service.create_session(topic="Archive Test")
        await service.update_context(
            session.session_id, {"speaker": "test", "text": "test", "turn": 1}
        )

        result = await service.close_session(session.session_id)

        # Read and verify archive
        with open(result["archive_file"], "r") as f:
            archived_data = json.load(f)

        assert archived_data["session_id"] == session.session_id
        assert archived_data["topic"] == "Archive Test"
        assert len(archived_data["debate_history"]) == 1

    @pytest.mark.asyncio
    async def test_close_session_not_found(self, service):
        """Test closing non-existent session"""
        result = await service.close_session("nonexistent")
        assert result["status"] == "not_found"

    def test_format_history_for_prompt_basic(self, service):
        """Test formatting history for prompts"""
        # Create session synchronously for this test
        session_id = "test_session"
        service.sessions[session_id] = DebateContext(
            session_id=session_id,
            topic="Test",
            current_turn=2,
            debate_history=[
                {"speaker": "shakti", "text": "Welcome!"},
                {"speaker": "agent1", "text": "My point!"},
            ],
            participants=["shakti", "agent1"],
            created_at="2024-01-01",
            updated_at="2024-01-01",
        )

        formatted = service.format_history_for_prompt(session_id)

        assert "shakti: Welcome!" in formatted
        assert "agent1: My point!" in formatted

    def test_format_history_for_prompt_last_n(self, service):
        """Test formatting with last_n parameter"""
        session_id = "test_session"
        service.sessions[session_id] = DebateContext(
            session_id=session_id,
            topic="Test",
            current_turn=5,
            debate_history=[
                {"speaker": "a1", "text": "T1"},
                {"speaker": "a2", "text": "T2"},
                {"speaker": "a3", "text": "T3"},
                {"speaker": "a4", "text": "T4"},
                {"speaker": "a5", "text": "T5"},
            ],
            participants=["a1", "a2", "a3", "a4", "a5"],
            created_at="2024-01-01",
            updated_at="2024-01-01",
        )

        formatted = service.format_history_for_prompt(session_id, last_n=2)

        assert "a4: T4" in formatted
        assert "a5: T5" in formatted
        assert "a1: T1" not in formatted

    def test_format_history_for_prompt_invalid_session(self, service):
        """Test formatting for non-existent session"""
        formatted = service.format_history_for_prompt("invalid")
        assert formatted == "(No debate history)"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
