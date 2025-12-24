"""
Integration Tests for ADK Orchestrator
Tests the complete debate generation pipeline
"""

import pytest
import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from adk_orchestrator import ADKDebateOrchestrator
from crossfire_producer import CrossfirePodcastProducer


class TestADKOrchestrator:
    """Test the streaming debate orchestrator"""
    
    @pytest.mark.asyncio
    async def test_debate_stream_generation(self):
        """Test generating a complete debate stream"""
        orchestrator = ADKDebateOrchestrator()
        
        events = []
        async for event in orchestrator.generate_debate_stream("Test Topic", turns=2):
            events.append(event)
        
        # Verify structure
        assert len(events) >= 3, "Should have intro + turns + conclusion"
        
        # Verify event types
        assert events[0]['type'] == 'intro'
        assert events[-1]['type'] == 'conclusion'
        
        # Verify all events have required fields
        for event in events:
            assert 'type' in event
            assert 'speaker' in event
            assert 'agent_name' in event
            assert 'text' in event
            assert 'turn' in event
    
    @pytest.mark.asyncio
    async def test_debate_with_different_turn_counts(self):
        """Test debate generation with various turn counts"""
        orchestrator = ADKDebateOrchestrator()
        
        for turns in [2, 4, 6]:
            events = []
            async for event in orchestrator.generate_debate_stream("Topic", turns=turns):
                events.append(event)
            
            # Should have intro + turns + conclusion
            expected_events = 1 + turns + 1
            assert len(events) == expected_events
    
    @pytest.mark.asyncio
    async def test_all_debaters_participate(self):
        """Verify all 4 debaters speak in longer debates"""
        orchestrator = ADKDebateOrchestrator()
        
        events = []
        async for event in orchestrator.generate_debate_stream("Topic", turns=4):
            events.append(event)
        
        # Extract debater speakers (exclude shakti)
        debaters = [e['speaker'] for e in events if e['speaker'] != 'shakti']
        
        # Should have all 4 debaters
        unique_debaters = set(debaters)
        assert len(unique_debaters) == 4
        assert 'sovereignist' in unique_debaters
        assert 'reformist' in unique_debaters
        assert 'technocrat' in unique_debaters
        assert 'humanist' in unique_debaters


class TestCrossfireProducer:
    """Test the complete production pipeline"""
    
    @pytest.mark.asyncio
    async def test_produce_podcast_basic(self):
        """Test basic podcast production"""
        producer = CrossfirePodcastProducer()
        
        result = await producer.produce_podcast(
            topic="Test Debate",
            turns_count=2,
            save_transcript=False,
            generate_audio=False
        )
        
        assert result['status'] == 'success'
        assert result['debate_data'] is not None
        assert result['debate_data'].total_turns > 0
    
    @pytest.mark.asyncio
    async def test_produce_podcast_with_transcript(self):
        """Test podcast production with transcript saving"""
        producer = CrossfirePodcastProducer()
        
        result = await producer.produce_podcast(
            topic="Integration Test",
            turns_count=2,
            save_transcript=True,
            generate_audio=False
        )
        
        assert result['status'] == 'success'
        assert 'files_created' in result
        assert len(result['files_created']) > 0
        
        # Verify file exists
        transcript_file = Path(result['files_created'][0])
        assert transcript_file.exists()
        
        # Verify content
        content = transcript_file.read_text()
        assert 'CROSSFIRE' in content
        assert 'Integration Test' in content
    
    @pytest.mark.asyncio
    async def test_structured_output_schema(self):
        """Test Pydantic schema validation"""
        producer = CrossfirePodcastProducer()
        
        result = await producer.produce_podcast(
            topic="Schema Test",
            turns_count=2,
            save_transcript=False
        )
        
        debate_data = result['debate_data']
        
        # Test schema fields
        assert debate_data.topic == "Schema Test"
        assert debate_data.date is not None
        assert debate_data.duration_seconds >= 0
        assert len(debate_data.turns) > 0
        assert len(debate_data.participants) == 5
        
        # Test turn structure
        for turn in debate_data.turns:
            assert hasattr(turn, 'speaker_id')
            assert hasattr(turn, 'speaker_name')
            assert hasattr(turn, 'text')
            assert hasattr(turn, 'turn_number')


class TestErrorHandling:
    """Test error handling and resilience"""
    
    @pytest.mark.asyncio
    async def test_invalid_turn_count(self):
        """Test handling of invalid turn counts"""
        orchestrator = ADKDebateOrchestrator()
        
        # Should handle gracefully (no exception)
        events = []
        async for event in orchestrator.generate_debate_stream("Topic", turns=0):
            events.append(event)
        
        # Should still produce intro and conclusion
        assert len(events) >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
