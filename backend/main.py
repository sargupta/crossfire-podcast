from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from google.cloud import texttospeech
from .orchestrator import PodcastOrchestrator
from pathlib import Path

# Load from project root robustly
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env.local")

app = FastAPI()

# CORS configuration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Services
orchestrator = PodcastOrchestrator()
tts_client = texttospeech.TextToSpeechClient()

class DebateRequest(BaseModel):
    topic: str
    turns: Optional[int] = 6

class TTSRequest(BaseModel):
    text: str
    speaker_id: str

VOICE_MAP = {
    "sovereignist": "en-IN-Neural2-B",
    "reformist": "en-GB-Neural2-A",
    "technocrat": "en-US-Journey-D",
    "humanist": "en-US-Neural2-F",
    "shakti": "en-IN-Neural2-A"
}

@app.get("/")
def read_root():
    return {"status": "Omni-Cast ADK Backend Operational"}

@app.post("/api/debate/generate")
def generate_debate(req: DebateRequest):
    try:
        script = orchestrator.generate_debate(req.topic, req.turns)
        return {"script": script}
    except Exception as e:
        print(f"Error generating debate: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tts")
def generate_tts(req: TTSRequest):
    try:
        voice_name = VOICE_MAP.get(req.speaker_id, "en-US-Neural2-D")
        language_code = "-".join(voice_name.split("-")[:2])
        
        input_text = texttospeech.SynthesisInput(text=req.text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = tts_client.synthesize_speech(
            input=input_text, voice=voice, audio_config=audio_config
        )
        
        # Return raw bytes? Or base64? 
        # FastAPI handles bytes response if we use Response class.
        from fastapi import Response
        return Response(content=response.audio_content, media_type="audio/mpeg")
        
    except Exception as e:
        print(f"TTS Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
