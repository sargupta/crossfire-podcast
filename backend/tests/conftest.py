import pytest
from unittest.mock import MagicMock
import os
import sys

# -------------------------------------------------------------------------
# SAFE GCP MOCKS
# We patch the specific attributes of the real modules.
# This avoids breaking other libraries (like anyio) that rely on
# complex internal imports within google packages.
# -------------------------------------------------------------------------

# 1. Mock Credentials (used by almost all clients)
try:
    import google.auth

    mock_creds = MagicMock()
    mock_creds.universe_domain = "googleapis.com"
    google.auth.default = MagicMock(return_value=(mock_creds, "test-project"))
except ImportError:
    pass

# Mock Storage (used in orchestrator.py)
try:
    from google.cloud import storage
    storage.Client = MagicMock()
except ImportError:
    pass

# 2. Mock TextToSpeech (used in main.py)
try:
    from google.cloud import texttospeech
    mock_tts_client = MagicMock()
    mock_response = MagicMock()
    mock_response.audio_content = b"fake_audio_content"
    mock_tts_client.synthesize_speech.return_value = mock_response
    texttospeech.TextToSpeechClient = MagicMock(return_value=mock_tts_client)
except ImportError:
    pass

# 3. Mock AI Platform (used in production_orchestrator.py)
try:
    from google.cloud import aiplatform

    aiplatform.init = MagicMock()
except ImportError:
    pass

# 4. Mock other services if needed
try:
    from google.cloud import logging

    logging.Client = MagicMock()
except ImportError:
    pass

try:
    from google.cloud import monitoring_v3

    monitoring_v3.MetricServiceClient = MagicMock()
except ImportError:
    pass

try:
    from google.cloud import trace_v1

    trace_v1.TraceServiceClient = MagicMock()
except ImportError:
    pass


@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    """Ensure environment variables are set for all tests"""
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "test-project")
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", "/dev/null")
