# System Architecture

## Overview
**CROSSFIRE PODCAST** is a hybrid AI application that combines a real-time Next.js frontend with a Python-based Agent Orchestrator. It leverages Google Gemini for intelligence and Google Cloud Storage for media delivery.

## High-Level Data Flow

```mermaid
graph TD
    User[User] -->|1. Enter Topic| FE[Next.js Frontend]
    FE -->|2. POST /api/debate/generate| BE[FastAPI Backend]
    
    subgraph "Backend Orchestrator"
        BE -->|3. Cast Experts| Gemini[Vertex AI (Gemini 2.0)]
        Gemini -->|4. Return Personas| BE
        BE -->|5. Generate Script| Gemini
        Gemini -->|6. Return Dialogue| BE
        BE -->|7. Batch TTS Synthesis| TTS[Google Cloud TTS]
        TTS -->|8. Upload MP3s| GCS[Google Cloud Storage]
    end
    
    GCS -->|9. Public URLs| BE
    BE -->|10. JSON Response (Script + Audio Links)| FE
    FE -->|11. Play Audio & Animate Avatars| User
```

## Tech Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS + Custom Glassmorphism
- **Animation**: Framer Motion
- **State Management**: React Hooks (local state)

### Backend
- **Server**: FastAPI (Python 3.10+)
- **AI Model**: Google Gemini 2.0 Flash Exp (via Vertex AI SDK)
- **Speech**: Google Cloud Text-to-Speech (Neural2 Voices)
- **Storage**: Google Cloud Storage (Bucket: `omni-cast-assets-[project-id]`)

## Key Components

### 1. PodcastOrchestrator (`backend/orchestrator.py`)
The brain of the operation.
- **Casting Engine**: Uses a specialized prompt to generate 5 unique personas based on the topic.
- **Script Generator**: Runs a round-robin debate simulation where agents "react" to previous turns.
- **Batch Processor**: Synthesizes all audio lines in parallel (conceptually) and uploads them to GCS.

### 2. PodcastPlayer (`components/PodcastPlayer.tsx`)
The visual interface.
- **Dynamic Grid**: Adapts to the number of cast members.
- **Audio Sync**: Plays audio files sequentially using native HTML5 Audio.
- **Visualizer**: Uses `framer-motion` to pulse the avatar of the active speaker.
