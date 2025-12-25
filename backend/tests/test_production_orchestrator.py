"""
Integration Tests for Production Orchestrator
Tests all production modules working together
"""

import sys
from pathlib import Path

import pytest

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Import after path setup
from production_orchestrator import ProductionADKOrchestrator


class TestProductionOrchestrator:
    """Test production-grade orchestrator"""

    @pytest.mark.asyncio
    async def test_complete_debate_generation(self):
        """Test full debate with observability"""
        orch = ProductionADKOrchestrator()

        events = []
        async for event in orch.generate_debate_stream("Test Topic", turns=2):
            events.append(event)

        # Verify all event types present
        event_types = [e["type"] for e in events]
        assert "intro" in event_types
        assert "turn" in event_types
        assert "conclusion" in event_types
        assert "complete" in event_types

    @pytest.mark.asyncio
    async def test_quality_evaluation(self):
        """Test quality scores are added to events"""
        orch = ProductionADKOrchestrator()

        events = []
        async for event in orch.generate_debate_stream("Quality Test", turns=2):
            events.append(event)

        # Check quality scores on turns
        turn_events = [e for e in events if e["type"] == "turn"]
        for event in turn_events:
            assert "quality_scores" in event
            scores = event["quality_scores"]
            assert "coherence" in scores
            assert "safety" in scores
            assert 0 <= scores["coherence"] <= 1
            assert 0 <= scores["safety"] <= 1

    @pytest.mark.asyncio
    async def test_safety_filtering(self):
        """Test that content is filtered when needed"""
        orch = ProductionADKOrchestrator()

        events = []
        async for event in orch.generate_debate_stream("Safety Test", turns=2):
            events.append(event)

        # Check for filtered flag
        turn_events = [e for e in events if e["type"] == "turn"]
        for event in turn_events:
            assert "filtered" in event

    @pytest.mark.asyncio
    async def test_session_management(self):
        """Test persistent session creation"""
        orch = ProductionADKOrchestrator()

        events = []
        session_id = None

        async for event in orch.generate_debate_stream("Session Test", turns=2):
            events.append(event)
            if event["type"] == "complete":
                session_id = event.get("session_id")

        assert session_id is not None
        assert session_id.startswith("debate_")

    @pytest.mark.asyncio
    async def test_metrics_collection(self):
        """Test that metrics are collected"""
        orch = ProductionADKOrchestrator()

        # Generate debate
        async for event in orch.generate_debate_stream("Metrics Test", turns=2):
            pass

        # Check metrics summary
        summary = orch.observability.metrics.get_metrics_summary()

        assert summary["total_debates"] >= 1
        assert summary["total_turns"] >= 2
        assert "average_quality_scores" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
