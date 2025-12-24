"""
Tests for Enhanced ADK Orchestrator
Tests transcript generation, file output, and streaming functionality
"""

import pytest
from pathlib import Path
import sys
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from adk_orchestrator_enhanced import (  # noqa: E402
    EnhancedADKOrchestrator,
    DebateMessage,
)


class TestEnhancedADKOrchestrator:
    """Test the enhanced orchestrator with transcript generation"""

    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self):
        """Test orchestrator initializes with all agents"""
        orch = EnhancedADKOrchestrator()

        assert orch.shakti is not None
        assert orch.sovereignist is not None
        assert orch.reformist is not None
        assert orch.technocrat is not None
        assert orch.humanist is not None
        assert len(orch.agents) == 5
        assert orch.current_turn == 0
        assert len(orch.debate_history) == 0

    @pytest.mark.asyncio
    async def test_debate_stream_basic(self):
        """Test basic debate stream generation"""
        orch = EnhancedADKOrchestrator()

        events = []
        async for event in orch.generate_debate_stream(
            "Test Topic", turns=2, save_transcript=False
        ):
            events.append(event)

        # Should have intro + 2 turns + conclusion
        assert len(events) >= 4
        assert events[0]["type"] == "intro"
        assert events[-1]["type"] == "conclusion"

        # Check turn events
        turn_events = [e for e in events if e["type"] == "turn"]
        assert len(turn_events) == 2

    @pytest.mark.asyncio
    async def test_debate_stream_with_transcript(self):
        """Test debate stream with transcript saving"""
        orch = EnhancedADKOrchestrator()

        events = []
        async for event in orch.generate_debate_stream(
            "Transcript Test", turns=2, save_transcript=True
        ):
            events.append(event)

        # Should have transcript_saved event
        transcript_events = [e for e in events if e["type"] == "transcript_saved"]
        assert len(transcript_events) == 1
        assert "filename" in transcript_events[0]
        # Check for sanitized version of topic
        assert "Transcript_Test" in transcript_events[0]["filename"]
        assert "crossfire_debate" in transcript_events[0]["filename"]

        # Cleanup - delete generated file
        filename = transcript_events[0]["filename"]
        if Path(filename).exists():
            Path(filename).unlink()

    @pytest.mark.asyncio
    async def test_debate_history_tracking(self):
        """Test that debate history is properly tracked"""
        orch = EnhancedADKOrchestrator()

        async for event in orch.generate_debate_stream(
            "History Test", turns=4, save_transcript=False
        ):
            pass

        # Should have intro + 4 turns + conclusion = 6 messages
        assert len(orch.debate_history) == 6
        assert orch.debate_history[0].speaker == "shakti"
        assert orch.debate_history[-1].speaker == "shakti"

    @pytest.mark.asyncio
    async def test_agent_rotation(self):
        """Test that agents rotate properly in debate"""
        orch = EnhancedADKOrchestrator()

        events = []
        async for event in orch.generate_debate_stream(
            "Rotation Test", turns=4, save_transcript=False
        ):
            if event["type"] == "turn":
                events.append(event)

        # Should have all 4 debaters
        speakers = [e["speaker"] for e in events]
        assert "sovereignist" in speakers
        assert "reformist" in speakers
        assert "technocrat" in speakers
        assert "humanist" in speakers

    @pytest.mark.asyncio
    async def test_event_structure(self):
        """Test that events have correct structure"""
        orch = EnhancedADKOrchestrator()

        async for event in orch.generate_debate_stream(
            "Structure Test", turns=1, save_transcript=False
        ):
            assert "type" in event
            assert "speaker" in event or event["type"] == "transcript_saved"
            assert "agent_name" in event or event["type"] == "transcript_saved"
            assert "text" in event or event["type"] == "transcript_saved"
            assert "turn" in event or event["type"] == "transcript_saved"

    @pytest.mark.asyncio
    async def test_different_turn_counts(self):
        """Test debate with various turn counts"""
        orch = EnhancedADKOrchestrator()

        for turns in [2, 4, 8]:
            events = []
            async for event in orch.generate_debate_stream(
                f"Test {turns} turns", turns=turns, save_transcript=False
            ):
                events.append(event)

            turn_events = [e for e in events if e["type"] == "turn"]
            assert len(turn_events) == turns

    def test_debate_message_dataclass(self):
        """Test DebateMessage dataclass"""
        msg = DebateMessage(
            speaker="test_speaker",
            agent_name="Test Agent",
            text="Test text",
            turn=1,
            timestamp="12:00:00",
        )

        assert msg.speaker == "test_speaker"
        assert msg.agent_name == "Test Agent"
        assert msg.text == "Test text"
        assert msg.turn == 1
        assert msg.timestamp == "12:00:00"

    def test_format_history_empty(self):
        """Test history formatting with empty history"""
        orch = EnhancedADKOrchestrator()
        formatted = orch._format_history()
        assert formatted == "(Debate just starting)"

    def test_format_history_with_messages(self):
        """Test history formatting with messages"""
        orch = EnhancedADKOrchestrator()

        # Add some messages
        orch.debate_history.append(
            DebateMessage(
                speaker="shakti",
                agent_name="Shakti",
                text="Intro",
                turn=0,
                timestamp="12:00:00",
            )
        )
        orch.debate_history.append(
            DebateMessage(
                speaker="sovereignist",
                agent_name="Sovereignist",
                text="Response 1",
                turn=1,
                timestamp="12:00:01",
            )
        )

        formatted = orch._format_history()
        assert "Shakti" in formatted
        assert "Sovereignist" in formatted

    def test_generate_transcript(self):
        """Test transcript generation"""
        orch = EnhancedADKOrchestrator()

        # Add some debate history
        orch.debate_history.append(
            DebateMessage(
                speaker="shakti",
                agent_name="Shakti",
                text="Welcome!",
                turn=0,
                timestamp="12:00:00",
            )
        )
        orch.debate_history.append(
            DebateMessage(
                speaker="sovereignist",
                agent_name="Sovereignist",
                text="My point!",
                turn=1,
                timestamp="12:00:01",
            )
        )

        start_time = datetime.now()
        transcript = orch._generate_transcript("Test Topic", start_time)

        assert "CROSSFIRE PODCAST" in transcript
        assert "Test Topic" in transcript
        assert "Shakti" in transcript
        assert "Sovereignist" in transcript
        assert "Welcome!" in transcript
        assert "My point!" in transcript

    def test_save_transcript(self):
        """Test transcript file saving"""
        orch = EnhancedADKOrchestrator()

        content = "# Test Transcript\n\nTest content"
        filename = orch._save_transcript(content, "Test Topic")

        # Verify file was created
        filepath = Path(filename)
        assert filepath.exists()
        assert "crossfire_debate" in filename
        assert "Test_Topic" in filename

        # Verify content
        saved_content = filepath.read_text(encoding="utf-8")
        assert saved_content == content

        # Cleanup
        filepath.unlink()

    def test_save_transcript_sanitizes_filename(self):
        """Test that special characters are sanitized in filename"""
        orch = EnhancedADKOrchestrator()

        content = "Test"
        filename = orch._save_transcript(content, "Test/Topic:With*Special?Chars")

        # Get just the filename part (not the full path)
        basename = Path(filename).name

        # Verify special chars are replaced in the basename
        assert "/" not in basename
        assert ":" not in basename
        assert "*" not in basename
        assert "?" not in basename
        assert "Test_Topic_With_Special_Chars" in basename

        # Cleanup
        Path(filename).unlink()

    @pytest.mark.asyncio
    async def test_call_agent_async_shakti_intro(self):
        """Test agent call for Shakti intro"""
        orch = EnhancedADKOrchestrator()

        response = await orch._call_agent_async(
            orch.shakti, "Introduce this debate: AI in Education"
        )

        assert "BREAKING" in response or "CROSSFIRE" in response
        assert len(response) > 0

    @pytest.mark.asyncio
    async def test_call_agent_async_shakti_conclusion(self):
        """Test agent call for Shakti conclusion"""
        orch = EnhancedADKOrchestrator()

        response = await orch._call_agent_async(orch.shakti, "Give a closing statement")

        assert len(response) > 0
        assert "EXPLOSIVE" in response or "CROSSFIRE" in response

    @pytest.mark.asyncio
    async def test_call_agent_async_debaters(self):
        """Test agent calls for all debaters"""
        orch = EnhancedADKOrchestrator()

        # Test each debater
        sovereignist_response = await orch._call_agent_async(
            orch.sovereignist, "React to topic"
        )
        assert len(sovereignist_response) > 0

        reformist_response = await orch._call_agent_async(
            orch.reformist, "React to topic"
        )
        assert len(reformist_response) > 0

        technocrat_response = await orch._call_agent_async(
            orch.technocrat, "React to topic"
        )
        assert len(technocrat_response) > 0

        humanist_response = await orch._call_agent_async(
            orch.humanist, "React to topic"
        )
        assert len(humanist_response) > 0

    @pytest.mark.asyncio
    async def test_current_turn_tracking(self):
        """Test that current turn is tracked correctly"""
        orch = EnhancedADKOrchestrator()

        assert orch.current_turn == 0

        async for event in orch.generate_debate_stream(
            "Turn Test", turns=3, save_transcript=False
        ):
            if event["type"] == "turn":
                # Current turn should match event turn
                assert orch.current_turn == event["turn"]

    @pytest.mark.asyncio
    async def test_timestamp_in_messages(self):
        """Test that timestamps are added to messages"""
        orch = EnhancedADKOrchestrator()

        async for event in orch.generate_debate_stream(
            "Timestamp Test", turns=1, save_transcript=False
        ):
            pass

        # Check all messages have timestamps
        for msg in orch.debate_history:
            assert msg.timestamp != ""
            assert ":" in msg.timestamp  # Should be in HH:MM:SS format


class TestDebateMessageDataclass:
    """Test the DebateMessage dataclass"""

    def test_create_with_all_fields(self):
        """Test creating message with all fields"""
        msg = DebateMessage(
            speaker="test",
            agent_name="Test Agent",
            text="Test text",
            turn=5,
            timestamp="14:30:00",
        )

        assert msg.speaker == "test"
        assert msg.agent_name == "Test Agent"
        assert msg.text == "Test text"
        assert msg.turn == 5
        assert msg.timestamp == "14:30:00"

    def test_create_with_default_timestamp(self):
        """Test creating message with default timestamp"""
        msg = DebateMessage(
            speaker="test", agent_name="Test Agent", text="Test text", turn=1
        )

        assert msg.timestamp == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
