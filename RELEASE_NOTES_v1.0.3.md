# CROSSFIRE Podcast - Release v1.0.3

**Release Date:** 2025-12-25
**Version:** v1.0.3

## 🚀 New Features

### 🌐 Frontend Deployment (Production)
- **Deployed to Cloud Run:** The Next.js frontend is now fully containerized and deployed to Google Cloud Run.
- **Auto-Connection:** Builds are configured to automatically connect to the correct backend environment (Staging vs Production) via build-time `NEXT_PUBLIC_API_URL` injection.
- **Public Access:** The service is configured for public unauthenticated access.

### 🎙️ Audio Generation
- **Demo Script:** `demo_debate.py` now produces actual MP3 audio files using Google Cloud TTS.
- **Streaming Audio:** The backend streaming endpoint now includes base64-encoded audio chunks alongside text.

## 🛠️ Bug Fixes & Stability

- **Vertex AI Initialization:** Fixed an issue where ADK Agents would fallback to hardcoded text because `vertexai.init()` was missing in the orchestrator.
- **CI/CD Reliability:** Fixed a critical test regression (`tests/test_api.py`) that was blocking deployments.
- **Authentication:** Resolved 403 Forbidden errors by explicitly adding `--allow-unauthenticated` to Cloud Run deployments.

## 🔗 Deployment Links

- **Frontend (Production):** `https://crossfire-frontend-252094635698.us-central1.run.app`
- **Backend (Production):** `https://crossfire-backend-252094635698.us-central1.run.app`
