"""
FastAPI Backend Entry Point.

This module initializes the FastAPI application, sets up service orchestration
using lifespan events, and defines the API endpoints for the podcast backend.
"""

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import texttospeech
from pydantic import BaseModel

from adk_orchestrator import ADKDebateOrchestrator
from orchestrator import PodcastOrchestrator
from production_orchestrator import ProductionADKOrchestrator

# Load from project root robustly
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env.local")

# Global instances (initialized in lifespan)
orchestrator: Optional[PodcastOrchestrator] = None
adk_orchestrator: Optional[ADKDebateOrchestrator] = None
production_orch: Optional[ProductionADKOrchestrator] = None
tts_client: Optional[texttospeech.TextToSpeechClient] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initialize services on startup to prevent import-time crashes.

    This ensures that heavy services like Vertex AI and TTSClient are
    loaded lazily and robustly, preventing the container from failing
    health checks if an external service is momentarily unavailable.
    """
    global orchestrator, adk_orchestrator, production_orch, tts_client

    print("[Startup] Initializing services...")
    try:
        # Initialize services lazily
        # 1. Base Orchestrator (Vertex AI, GCS)
        try:
            orchestrator = PodcastOrchestrator()
            print("[Startup] PodcastOrchestrator initialized")
        except Exception as e:
            print(f"[Startup] Warning: PodcastOrchestrator init failed: {e}")

        # 2. ADK Orchestrator
        try:
            adk_orchestrator = ADKDebateOrchestrator()
            print("[Startup] ADKDebateOrchestrator initialized")
        except Exception as e:
            print(f"[Startup] Warning: ADKDebateOrchestrator init failed: {e}")

        # 3. Production Orchestrator (Firestore, Vertex AI)
        try:
            production_orch = ProductionADKOrchestrator()
            print("[Startup] ProductionADKOrchestrator initialized")
        except Exception as e:
            print(f"[Startup] Warning: ProductionADKOrchestrator init failed: {e}")

        # 4. TTS Client
        try:
            tts_client = texttospeech.TextToSpeechClient()
            print("[Startup] TTS Client initialized")
        except Exception as e:
            print(f"[Startup] Warning: TTS Client init failed: {e}")

    except Exception as e:
        print(f"[Startup] Critical error during initialization: {e}")
        # We don't raise here to allow the app to start and health check to pass
        # Services will fail on usage if not initialized

    yield

    # Cleanup if needed
    print("[Shutdown] Cleaning up resources...")


app = FastAPI(lifespan=lifespan)

# CORS configuration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://crossfire-backend-staging-481909.a.run.app",
    "*",  # Allow all for staging easier debugging
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DebateRequest(BaseModel):
    """Request model for generating a debate script."""

    topic: str
    turns: Optional[int] = 6


class TTSRequest(BaseModel):
    """Request model for Text-to-Speech generation."""

    text: str
    speaker_id: str


VOICE_MAP = {
    "sovereignist": "en-IN-Neural2-B",
    "reformist": "en-GB-Neural2-A",
    "technocrat": "en-US-Journey-D",
    "humanist": "en-US-Neural2-F",
    "shakti": "en-IN-Neural2-A",
}


@app.get("/")
def read_root():
    """Health check endpoint to verify service status."""
    status = {
        "status": "Omni-Cast ADK Backend Operational",
        "services": {
            "orchestrator": orchestrator is not None,
            "adk_orchestrator": adk_orchestrator is not None,
            "production_orch": production_orch is not None,
            "tts_client": tts_client is not None,
        },
    }
    return status


@app.post("/api/debate/generate")
def generate_debate(req: DebateRequest):
    """Generate a debate script using the basic orchestrator."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    try:
        script = orchestrator.generate_debate(req.topic, req.turns)
        return {"script": script}
    except Exception as e:
        print(f"Error generating debate: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tts")
def generate_tts(req: TTSRequest):
    """Generate audio from text using Google Cloud TTS."""
    if not tts_client:
        raise HTTPException(status_code=503, detail="TTS Client not initialized")
    try:
        voice_name = VOICE_MAP.get(req.speaker_id, "en-US-Neural2-D")
        language_code = "-".join(voice_name.split("-")[:2])

        input_text = texttospeech.SynthesisInput(text=req.text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code, name=voice_name
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = tts_client.synthesize_speech(
            input=input_text, voice=voice, audio_config=audio_config
        )

        from fastapi import Response

        return Response(content=response.audio_content, media_type="audio/mpeg")

    except Exception as e:
        print(f"TTS Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/api/debate/stream-adk")
async def adk_debate_stream(websocket: WebSocket):
    """Handle ADK-powered streaming debate via WebSocket.

    Real-time multiagent debate with progressive delivery.
    """
    await websocket.accept()
    if not adk_orchestrator:
        # ... (rest same, abbreviated for concise replacement)
        await websocket.send_json(
            {"type": "error", "message": "ADK Orchestrator not initialized"}
        )
        await websocket.close()
        return

    try:
        data = await websocket.receive_json()
        topic = data.get("topic", "Future of AI")
        turns = data.get("turns", 6)

        print(f"[ADK Stream] Starting debate on: {topic}")
        async for event in adk_orchestrator.generate_debate_stream(topic, turns):
            await websocket.send_json(event)

        await websocket.send_json({"type": "complete"})
        print("[ADK Stream] Debate complete")

    except WebSocketDisconnect:
        print("[ADK Stream] Client disconnected")
    except Exception as e:
        print(f"[ADK Stream] Error: {e}")
        await websocket.send_json({"type": "error", "message": str(e)})
    finally:
        pass


@app.websocket("/api/debate/stream-production")
async def production_debate_stream(websocket: WebSocket):
    """Production-grade debate stream with full observability.

    Features:
    - Persistent session management
    - Real-time quality evaluation
    - Safety filtering
    - Complete tracing and metrics
    """
    await websocket.accept()

    if not production_orch:
        await websocket.send_json(
            {"type": "error", "message": "Production Orchestrator not initialized"}
        )
        await websocket.close()
        return

    try:
        data = await websocket.receive_json()
        topic = data.get("topic", "AI Ethics")
        turns = data.get("turns", 6)

        print(f"[Production] Starting debate: {topic}")

        # Stream with production orchestrator
        async for event in production_orch.generate_debate_stream(topic, turns):
            await websocket.send_json(event)

        print("[Production] Debate complete")

    except WebSocketDisconnect:
        print("[Production] Client disconnected")
    except Exception as e:
        print(f"[Production] Error: {e}")
        await websocket.send_json({"type": "error", "message": str(e)})


@app.get("/api/metrics")
async def get_metrics():
    """Retrieve current metrics from production orchestrator."""
    if not production_orch:
        return {"status": "error", "message": "Production Orchestrator not initialized"}

    try:
        summary = production_orch.observability.metrics.get_metrics_summary()
        return {"status": "success", "metrics": summary}
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    import uvicorn

    # Use PORT env var for Cloud Run compatibility if running directly
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)  # nosec
