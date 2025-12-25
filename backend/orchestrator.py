"""
Orchestrator for managing the Debate Podcast generation.

Handles both Standard (One-shot) and potentially other modes.
Uses Vertex AI for casting and script generation.
"""

import os
from typing import Dict, List, Tuple

import vertexai
from vertexai.generative_models import ChatSession, GenerativeModel

# Initialize Vertex AI
# Project ID is pulled from environment variable GCP_PROJECT_ID provided by python-dotenv in main.py
# vertexai.init(project=os.getenv("GCP_PROJECT_ID"), location="us-central1")


class DebateAgent:
    """Wrapper for a debate agent with persona."""

    def __init__(self, manifest, model: GenerativeModel):
        """Initialize agent with manifest and model."""
        self.manifest = manifest
        self.model = model
        self.chat: ChatSession = model.start_chat()

        # Prime the agent with its identity
        self.system_prompt = f"""
        IDENTITY: {manifest.display_name}
        GOALS: {', '.join(manifest.goals)}
        INSTRUCTIONS: {', '.join(manifest.instructions)}
        TONE: {manifest.tone}

        You are participating in a high-stakes debate podcast called OMNI-CAST.
        Keep your responses short (under 50 words), punchy, and spoken-word style.
        Interject aggressively if the phase demands it.
        """


class PodcastOrchestrator:
    """
    Orchestrates the entire podcast generation process.

    Handles Casting, Agent instantiation, Script Generation, and TTS.
    """

    CASTING_PROMPT = """
    CRITICAL: The topic can be ANYTHING (Politics, Sports, Coding, Movies, Food).
    The tone must be AGGRESSIVE, CONTROVERSIAL, and HIGH-STAKES.
    Cast characters who are POLEMICISTS, FIREBRANDS, and ABSOLUTISTS.

    Archetype Definitions:

    1. sovereignist (The Traditionalist / Gatekeeper):
       - Trait: Fanatic defender of the old ways. Hostile to change.
       - Behavior: "My way or the highway."

    2. reformist (The Disruptor / Radical):
       - Trait: Wants to burn down the establishment.
       - Behavior: Mocking, Arrogant, Visionary.

    3. technocrat (The Logical Extremist):
       - Trait: Zero empathy. Pure data.
       - Behavior: Cold, robotic, merciless with facts.

    4. humanist (The Bleeding Heart / Moralist):
       - Trait: Extremely emotional. Guilt-tripper.
       - Behavior: Loud, Passionate, Accusatory.

    5. shakti (The Ruthless Anchor):
       - Role: Provocateur. Pokes the bear.
       - Trait: Doesn't let anyone speak fluff. Cuts mics.

    Instruction:
    - Create specific personas for the topic: '{topic}'.
    - Give them INTENSE backstories and credentials.
    - Names should sound formidable.

    Return a JSON List of objects with keys: category_id, name, sub_role, credential, behavior.
    """

    VOICE_MAP = {
        "sovereignist": "en-IN-Neural2-B",
        "reformist": "en-GB-Neural2-A",
        "technocrat": "en-US-Journey-D",
        "humanist": "en-US-Neural2-F",
        "shakti": "en-IN-Neural2-A",
    }

    def __init__(self):
        """Initialize Orchestrator with Vertex AI and GCS clients."""
        # 1. Initialize Vertex AI
        project_id = os.getenv("GCP_PROJECT_ID", "aipodcaster-481909")
        try:
            vertexai.init(project=project_id, location="us-central1")
            # Use stable model for default, though generate_debate sets its own
            self.model = GenerativeModel("gemini-1.5-flash")
        except Exception as e:
            print(f"Vertex AI Init Error: {e}")
            raise

        # 2. Text-to-Speech
        from google.cloud import texttospeech

        try:
            self.tts_client = texttospeech.TextToSpeechClient()
        except Exception as e:
            print(f"TTS Init Error: {e}")
            self.tts_client = None

        # 3. Initialize Storage
        from google.cloud import storage

        self.bucket_name = "omni-cast-assets-aipodcaster"
        try:
            self.storage_client = storage.Client()
        except Exception as e:
            print(f"Storage Init Error: {e}")
            self.storage_client = None

        self.agents = {}
        self.debug_logs = []

    def log(self, msg: str):
        """Append a message to the debug log."""
        print(msg)
        if hasattr(self, "debug_logs"):
            self.debug_logs.append(str(msg))

    def _ensure_bucket(self):
        """Ensure GCS bucket exists."""
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            if not bucket.exists():
                self.storage_client.create_bucket(self.bucket_name, location="US")
                print(f"Created bucket {self.bucket_name}")
        except Exception as e:
            print(f"Bucket Warning: {e}")

    def _upload_audio(self, content: bytes, filename: str) -> str:
        """Upload audio bytes to GCS and return public URL."""
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            blob = bucket.blob(f"audio/{filename}")
            blob.upload_from_string(content, content_type="audio/mpeg")

            try:
                blob.make_public()
            except Exception as e:
                print(f"Warning: Could not make blob public (IAM issue?): {e}")

            return blob.public_url
        except Exception as e:
            print(f"Upload Failed: {e}")
            return ""

    def _synthesize_line(self, text: str, speaker_id: str) -> bytes:
        """Synthesizes speech for a single line."""
        from google.cloud import texttospeech

        voice_name = self.VOICE_MAP.get(
            speaker_id.lower(), "en-US-Neural2-D"
        )  # Fallback
        if "sovereignist" in speaker_id:
            voice_name = self.VOICE_MAP["sovereignist"]
        elif "reformist" in speaker_id:
            voice_name = self.VOICE_MAP["reformist"]
        elif "technocrat" in speaker_id:
            voice_name = self.VOICE_MAP["technocrat"]
        elif "humanist" in speaker_id:
            voice_name = self.VOICE_MAP["humanist"]
        elif "shakti" in speaker_id:
            voice_name = self.VOICE_MAP["shakti"]

        language_code = "-".join(voice_name.split("-")[:2])

        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code, name=voice_name
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = self.tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        return response.audio_content

    def generate_cast(self, topic: str) -> Tuple[List[Dict[str, str]], str]:
        """Generate a cast of 5 debate personas based on the topic."""
        # Use a "Thinking" model (Pro) for Casting to get creative results
        candidate_models = [
            "gemini-2.0-flash-exp",
            "gemini-1.5-flash-001",
            "gemini-pro",
        ]

        for model_name in candidate_models:
            try:
                model = GenerativeModel(
                    model_name,
                    system_instruction="You are the Casting Director for a high-stakes debate.",
                )
                response = model.generate_content(
                    self.CASTING_PROMPT.format(topic=topic)
                )

                import json
                import re

                text = response.text
                match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
                if match:
                    text = match.group(1)
                else:
                    # Try to parse raw text if no code blocks
                    text = text.strip()

                return json.loads(text), model_name
            except Exception as e:
                print(f"Model {model_name} failed: {e}")
                continue

        # Fallback Cast (Guarantees functionality)
        print("WARNING: Dynamic Casting failed. Using Fallback Cast.")
        fallback_cast = [
            {
                "category_id": "shakti",
                "name": "Shakti",
                "sub_role": "The Ruthless Anchor",
                "credential": "Host",
                "behavior": "Ruthless moderator.",
            },
            {
                "category_id": "sovereignist",
                "name": "The Sovereignist",
                "sub_role": "Traditionalist",
                "credential": "Guardian",
                "behavior": "Defends tradition.",
            },
            {
                "category_id": "reformist",
                "name": "The Reformist",
                "sub_role": "The Disruptor",
                "credential": "Visionary",
                "behavior": "Demands change.",
            },
            {
                "category_id": "technocrat",
                "name": "The Technocrat",
                "sub_role": "The Logician",
                "credential": "Analyst",
                "behavior": "Pure data.",
            },
            {
                "category_id": "humanist",
                "name": "The Humanist",
                "sub_role": "The Moralist",
                "credential": "Advocate",
                "behavior": "Focuses on people.",
            },
        ]
        # Return a valid model name for the agents to use
        return fallback_cast, "gemini-2.0-flash-exp"

    def generate_debate(self, topic: str, turns: int = 4):
        """Generate a full debate script and audio."""
        self.debug_logs = []
        self.log(f"Starting generation for topic: {topic} with {turns} turns")

        # 2. Dynamic Casting
        try:
            formatted_cast, _ = self.generate_cast(topic)
            self.log(f"Cast generated: {len(formatted_cast)} agents")
        except Exception as e:
            self.log(f"Cast generation error: {e}")
            fallback = [
                {
                    "category_id": 1,
                    "name": "Shakti",
                    "sub_role": "Moderator",
                    "credential": "AI",
                    "behavior": "Strict",
                },
                {
                    "category_id": 2,
                    "name": "Sovereignist",
                    "sub_role": "Sovereignist",
                    "credential": "Patriot",
                    "behavior": "Defensive",
                },
                {
                    "category_id": 3,
                    "name": "Reformist",
                    "sub_role": "Reformist",
                    "credential": "Change",
                    "behavior": "Critical",
                },
                {
                    "category_id": 4,
                    "name": "Technocrat",
                    "sub_role": "Technocrat",
                    "credential": "Data",
                    "behavior": "Cold",
                },
                {
                    "category_id": 5,
                    "name": "Humanist",
                    "sub_role": "Humanist",
                    "credential": "People",
                    "behavior": "Emotional",
                },
            ]
            formatted_cast = fallback
            self.log("Using Fallback Cast")

        active_cast = []
        self.agents = {}

        system_prompt = """
        You are a debater in a high-stakes automated podcast.
        Role: {sub_role}
        Background: {credential}
        Personality: {behavior}

        CRITICAL INSTRUCTIONS:
        1. Keep response under 3 sentences.
        2. Be concise.
        """

        for profile in formatted_cast:
            # Handle key derivation carefully
            if "category_id" in profile:
                key = str(profile["category_id"]).lower()  # e.g. "sovereignist" or "1"
                # Map to role names if needed, or stick to simple keys
                if "sovereignist" in key:
                    key = "sovereignist"
                elif "reformist" in key:
                    key = "reformist"
                elif "technocrat" in key:
                    key = "technocrat"
                elif "humanist" in key:
                    key = "humanist"
                elif "shakti" in key:
                    key = "shakti"
            else:
                key = profile["sub_role"].lower()

            role_prompt = system_prompt.format(**profile)
            try:
                agent_model = GenerativeModel(
                    "gemini-1.5-flash", system_instruction=role_prompt
                )
                self.agents[key] = SimpleAgentWrapper(profile["name"], agent_model)
                active_cast.append(profile)
                self.log(f"Instantiated agent: {key}")
            except Exception as e:
                self.log(f"Error instantiating {key}: {e}")

        if not self.agents:
            self.log("No agents instantiated! Aborting.")
            return {"cast": [], "script": [], "debug_log": self.debug_logs}

        script = []
        history_text = f"TOPIC: {topic}\n"

        # Host Intro
        host = self.agents.get("shakti")
        if host:
            self.log("Generating Host Intro...")
            try:
                import time

                time.sleep(0.1)
                resp = host.chat.send_message(
                    f"Start the debate on '{topic}'. Introduce panel."
                )
                text = resp.text.strip()
                self.log(f"Host Intro: {text[:50]}...")
                script.append({"speaker": "shakti", "text": text, "name": host.name})
                history_text += f"Shakti: {text}\n"
            except Exception as e:
                self.log(f"Host Intro Error: {e}")
                script.append(
                    {"speaker": "System", "text": f"Error: {e}", "name": "System"}
                )
        else:
            self.log("Host (shakti) not found!")

        # Rounds
        order = ["sovereignist", "reformist", "technocrat", "humanist"]
        for i in range(turns):
            key = order[i % len(order)]
            agent = self.agents.get(key)
            if not agent:
                self.log(f"Agent {key} not found, skipping.")
                continue

            self.log(f"Generating turn {i+1} for {key}...")
            prompt = f"Previous conversation:\n{history_text}\nIt is your turn. Speak."
            try:
                import time

                time.sleep(0.1)
                resp = agent.chat.send_message(prompt)
                text = resp.text.strip()
                self.log(f"Agent Response: {text[:50]}...")
                script.append({"speaker": key, "text": text, "name": agent.name})
                history_text += f"{agent.name}: {text}\n"
            except Exception as e:
                self.log(f"Agent Error ({key}): {e}")
                script.append(
                    {"speaker": "System", "text": f"Error: {e}", "name": "System"}
                )

        self.log(f"Script generated: {len(script)} lines. Starting TTS...")

        import uuid

        for idx, line in enumerate(script):
            if line["speaker"] == "System":
                continue
            try:
                self.log(f"Synthesizing line {idx+1}")
                audio_bytes = self._synthesize_line(line["text"], line["speaker"])
                filename = f"{uuid.uuid4()}.mp3"
                public_url = self._upload_audio(audio_bytes, filename)
                line["audio_url"] = public_url
            except Exception as e:
                self.log(f"TTS Error line {idx+1}: {e}")
                line["audio_url"] = ""

        return {"cast": active_cast, "script": script, "debug_log": self.debug_logs}


class SimpleAgentWrapper:
    """Simple wrapper for a chat model."""

    def __init__(self, name, model):
        """Initialize with name and chat model."""
        self.name = name
        self.chat = model.start_chat()
