from typing import List, Dict
import os
import time
from agents.manifests import AGENT_MANIFESTS
import vertexai
from vertexai.generative_models import GenerativeModel, ChatSession

# Initialize Vertex AI
# Project ID is pulled from environment variable GCP_PROJECT_ID provided by python-dotenv in main.py
# vertexai.init(project=os.getenv("GCP_PROJECT_ID"), location="us-central1")


class DebateAgent:
    def __init__(self, manifest, model: GenerativeModel):
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
        # Send system prompt as history (or use system_instruction if model supports it directly in init)
        # Gemini 1.5 Pro support system_instruction in constructor.


class PodcastOrchestrator:
    # Dynamic Casting Map
    CASTING_PROMPT = """
    For the debate topic '{topic}', Cast 5 specific experts.
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
        # 1. Initialize Vertex AI
        project_id = os.getenv("GCP_PROJECT_ID", "aipodcaster-481909")
        try:
            vertexai.init(project=project_id, location="us-central1")
        except Exception as e:
            print(f"Vertex Init Warning: {e}")

        # 2. Initialize TTS Client
        from google.cloud import texttospeech

        self.tts_client = texttospeech.TextToSpeechClient()

        # 3. Initialize Storage
        from google.cloud import storage

        self.storage_client = storage.Client()
        self.bucket_name = "omni-cast-assets-aipodcaster"  # User's actual bucket
        self._ensure_bucket()

        self.agents = {}

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
        """Uploads audio bytes to GCS and returns public URL."""
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

    def generate_cast(self, topic: str) -> tuple[List[Dict[str, str]], str]:
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
                return json.loads(text), model_name
            except Exception as e:
                print(f"Model {model_name} failed: {e}")
                continue
        return [], ""

    def generate_debate(self, topic: str, turns: int = 6) -> Dict:
        # 1. Dynamic Casting
        cast, working_model_name = self.generate_cast(topic)
        if not cast:
            raise ValueError("No agents could be cast.")

        # 2. Instantiate Agents
        self.agents = {}
        active_cast = []
        for profile in cast:
            cat_id = str(profile.get("category_id", "")).lower()
            if not cat_id:
                continue

            # Map keys
            key = cat_id
            if "sovereignist" in cat_id:
                key = "sovereignist"
            elif "reformist" in cat_id:
                key = "reformist"
            elif "technocrat" in cat_id:
                key = "technocrat"
            elif "humanist" in cat_id:
                key = "humanist"
            elif "shakti" in cat_id:
                key = "shakti"

            system_prompt = f"""
            IDENTITY: {profile['name']}
            ROLE: {profile['sub_role']}
            BEHAVIOR: {profile['behavior']}
            TOPIC: {topic}
            CONTEXT: OMNI-CAST Debate.
            
            CRITICAL INSTRUCTIONS:
            1. BE AGGRESSIVE. Attack previous speakers directly.
            2. USE FACTS AS WEAPONS. Under 3 sentences. Punchy.
            3. SHOW NO MERCY.
            """
            agent_model = GenerativeModel(
                working_model_name, system_instruction=system_prompt
            )
            self.agents[key] = SimpleAgentWrapper(profile["name"], agent_model)
            active_cast.append(profile)

        if not self.agents:
            raise ValueError("No agents instantiated.")

        # 3. Execution (Script Generation)
        script = []
        history_text = f"TOPIC: {topic}\nPANEL:\n" + "\n".join(
            [f"- {p['name']} ({p['sub_role']})" for p in active_cast]
        )

        # Host Intro
        host = self.agents.get("shakti")
        if host:
            time.sleep(5)
            resp = host.chat.send_message(
                f"Start the debate. Introduce the topic '{topic}' and the panel."
            )
            text = resp.text.strip()
            script.append({"speaker": "shakti", "text": text, "name": host.name})
            history_text += f"{host.name}: {text}\n"

        # Rounds
        order = ["sovereignist", "reformist", "technocrat", "humanist"]
        for i in range(turns):
            time.sleep(5)
            key = order[i % len(order)]
            agent = self.agents.get(key)
            if not agent:
                continue

            prompt = (
                f"The conversation so far:\n{history_text}\nIt is your turn. React."
            )
            resp = agent.chat.send_message(prompt)
            text = resp.text.strip()

            script.append({"speaker": key, "text": text, "name": agent.name})
            history_text += f"{agent.name}: {text}\n"

        # 4. Batch TTS & Upload (The "Generate Entire Podcast" Phase)
        print("Script generated. Starting Batch Audio Synthesis...")
        import uuid

        for idx, line in enumerate(script):
            try:
                print(f"  Synthesizing line {idx+1}/{len(script)}: {line['speaker']}")
                audio_bytes = self._synthesize_line(line["text"], line["speaker"])
                filename = f"{uuid.uuid4()}.mp3"
                print(f"  Uploading {filename} to GCS...")
                public_url = self._upload_audio(audio_bytes, filename)
                line["audio_url"] = public_url
                print(f"  ✅ {filename} uploaded: {public_url}")
            except Exception as e:
                print(f"  ❌ Error on line {idx+1}: {e}")
                line["audio_url"] = ""  # Empty URL on failure

        return {"cast": active_cast, "script": script}


class SimpleAgentWrapper:
    def __init__(self, name, model):
        self.name = name
        self.chat = model.start_chat()
