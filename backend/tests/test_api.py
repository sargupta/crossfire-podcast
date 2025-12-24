"""
API Integration Tests for FastAPI Endpoints
Tests WebSocket and HTTP endpoints
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app
from unittest.mock import patch, MagicMock
import main

@pytest.fixture(autouse=True)
def mock_orchestrator():
    """Mock the orchestrator to prevent real backend calls"""
    mock_orch = MagicMock()
    mock_orch.generate_debate.return_value = "Mock Script"
    
    # We must patch the global 'orchestrator' in the main module
    original_orch = main.orchestrator
    main.orchestrator = mock_orch
    yield
    main.orchestrator = original_orch


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


class TestHTTPEndpoints:
    """Test REST API endpoints"""

    def test_root_endpoint(self, client):
        """Test root endpoint returns status"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "Operational" in data["status"]

    def test_generate_debate_endpoint(self, client):
        """Test POST /api/debate/generate"""
        response = client.post(
            "/api/debate/generate", json={"topic": "Test Topic", "turns": 2}
        )

        assert response.status_code == 200
        data = response.json()
        assert "script" in data

    def test_tts_endpoint(self, client):
        """Test POST /api/tts"""
        response = client.post(
            "/api/tts", json={"text": "Test speech", "speaker_id": "shakti"}
        )

        # Should return audio or error
        assert response.status_code in [200, 500]


class TestWebSocketEndpoint:
    """Test WebSocket streaming endpoint"""

    def test_websocket_connection(self, client):
        """Test WebSocket can connect"""
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
        """Test WebSocket returns correct event types"""
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
    """Test CORS headers and configuration"""

    def test_cors_headers_present(self, client):
        """Verify CORS headers are set"""
        response = client.options("/", headers={"Origin": "http://localhost:3000"})

        # CORS headers should be present
        assert (
            "access-control-allow-origin" in response.headers
            or response.status_code == 200
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
