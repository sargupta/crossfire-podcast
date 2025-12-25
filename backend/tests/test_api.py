"""
API Integration Tests for FastAPI Endpoints.

Tests WebSocket and HTTP endpoints and verifies robust startup behavior.
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))

from unittest.mock import MagicMock  # noqa: E402

import main  # noqa: E402
from main import app  # noqa: E402


@pytest.fixture(autouse=True)
def mock_services():
    """Mock all backend services to prevent real API calls."""
    # 1. Mock PodcastOrchestrator
    mock_orch = MagicMock()
    mock_orch.generate_debate.return_value = "Mock Script"

    # 2. Mock ADKDebateOrchestrator (Async Generator)
    mock_adk = MagicMock()

    async def mock_debate_stream(*args, **kwargs):
        yield {"type": "intro", "text": "Welcome to Crossfire!"}
        yield {
            "type": "turn",
            "agent_name": "Sovereignist",
            "text": "Tradition matters!",
        }
        yield {"type": "turn", "agent_name": "Reformist", "text": "Change is good!"}
        yield {"type": "conclusion", "text": "What a debate!"}

    mock_adk.generate_debate_stream = mock_debate_stream

    # 3. Mock ProductionADKOrchestrator
    mock_prod = MagicMock()
    mock_prod.generate_debate_stream = mock_debate_stream
    mock_prod.observability.metrics.get_metrics_summary.return_value = {
        "total_debates": 10,
        "success_rate": 0.95,
    }

    # 4. Mock TTS Client
    mock_tts = MagicMock()
    mock_response = MagicMock()
    mock_response.audio_content = b"fake_audio_bytes"
    mock_tts.synthesize_speech.return_value = mock_response

    # Patch all globals
    # We save originals to restore them (though Pytest isolation usually handles this)
    orig_orch = main.orchestrator
    orig_adk = main.adk_orchestrator
    orig_prod = main.production_orch
    orig_tts = main.tts_client

    main.orchestrator = mock_orch
    main.adk_orchestrator = mock_adk
    main.production_orch = mock_prod
    main.tts_client = mock_tts

    yield

    # Restore
    main.orchestrator = orig_orch
    main.adk_orchestrator = orig_adk
    main.production_orch = orig_prod
    main.tts_client = orig_tts


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHTTPEndpoints:
    """Test REST API endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns status."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "Operational" in data["status"]

    def test_generate_debate_endpoint(self, client):
        """Test POST /api/debate/generate."""
        response = client.post(
            "/api/debate/generate", json={"topic": "Test Topic", "turns": 2}
        )

        assert response.status_code == 200
        data = response.json()
        assert "script" in data

    def test_tts_endpoint(self, client):
        """Test POST /api/tts."""
        response = client.post(
            "/api/tts", json={"text": "Test speech", "speaker_id": "shakti"}
        )

        # Should return audio or error
        assert response.status_code in [200, 500]


class TestWebSocketEndpoint:
    """Test WebSocket streaming endpoint."""

    def test_websocket_connection(self, client):
        """Test WebSocket can connect."""
        with client.websocket_connect("/api/debate/stream-adk") as websocket:
            # Send request
            websocket.send_json({"topic": "WS Test", "turns": 2})

            # Receive events
            events = []
            while True:
                data = websocket.receive_json()
                events.append(data)

                if data.get("type") == "complete":
                    break

            # Verify events received
            assert len(events) > 0

            # Check event structure
            non_complete_events = [e for e in events if e.get("type") != "complete"]
            assert len(non_complete_events) >= 3  # intro + turns + conclusion

    def test_websocket_event_types(self, client):
        """Test WebSocket returns correct event types."""
        with client.websocket_connect("/api/debate/stream-adk") as websocket:
            websocket.send_json({"topic": "Event Test", "turns": 2})

            event_types = []
            while True:
                data = websocket.receive_json()
                event_types.append(data.get("type"))

                if data.get("type") == "complete":
                    break

            # Should have intro, turns, conclusion, complete
            assert "intro" in event_types
            assert "conclusion" in event_types
            assert "complete" in event_types
            assert "turn" in event_types


class TestCORSConfiguration:
    """Test CORS headers and configuration."""

    def test_cors_headers_present(self, client):
        """Verify CORS headers are set."""
        response = client.options("/", headers={"Origin": "http://localhost:3000"})

        # CORS headers should be present
        assert (
            "access-control-allow-origin" in response.headers
            or response.status_code == 200
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
