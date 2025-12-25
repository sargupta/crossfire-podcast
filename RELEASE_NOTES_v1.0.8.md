# CROSSFIRE Podcast - Release v1.0.8 (Critical Stability)

**Release Date:** 2025-12-25
**Version:** v1.0.8
**Type:** Full Stack Critical Patch

## 🧠 Backend (AI Logic)
- **Model Upgrade:** Capped experimental model. Switched to `gemini-1.5-flash` (Stable & Fast).
- **Impact:** Fixes the "Empty Script" issue where the AI would refuse to generate content or formatted it incorrectly.
- **Logging:** Added deep logging for Vertex AI responses to debug future issues instantly.

## 🖥️ Frontend (UI)
- **Bug Fix:** Fixed `TypeError: t.toLowerCase is not a function`.
- **Root Cause:** If the AI returned a numeric ID (e.g. `1` instead of `"1"`), the UI crashed.
- **Solution:** Added robust Type Guards (`String(id || "")`) to `getAvatar` and `getAgentColor`.

## 🔗 Status
- **System:** Fully Operational.
- **Audio:** Enabled.
