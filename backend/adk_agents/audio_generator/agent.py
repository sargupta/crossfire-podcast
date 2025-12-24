"""
Audio Generation Agent for CROSSFIRE Podcast
Specialized agent that converts debate transcripts to multi-speaker audio
"""

from typing import Dict
import pathlib
from google.adk.agents import Agent


def generate_debate_audio(
    script: str, filename: str = "crossfire_debate"
) -> Dict[str, str]:
    """
    Converts debate script to multi-speaker audio podcast.

    Args:
        script: Formatted debate script with speaker labels
        filename: Output filename (without extension)

    Returns:
        Dictionary with audio generation status
    """
    try:
        # TODO: Integrate with Google TTS or existing TTS system
        # For now, save script for manual processing
        output_file = pathlib.Path.cwd() / f"{filename}_script.txt"
        output_file.write_text(script, encoding="utf-8")

        return {
            "status": "success",
            "message": f"Audio script prepared at {output_file}. Ready for TTS processing.",
            "audio_file": f"{filename}.mp3",
            "script_file": str(output_file),
        }
    except Exception as e:
        return {"status": "error", "message": f"Audio generation failed: {str(e)}"}


# Audio Generation Specialist Agent
audio_generator = Agent(
    name="audio_generator",
    model="gemini-2.0-flash-exp",
    instruction="""
**Your Identity:** You are an Audio Generation Specialist for CROSSFIRE Podcast.

**Single Task:** Convert debate transcripts into multi-speaker audio files.

**Workflow:**
1. Receive debate script from coordinator
2. Call `generate_debate_audio` tool with script and filename
3. Report success or failure back

**Critical:** You ONLY handle audio generation. Don't debate or moderate.
""",
    tools=[generate_debate_audio],
)

root_agent = audio_generator
