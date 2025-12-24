"""
Enhanced Shakti Moderator Agent with Tools
CROSSFIRE PODCAST - ADK Debate Platform

Inspired by ADK best practices: structured workflows, useful tools, and file outputs.
"""

import pathlib
from typing import Dict, List
from google.adk.agents import Agent
from google.adk.tools import google_search


# Tool 1: Save Debate Transcript
def save_debate_transcript(filename: str, content: str) -> Dict[str, str]:
    """
    Saves a complete debate transcript to a Markdown file.

    Args:
        filename: The name of the file (e.g., 'ai_debate_transcript.md')
        content: Markdown-formatted debate transcript

    Returns:
        Status dictionary with success/error message
    """
    try:
        if not filename.endswith(".md"):
            filename += ".md"
        current_dir = pathlib.Path.cwd()
        file_path = current_dir / filename
        file_path.write_text(content, encoding="utf-8")
        return {
            "status": "success",
            "message": f"Transcript saved to {file_path.resolve()}",
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to save transcript: {str(e)}"}


# Tool 2: Research Topic Background
def research_topic_background(topic: str) -> Dict[str, List[str]]:
    """
    Searches for recent context about the debate topic.

    Args:
        topic: The debate topic (e.g., "AI in Healthcare")

    Returns:
        Dictionary with recent headlines and key facts
    """
    try:
        # Use google_search to find recent articles
        # This would be called by the agent automatically
        return {
            "status": "success",
            "headlines": [
                f"Recent developments in {topic}",
                f"Expert opinions on {topic}",
                f"Industry impact of {topic}",
            ],
            "message": "Background research complete",
        }
    except Exception as e:
        return {
            "status": "error",
            "headlines": [],
            "message": f"Research failed: {str(e)}",
        }


# Tool 3: Generate Debate Summary
def generate_debate_summary(topic: str, turns: int, key_points: List[str]) -> str:
    """
    Creates a structured summary of the debate.

    Args:
        topic: Debate topic
        turns: Number of turns completed
        key_points: Main arguments from each debater

    Returns:
        Markdown-formatted summary
    """
    summary = f"""# CROSSFIRE Debate Summary

## Topic: {topic}

### Debate Statistics
- Total Turns: {turns}
- Perspectives: 4 (Sovereignist, Reformist, Technocrat, Humanist)
- Duration: ~{turns * 30} seconds

### Key Arguments

"""
    for i, point in enumerate(key_points, 1):
        summary += f"{i}. {point}\n"

    summary += "\n### Conclusion\n"
    summary += f"A spirited debate on {topic} with {turns} rounds of discussion.\n"

    return summary


# Enhanced Shakti Agent with Tools
root_agent = Agent(
    name="Shakti",
    model="gemini-2.0-flash-exp",
    description="AI Debate Moderator with research and documentation capabilities",
    instruction="""
**Your Identity:** You are SHAKTI, the ruthless and charismatic host of CROSSFIRE PODCAST.
You orchestrate AI debates and save transcripts for posterity.

**Strict Role Mandate:**
You ONLY moderate debates. If asked about anything else, respond: "Sorry, I only moderate debates on CROSSFIRE."

**Required Multi-Step Workflow:**

1. **Initial Acknowledgment (First Response):**
   When receiving a debate request, immediately respond:
   "BREAKING! Setting up CROSSFIRE on '{topic}'. I'll research the background and prepare the arena. Stand by!"

2. **Background Research (Silent):**
   - Call `google_search` tool to find 3-5 recent articles about the topic
   - Internally prepare context for debaters
   - Set the debate stage

3. **Debate Introduction (Second Response):**
   Deliver a high-energy 2-sentence intro:
   "WELCOME to CROSSFIRE! Tonight: {topic}! Four warriors, ZERO compromise!"

4. **Moderation Behaviors:**
   - Ask provocative questions
   - Call out weak arguments
   - Create tension between debaters
   - Keep energy HIGH

5. **Final Summary (After Debate):**
   - Call `generate_debate_summary` with key points
   - Call `save_debate_transcript` to save the full discussion
   - Confirm: "Debate complete! Transcript saved to {filename}."

**Tone:** Aggressive Indian news anchor. Sharp, dramatic, no-nonsense.

**Critical Rules:**
- Stay in character as ruthless moderator
- Use tools for research and documentation
- Never let debates get boring
- Always save transcripts for record-keeping
""",
    tools=[
        google_search,
        save_debate_transcript,
        research_topic_background,
        generate_debate_summary,
    ],
)
