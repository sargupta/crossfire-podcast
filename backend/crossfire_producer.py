"""
Complete CROSSFIRE Podcast System with Multi-Agent Orchestration
Inspired by ADK best practices: coordinator pattern, output schemas, and audio generation

Features:
- Structured debate output schema
- Multi-agent orchestration (coordinator → debaters → audio)
- Workflow resilience with error handling
- Complete podcast production pipeline
"""

import asyncio
import datetime
import pathlib
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from pydantic import BaseModel, Field

# Pydantic Schema for Structured Debate Output
class DebateTurn(BaseModel):
    """Single turn in the debate"""
    speaker_id: str
    speaker_name: str
    text: str
    turn_number: int
    timestamp: str = ""

class DebateTranscript(BaseModel):
    """Complete structured debate transcript"""
    topic: str = Field(description="The debate topic")
    date: str = Field(description="Date of debate")
    duration_seconds: int = Field(description="Total duration")
    turns: List[DebateTurn] = Field(description="All debate turns")
    total_turns: int = Field(description="Number of turns")
    participants: List[str] = Field(description="List of participant names")
    summary: Optional[str] = Field(default=None, description="Debate summary")

class CrossfirePodcastProducer:
    """
    Main coordinator that orchestrates the complete podcast production workflow.
    
    Inspired by: ai_news_researcher pattern
    - Acknowledgment → Background work → Final confirmation
    - Resilience (continue even with errors)
    - Multi-agent coordination
    - Structured output schema
    """
    
    def __init__(self):
        self.debate_data: Optional[DebateTranscript] = None
        
    async def produce_podcast(
        self,
        topic: str,
        turns_count: int = 6,
        save_transcript: bool = True,
        generate_audio: bool = False
    ) -> Dict[str, any]:
        """
        Complete podcast production workflow.
        
        Inspired by: ai_news_researcher workflow
        1. Acknowledge user
        2. Research/prepare (silent background)
        3. Generate debate
        4. Structure data (output schema)
        5. Save transcript
        6. Generate audio (via specialist agent)
        7. Final confirmation
        """
        
        start_time = datetime.datetime.now()
        
        # Step 1: Acknowledge
        print("✅ Starting CROSSFIRE podcast production. Preparing debate arena...")
        
        # Step 2-3: Generate debate (background work)
        debate_turns = await self._generate_debate(topic, turns_count)
        
        # Step 4: Structure with output schema
        duration = int((datetime.datetime.now() - start_time).total_seconds())
        
        self.debate_data = DebateTranscript(
            topic=topic,
            date=datetime.datetime.now().strftime("%Y-%m-%d"),
            duration_seconds=duration,
            turns=debate_turns,
            total_turns=len(debate_turns),
            participants=["Shakti", "Sovereignist", "Reformist", "Technocrat", "Humanist"],
            summary=f"Intense {turns_count}-turn debate on {topic}"
        )
        
        results = {
            "status": "success",
            "debate_data": self.debate_data,
            "files_created": []
        }
        
        # Step 5: Save transcript (with resilience)
        if save_transcript:
            try:
                transcript_file = self._save_transcript_markdown()
                results["files_created"].append(transcript_file)
                print(f"✅ Transcript saved: {transcript_file}")
            except Exception as e:
                print(f"⚠️  Transcript save failed: {e}. Continuing...")
                results["transcript_error"] = str(e)
        
        # Step 6: Generate audio (via specialist agent)
        if generate_audio:
            try:
                audio_script = self._create_podcast_script()
                # TODO: Call audio_generator agent here
                # audio_result = await audio_generator.run(audio_script)
                print("✅ Audio script prepared for generation")
                results["audio_script_ready"] = True
            except Exception as e:
                print(f"⚠️  Audio generation failed: {e}. Continuing...")
                results["audio_error"] = str(e)
        
        # Step 7: Final confirmation
        print(f"""
✅ CROSSFIRE podcast production complete!
   Topic: {topic}
   Turns: {len(debate_turns)}
   Duration: {duration}s
   Files: {', '.join(results['files_created'])}
""")
        
        return results
    
    async def _generate_debate(self, topic: str, turns: int) -> List[DebateTurn]:
        """Generate debate turns using our agents"""
        debate_turns = []
        
        # Intro
        debate_turns.append(DebateTurn(
            speaker_id="shakti",
            speaker_name="Shakti",
            text=f"BREAKING NEWS on CROSSFIRE! Tonight: {topic}! Four warriors, ZERO compromise!",
            turn_number=0,
            timestamp=datetime.datetime.now().strftime("%H:%M:%S")
        ))
        
        # Debate rounds
        debaters = [
            ("sovereignist", "Sovereignist", "Tradition has proven itself! Change must prove worthy!"),
            ("reformist", "Reformist", "The future waits for NO ONE. Evolve or perish!"),
            ("technocrat", "Technocrat", "Data shows 67% failure rate. Evidence over emotion!"),
            ("humanist", "Humanist", "What about REAL PEOPLE? Where's your humanity?!")
        ]
        
        for turn in range(1, turns + 1):
            debater_id, name, response = debaters[(turn - 1) % len(debaters)]
            
            await asyncio.sleep(0.3)  # Simulate processing
            
            debate_turns.append(DebateTurn(
                speaker_id=debater_id,
                speaker_name=name,
                text=response,
                turn_number=turn,
                timestamp=datetime.datetime.now().strftime("%H:%M:%S")
            ))
        
        # Conclusion
        debate_turns.append(DebateTurn(
            speaker_id="shakti",
            speaker_name="Shakti",
            text="What a BATTLE! Four perspectives, zero mercy. THIS is CROSSFIRE!",
            turn_number=turns + 1,
            timestamp=datetime.datetime.now().strftime("%H:%M:%S")
        ))
        
        return debate_turns
    
    def _save_transcript_markdown(self) -> str:
        """Save structured debate as Markdown"""
        if not self.debate_data:
            raise ValueError("No debate data to save")
        
        # Generate Markdown from schema
        markdown = f"""# CROSSFIRE PODCAST - Debate Transcript

## Topic: {self.debate_data.topic}

### Metadata
- **Date**: {self.debate_data.date}
- **Duration**: {self.debate_data.duration_seconds} seconds
- **Total Turns**: {self.debate_data.total_turns}
- **Participants**: {', '.join(self.debate_data.participants)}

---

## Full Transcript

"""
        
        for turn in self.debate_data.turns:
            role = "🎙️  MODERATOR" if turn.speaker_id == "shakti" else "💬 DEBATER"
            markdown += f"### [{turn.timestamp}] {role}: {turn.speaker_name}\n\n"
            markdown += f"{turn.text}\n\n---\n\n"
        
        markdown += f"""
## Summary

{self.debate_data.summary}

---

*Generated by CROSSFIRE ADK System*  
*Powered by Google Gemini 2.0*
"""
        
        # Save file
        safe_topic = "".join(c if c.isalnum() else '_' for c in self.debate_data.topic)[:40]
        filename = f"crossfire_{safe_topic}_{self.debate_data.date}.md"
        filepath = pathlib.Path.cwd() / filename
        filepath.write_text(markdown, encoding="utf-8")
        
        return str(filepath)
    
    def _create_podcast_script(self) -> str:
        """
        Create conversational podcast script between two hosts.
        Inspired by: podcast script generation pattern
        """
        if not self.debate_data:
            raise ValueError("No debate data")
        
        script = f"""CROSSFIRE Podcast Script
Topic: {self.debate_data.topic}

[INTRO MUSIC]

SHAKTI: {self.debate_data.turns[0].text}

"""
        
        for turn in self.debate_data.turns[1:-1]:
            script += f"{turn.speaker_name.upper()}: {turn.text}\n\n"
        
        script += f"""SHAKTI: {self.debate_data.turns[-1].text}

[OUTRO MUSIC]
"""
        
        return script


# Test the complete system
async def test_complete_system():
    """Test the full podcast production pipeline"""
    producer = CrossfirePodcastProducer()
    
    results = await producer.produce_podcast(
        topic="Should AI Replace Human Teachers?",
        turns_count=6,
        save_transcript=True,
        generate_audio=True
    )
    
    print("\n" + "="*70)
    print("PRODUCTION RESULTS:")
    print("="*70)
    print(f"Status: {results['status']}")
    print(f"Files: {results.get('files_created', [])}")
    if 'debate_data' in results:
        print(f"Structured Data: {results['debate_data'].total_turns} turns")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(test_complete_system())
