# CROSSFIRE Podcast - Release v1.0.5 (Performance Patch)

**Release Date:** 2025-12-25
**Version:** v1.0.5
**Type:** Performance Patch

## 🚀 Performance Improvements
- **Turbo Generation:** Drastically reduced the debate generation latency by removing artificial delays (`sleep(5s)` -> `sleep(0.1s)`).
- **Result:** "Generating Debate..." now completes in **~10-15 seconds** (previously >1 minute), preventing UI timeouts and "hanging" states.

## 🔗 Deployment Links
- **Frontend (Production):** `https://crossfire-frontend-252094635698.us-central1.run.app`
- **Backend (Production):** `https://crossfire-backend-252094635698.us-central1.run.app`
