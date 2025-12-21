# API Reference

The backend exposes a REST API via FastAPI.

## Base URL
`http://localhost:8000`

---

## Endpoints

### 1. Generate Debate
Triggers the full pipeline: Casting -> Scripting -> TTS -> Upload.

- **URL**: `/api/debate/generate`
- **Method**: `POST`
- **Content-Type**: `application/json`

#### Request Body
```json
{
  "topic": "The Future of AI: Utopia or Doom?",
  "turns": 8
}
```

#### Response (Success: 200 OK)
Returns a JSON object containing the Cast profiles and the Script with audio links.

```json
{
  "cast": [
    {
      "category_id": "technocrat",
      "name": "Dr. Nexus",
      "sub_role": "AI Safety Researcher",
      "credential": "PhD, MIT",
      "behavior": "Cold, Logical"
    },
    ...
  ],
  "script": [
    {
      "speaker": "shakti",
      "name": "Shakti",
      "text": "Welcome to Crossfire. Today, is AI our savior?",
      "audio_url": "https://storage.googleapis.com/omni-cast-assets-xyz/audio/uuid-1.mp3"
    },
    ...
  ]
}
```

### 2. Health Check
Verifies backend status.

- **URL**: `/`
- **Method**: `GET`

#### Response
```json
{
  "status": "Omni-Cast ADK Backend Operational"
}
```
