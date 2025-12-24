"""
Production-Ready ADK Orchestrator
Integrates all production modules: sessions, quality, observability
"""

import asyncio

from typing import AsyncGenerator, Dict, Optional
from datetime import datetime

from managed_session_service import ManagedSessionService, DebateContext
from quality_evaluator import DebateQualityEvaluator, SafetyFilter
from observability import Observability

from google.adk.agents.llm_agent import Agent


class ProductionADKOrchestrator:
    """
    Production orchestrator with full observability and quality assurance.

    Features:
    - Persistent session management
    - Real-time quality evaluation
    - Content safety filtering
    - Complete observability (logging, tracing, metrics)
    """

    def __init__(self, project_id: str = "aipodcaster-481909"):
        # Initialize production services
        self.session_service = ManagedSessionService(project_id)
        self.quality_evaluator = DebateQualityEvaluator(project_id)
        self.safety_filter = SafetyFilter(self.quality_evaluator)
        self.observability = Observability()

        # Create agents
        self._initialize_agents()

        self.current_session: Optional[DebateContext] = None

    def _initialize_agents(self):
        """Initialize all debate agents"""

        # Shakti (Moderator)
        self.shakti = Agent(
            model="gemini-2.0-flash-exp",
            name="Shakti",
            description="Ruthless CROSSFIRE host",
            instruction="""
            You are SHAKTI, host of CROSSFIRE debates.
            Keep responses under 2 sentences. Be dramatic and aggressive.
            """,
        )

        # Debaters
        self.sovereignist = Agent(
            model="gemini-2.0-flash-exp",
            name="Sovereignist",
            instruction="Defender of tradition. Attack change. Under 3 sentences.",
        )

        self.reformist = Agent(
            model="gemini-2.0-flash-exp",
            name="Reformist",
            instruction="Revolutionary disruptor. Mock tradition. Under 3 sentences.",
        )

        self.technocrat = Agent(
            model="gemini-2.0-flash-exp",
            name="Technocrat",
            instruction="Pure logic, zero empathy. Cite data. Under 3 sentences.",
        )

        self.humanist = Agent(
            model="gemini-2.0-flash-exp",
            name="Humanist",
            instruction="Emotional advocate. Show passion. Under 3 sentences.",
        )

        self.agents = {
            "shakti": self.shakti,
            "sovereignist": self.sovereignist,
            "reformist": self.reformist,
            "technocrat": self.technocrat,
            "humanist": self.humanist,
        }

    async def generate_debate_stream(
        self, topic: str, turns: int = 6
    ) -> AsyncGenerator[Dict, None]:
        """
        Generate production-ready debate stream with full observability.

        Features:
        - Persistent session management
        - Quality evaluation on every turn
        - Safety filtering
        - Complete tracing and metrics
        """

        start_time = datetime.now()

        # Create managed session
        self.current_session = await self.session_service.create_session(
            topic=topic,
            participants=[
                "shakti",
                "sovereignist",
                "reformist",
                "technocrat",
                "humanist",
            ],
        )

        session_id = self.current_session.session_id

        # Log debate start
        self.observability.log_debate_start(topic, turns, session_id)

        # Trace entire debate
        with self.observability.tracer.span(
            "debate_generation", topic=topic, turns=turns
        ):
            try:
                # 1. Moderator Introduction
                yield await self._generate_intro(topic, session_id)

                # 2. Debate Turns
                debaters = [
                    ("sovereignist", self.sovereignist),
                    ("reformist", self.reformist),
                    ("technocrat", self.technocrat),
                    ("humanist", self.humanist),
                ]

                for turn in range(1, turns + 1):
                    debater_id, debater_agent = debaters[(turn - 1) % len(debaters)]

                    yield await self._generate_turn(
                        debater_id, debater_agent, turn, session_id
                    )

                # 3. Conclusion
                yield await self._generate_conclusion(topic, session_id)

                # Log successful completion
                duration = (datetime.now() - start_time).total_seconds()
                self.observability.log_debate_complete(topic, session_id, duration)

                # Close session
                await self.session_service.close_session(session_id)

                yield {
                    "type": "complete",
                    "session_id": session_id,
                    "total_turns": turns,
                }

            except Exception as e:
                self.observability.log_error(
                    "debate_generation_failed", str(e), session_id=session_id
                )
                yield {"type": "error", "message": str(e), "session_id": session_id}

    async def _generate_intro(self, topic: str, session_id: str) -> Dict:
        """Generate moderated introduction"""

        with self.observability.tracer.span("intro_generation", topic=topic):
            intro_text = f"BREAKING NEWS on CROSSFIRE! Tonight: {topic}! Four warriors, ZERO compromise!"

            # Evaluate quality
            scores = await self.quality_evaluator.evaluate_turn(intro_text, "shakti")

            # Update session
            await self.session_service.update_context(
                session_id,
                {
                    "speaker": "shakti",
                    "text": intro_text,
                    "turn": 0,
                    "quality_scores": {
                        "coherence": scores.coherence,
                        "safety": scores.safety,
                        "toxicity": scores.toxicity,
                    },
                },
            )

            # Record metrics
            self.observability.metrics.record_quality_score(
                "coherence", scores.coherence, "shakti"
            )
            self.observability.metrics.record_quality_score(
                "safety", scores.safety, "shakti"
            )

            return {
                "type": "intro",
                "speaker": "shakti",
                "agent_name": "Shakti",
                "text": intro_text,
                "turn": 0,
                "quality_scores": {
                    "coherence": scores.coherence,
                    "safety": scores.safety,
                    "toxicity": scores.toxicity,
                },
            }

    async def _generate_turn(
        self, speaker_id: str, agent: Agent, turn: int, session_id: str
    ) -> Dict:
        """Generate a single debate turn with quality checks"""

        with self.observability.tracer.span(
            "turn_generation", turn=turn, speaker=speaker_id
        ):
            turn_start = datetime.now()

            # history = self.session_service.format_history_for_prompt(
            #     session_id, last_n=3
            # )

            # Generate response (simulated for now)
            await asyncio.sleep(0.3)

            # Mock responses
            responses = {
                "sovereignist": "Tradition has proven itself! Change must prove worthy!",
                "reformist": "The future waits for NO ONE. Evolve or perish!",
                "technocrat": "Data shows 67% failure rate. Evidence over emotion!",
                "humanist": "What about REAL PEOPLE? Where's your humanity?!",
            }

            text = responses.get(speaker_id, "...")

            # Evaluate quality
            scores = await self.quality_evaluator.evaluate_turn(text, speaker_id)

            # Apply safety filter
            filtered = await self.safety_filter.filter_content(text, speaker_id)

            final_text = filtered["text"]

            # Update session
            await self.session_service.update_context(
                session_id,
                {
                    "speaker": speaker_id,
                    "text": final_text,
                    "turn": turn,
                    "filtered": filtered["filtered"],
                    "quality_scores": {
                        "coherence": scores.coherence,
                        "safety": scores.safety,
                        "toxicity": scores.toxicity,
                    },
                },
            )

            # Record metrics
            turn_duration = (datetime.now() - turn_start).total_seconds()
            self.observability.metrics.record_turn_generated(
                speaker_id, turn, turn_duration
            )
            self.observability.metrics.record_quality_score(
                "coherence", scores.coherence, speaker_id
            )
            self.observability.metrics.record_quality_score(
                "safety", scores.safety, speaker_id
            )

            # Log turn
            self.observability.log_turn_generated(speaker_id, turn, final_text)

            return {
                "type": "turn",
                "speaker": speaker_id,
                "agent_name": agent.name,
                "text": final_text,
                "turn": turn,
                "filtered": filtered["filtered"],
                "quality_scores": {
                    "coherence": scores.coherence,
                    "safety": scores.safety,
                    "toxicity": scores.toxicity,
                },
            }

    async def _generate_conclusion(self, topic: str, session_id: str) -> Dict:
        """Generate conclusion"""

        with self.observability.tracer.span("conclusion_generation"):
            conclusion_text = (
                "What a BATTLE! Four perspectives, zero mercy. THIS is CROSSFIRE!"
            )

            # Evaluate
            scores = await self.quality_evaluator.evaluate_turn(
                conclusion_text, "shakti"
            )

            return {
                "type": "conclusion",
                "speaker": "shakti",
                "agent_name": "Shakti",
                "text": conclusion_text,
                "turn": -1,
                "quality_scores": {
                    "coherence": scores.coherence,
                    "safety": scores.safety,
                },
            }


# Test the production orchestrator
async def test_production_orchestrator():
    """Test complete production pipeline"""

    orchestrator = ProductionADKOrchestrator()

    print("=" * 70)
    print("PRODUCTION ORCHESTRATOR TEST")
    print("=" * 70)

    topic = "AI vs Human Intelligence"
    events = []

    async for event in orchestrator.generate_debate_stream(topic, turns=4):
        events.append(event)

        print(f"\n[{event['type'].upper()}] {event.get('agent_name', 'N/A')}")
        print(f"Text: {event.get('text', '')[:60]}...")

        if "quality_scores" in event:
            scores = event["quality_scores"]
            print(
                f"Quality: C={scores.get('coherence', 0):.2f} S={scores.get('safety', 0):.2f}"
            )

    print("\n" + "=" * 70)
    print(f"✅ Generated {len(events)} events")

    # Get metrics summary
    summary = orchestrator.observability.metrics.get_metrics_summary()
    print("\n📊 METRICS SUMMARY:")
    print(f"   Total Debates: {summary['total_debates']}")
    print(f"   Success Rate: {summary['success_rate']:.1%}")
    print(
        f"   Avg Coherence: {summary['average_quality_scores'].get('coherence', 0):.2f}"
    )
    print(f"   Avg Safety: {summary['average_quality_scores'].get('safety', 0):.2f}")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_production_orchestrator())
