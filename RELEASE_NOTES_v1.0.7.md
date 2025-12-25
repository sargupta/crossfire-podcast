# CROSSFIRE Podcast - Release v1.0.7 (Frontend Critical Patch)

**Release Date:** 2025-12-25
**Version:** v1.0.7
**Type:** Frontend Critical Patch

## 🐛 Bug Fixes
- **Frontend Crash (SSR Mismatch):** Disabled Server-Side Rendering for `PodcastPlayer` completely.
- **Solution:** Used `next/dynamic` with `{ ssr: false }`. This forces the player to load only on the Client, bypassing all "hydration" and "server/client mismatch" errors (minified React error #418/423).
- **Impact:** The "Application error" screen will disappear.

## 🔗 Deployment Links
- **Frontend (Production):** `https://crossfire-frontend-252094635698.us-central1.run.app`
