# CROSSFIRE Podcast - Release v1.0.6 (Frontend Stability)

**Release Date:** 2025-12-25
**Version:** v1.0.6
**Type:** Frontend Patch

## 🐛 Bug Fixes
- **Frontend Crash (Hydration Mismatch):** Fixed a "Client-side Exception" caused by random layout generation (`Math.random()`) in the background particle effect.
- **Solution:** `FloatingParticles` now render only after the component has mounted on the client, ensuring server-client consistency.

## 🔗 Deployment Links
- **Frontend (Production):** `https://crossfire-frontend-252094635698.us-central1.run.app` (Will work after this deploy completes)
- **Backend (Production):** `https://crossfire-backend-252094635698.us-central1.run.app`
