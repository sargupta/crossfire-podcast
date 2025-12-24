"""
ADK Multi-Agent Debate Orchestrator - WORKING VERSION
CROSSFIRE PODCAST - Streaming Architecture

This module coordinates the 5 ADK agents using their chat capabilities
to create dynamic debates with real-time streaming.
"""

import asyncio
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import AsyncGenerator, Dict, List

# Import ADK Agent class
sys.path.insert(0, str(Path(__file__).parent / "adk_agents"))
from google.adk.agents.llm_agent import Agent


@dataclass
class DebateMessage:
    """A single message in the debate"""

    speaker: str
    agent_name: str
    text: str
    turn: int


class ADKDebateOrchestrator:
    """
    Manages multiagent debate using Google ADK agents.

    Simplified approach: Use agent prompting instead of complex tool calling.
    """

    def __init__(self):
        # Define agents inline to avoid import issues
        self.shakti = Agent(
            model="gemini-2.0-flash-exp",
            name="Shakti",
            description="Ruthless debate moderator",
            instruction="""
You are SHAKTI, the ruthless host of CROSSFIRE PODCAST.
Be aggressive, dramatic, and create conflict. Keep responses under 2 sentences.
Example: "BREAKING! Tonight: {topic}! Four experts, ZERO compromise!"
""",
        )

        self.sovereignist = Agent(
            model="gemini-2.0-flash-exp",
            name="Sovereignist",
            description="Traditionalist debater",
            instruction="""
You are the SOVEREIGNIST - defender of tradition.
Attack change aggressively. Keep under 3 sentences. Be punchy.
Example: "AI teachers? We've seen this before - calculators were supposed to make us smarter!"
""",
        )

        self.reformist = Agent(
            model="gemini-2.0-flash-exp",
            name="Reformist",
            description="Disruptor debater",
            instruction="""
You are the REFORMIST - radical who wants revolution.
Mock traditionalists. Keep under 3 sentences. Be sarcastic.
Example: "Oh please! Defending a system from the Industrial Revolution? Wake up!"
""",
        )

        self.technocrat = Agent(
            model="gemini-2.0-flash-exp",
            name="Technocrat",
            description="Data-driven debater",
            instruction="""
You are the TECHNOCRAT - pure logic, zero empathy.
Use stats and data. Keep under 3 sentences. Be ruthless.
Example: "Both wrong. AI outcomes improve by 34% (Stanford). Data over feelings."
""",
        )

        self.humanist = Agent(
            model="gemini-2.0-flash-exp",
            name="Humanist",
            description="Emotional moralist",
            instruction="""
You are the HUMANIST - emotional advocate.
Get passionate. Keep under 3 sentences. Be accusatory.
Example: "You're talking about kids like data points! Every child needs a human who CARES!"
""",
        )

        self.agents = {
            "shakti": self.shakti,
            "sovereignist": self.sovereignist,
            "reformist": self.reformist,
            "technocrat": self.technocrat,
            "humanist": self.humanist,
        }

        self.debate_history: List[DebateMessage] = []
        self.current_turn = 0

    async def generate_debate_stream(
        self, topic: str, turns: int = 8
    ) -> AsyncGenerator[Dict, None]:
        """
        Generate debate with streaming responses.

        Yields:
            Dict events with type: 'intro', 'turn', 'conclusion'
        """

        # 1. Moderator Introduction
        intro_prompt = f"Introduce this explosive debate topic in 2 sentences: {topic}"
        intro_response = await self._call_agent_async(self.shakti, intro_prompt)

        yield {
            "type": "intro",
            "speaker": "shakti",
            "agent_name": "Shakti",
            "text": intro_response,
            "turn": 0,
        }

        # 2. Debate Turns
        debaters = [
            ("sovereignist", self.sovereignist),
            ("reformist", self.reformist),
            ("technocrat", self.technocrat),
            ("humanist", self.humanist),
        ]

        for turn in range(1, turns + 1):
            self.current_turn = turn

            # Select debater (round-robin for prototype)
            debater_id, debater_agent = debaters[(turn - 1) % len(debaters)]

            # Debater responds
            debater_prompt = f"""
TOPIC: {topic}

DEBATE SO FAR:
{self._format_history()}

React to this debate. Attack previous speakers if relevant. Stay in character.
"""

            debater_response = await self._call_agent_async(
                debater_agent, debater_prompt
            )

            # Record in history
            msg = DebateMessage(
                speaker=debater_id,
                agent_name=debater_agent.name,
                text=debater_response,
                turn=turn,
            )
            self.debate_history.append(msg)

            yield {
                "type": "turn",
                "speaker": debater_id,
                "agent_name": debater_agent.name,
                "text": debater_response,
                "turn": turn,
            }

            # Small delay for pacing
            await asyncio.sleep(0.3)

        # 3. Conclusion
        conclusion_prompt = (
            f"Give a dramatic 2-sentence closing for this debate: {topic}"
        )
        conclusion = await self._call_agent_async(self.shakti, conclusion_prompt)

        yield {
            "type": "conclusion",
            "speaker": "shakti",
            "agent_name": "Shakti",
            "text": conclusion,
            "turn": turns + 1,
        }

    async def _call_agent_async(self, agent: Agent, prompt: str) -> str:
        """
        Call an ADK agent using proper session management.
        This uses REAL AI with ADK's session service!
        """
        try:
            from google.adk.runners import Runner
            from google.adk.sessions import InMemorySessionService

            # Create session service (in-memory for prototype)
            session_service = InMemorySessionService()

            # Create a runner for this agent
            runner = Runner(agent=agent, session_service=session_service)

            # Run the agent with the prompt (synchronous call)
            # Wrap in asyncio.to_thread for async behavior
            result = await asyncio.to_thread(runner.run, user_message=prompt)

            # Extract text response from ADK result
            # The result is a RunResult object with a 'response_message' attribute
            if hasattr(result, "response_message"):
                response = result.response_message
                if hasattr(response, "content") and response.content:
                    # Content is a list of parts
                    if isinstance(response.content, list) and len(response.content) > 0:
                        first_part = response.content[0]
                        if hasattr(first_part, "text"):
                            return first_part.text
                        return str(first_part)
                    return str(response.content)
                elif hasattr(response, "text"):
                    return response.text
                return str(response)
            elif hasattr(result, "text"):
                return result.text
            else:
                return str(result)

        except Exception as e:
            print(f"[ADK Error] Failed to call {agent.name}: {e}")
            import traceback

            traceback.print_exc()
            # Fallback to simulated response in case of error
            return self._get_fallback_response(agent.name)

    def _get_fallback_response(self, agent_name: str) -> str:
        """Fallback responses if ADK call fails"""
        fallbacks = {
            "Shakti": "BREAKING! Let's keep this debate moving!",
            "Sovereignist": "Tradition has proven itself. Change must prove worthy!",
            "Reformist": "The future waits for no one. Evolve or perish!",
            "Technocrat": "The data doesn't support either claim. Next!",
            "Humanist": "What about the human cost? That's what matters!",
        }
        return fallbacks.get(agent_name, "...")

    def _format_history(self) -> str:
        """Format debate history for context"""
        if not self.debate_history:
            return "(Debate just starting)"

        formatted = []
        for msg in self.debate_history[-3:]:  # Last 3 messages
            formatted.append(f"{msg.agent_name}: {msg.text}")

        return "\n".join(formatted)


# Test function
async def test_debate():
    """Test the orchestrator"""
    orchestrator = ADKDebateOrchestrator()

    topic = "Should AI Replace Human Teachers?"

    print(f"\n{'='*70}")
    print(f"CROSSFIRE PODCAST - ADK Multiagent System")
    print(f"Topic: {topic}")
    print(f"{'='*70}\n")

    async for event in orchestrator.generate_debate_stream(topic, turns=6):
        event_type = event["type"].upper()
        print(f"\n[{event_type}] Turn {event['turn']} - {event['agent_name']}")
        print(f"{event['text']}")
        print("-" * 70)

    print(f"\n{'='*70}")
    print("Debate Complete!")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    # Run test
    print("Testing ADK Orchestrator...")
    asyncio.run(test_debate())
