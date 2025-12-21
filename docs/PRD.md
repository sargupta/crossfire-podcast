# Product Requirements Document (PRD)
## CROSSFIRE PODCAST

**Version**: 1.0  
**Last Updated**: December 21, 2024  
**Status**: Production Ready

---

## 1. Executive Summary

**Product Name**: CROSSFIRE PODCAST  
**Product Type**: AI-Powered Content Generation Platform  
**Target Market**: Content Creators, Podcasters, Educators, Media Companies

**Vision Statement**:  
To democratize high-quality debate content creation by enabling anyone to generate broadcast-quality, multi-perspective discussions on any topic in minutes, not weeks.

---

## 2. Problem Statement

### Current Pain Points
- **Content Creation Bottleneck**: Traditional podcast production requires scheduling multiple experts, recording sessions, and extensive editing.
- **Limited Diversity of Voices**: Access to diverse expert perspectives is expensive and time-consuming.
- **Scalability Issues**: Creating content on new/trending topics quickly is nearly impossible with traditional methods.
- **Production Costs**: Professional-grade podcast production can cost $500-5000 per episode.

---

## 3. Product Goals

### Primary Goals
1. Generate a complete 5-minute podcast episode in under 60 seconds
2. Support ANY topic domain (Politics, Tech, Sports, Culture, Science)
3. Deliver broadcast-quality audio with distinct, realistic voices
4. Provide visually engaging companion experience

### Success Metrics
- **Generation Speed**: < 60s for 8-turn debate
- **Audio Quality**: MOS (Mean Opinion Score) > 4.0/5.0
- **Topic Coverage**: Successfully handle 95%+ of user-submitted topics
- **User Satisfaction**: NPS Score > 40

---

## 4. User Personas

### Persona 1: "The Indie Podcaster"
- **Name**: Alex Chen
- **Role**: Independent Content Creator
- **Pain**: Limited time and budget for guest coordination
- **Need**: Rapid content creation to maintain publishing schedule
- **Use Case**: Generate 3-4 episodes/week on trending tech topics

### Persona 2: "The Educator"
- **Name**: Dr. Priya Sharma
- **Role**: University Professor
- **Pain**: Need diverse perspectives for classroom discussion
- **Need**: Educational content that presents balanced viewpoints
- **Use Case**: Create debate episodes for students on complex topics

### Persona 3: "The Media Company"
- **Name**: Rahul Verma
- **Role**: Digital Media Manager
- **Pain**: Need to cover breaking news and trending topics instantly
- **Need**: Scalable content production pipeline
- **Use Case**: Produce daily debate shows on current events

---

## 5. Core Features

### 5.1 Dynamic Expert Casting
**Description**: AI generates 5 unique expert personas tailored to the topic.

**Requirements**:
- Cast includes: Traditionalist, Disruptor, Analyst, Empath, Moderator
- Each persona has: Name, Role, Credentials, Behavioral Traits
- Personas must be contextually relevant (e.g., "Cricket Analyst" for sports topics)

**Acceptance Criteria**:
- ✅ System generates unique personas within 10 seconds
- ✅ Personas demonstrate clear ideological/perspective differences
- ✅ Names and credentials feel authentic to the domain

### 5.2 Aggressive Debate Generation
**Description**: Create high-stakes, confrontational dialogue scripts.

**Requirements**:
- Dialogue must be punchy (< 3 sentences per turn)
- Include rhetorical attacks, fact-based arguments
- Maintain coherent conversation flow despite aggression

**Acceptance Criteria**:
- ✅ Average turn length: 20-40 words
- ✅ No generic "I agree with previous speaker" responses
- ✅ Minimum 2 direct rebuttals per persona

### 5.3 Batch Audio Synthesis
**Description**: Generate all speech audio upfront before playback.

**Requirements**:
- Use Google Cloud TTS Neural2 voices
- Voice mapping: Indian English for some personas, GB/US English for others
- Upload all audio to GCS for streaming

**Acceptance Criteria**:
- ✅ Audio generation completes before playback starts
- ✅ No buffering during episode playback
- ✅ Audio URLs are publicly accessible

### 5.4 Visual Podcast Player
**Description**: Immersive UI with animated avatars and live transcript.

**Requirements**:
- Display all 5 cast members with generated portraits
- Highlight active speaker with scale/glow animation
- Show real-time transcript of current dialogue
- Background: Studio environment image

**Acceptance Criteria**:
- ✅ Avatars react within 100ms of audio playback
- ✅ Transcript updates synchronously with audio
- ✅ UI maintains 60fps during animations

---

## 6. Non-Functional Requirements

### 6.1 Performance
- API Response Time: < 45s for full generation
- UI Load Time: < 2s on 4G connection
- Audio Streaming: < 200ms initial latency

### 6.2 Scalability
- Support 100 concurrent generations
- GCS bucket auto-scaling for storage
- CDN integration for audio delivery (future)

### 6.3 Reliability
- 99.5% uptime SLA
- Graceful degradation on API failures (fallback models)
- Automatic retry logic for transient errors

### 6.4 Security
- GCP IAM-based authentication
- Rate limiting: 10 generations/user/hour
- Content moderation filters (future)

---

## 7. Out of Scope (V1)

- Multi-language support (Hindi, Tamil, etc.)
- User accounts and authentication
- Custom voice cloning
- Real-time collaborative editing
- Mobile apps (iOS/Android)
- Video generation (faces, lip-sync)

---

## 8. Technical Dependencies

### Required Services
- Google Cloud Vertex AI (Gemini 2.0 Flash)
- Google Cloud Text-to-Speech
- Google Cloud Storage
- Next.js 14+ Frontend
- Python 3.10+ Backend

### API Quotas
- Vertex AI: 60 RPM (Requests Per Minute)
- TTS: 300 RPM
- GCS: Unlimited reads (Standard tier)

---

## 9. Roadmap

### Phase 1 (Current - V1.0)
- ✅ Core debate generation
- ✅ Indian persona avatars
- ✅ Batch audio processing
- ✅ GCS integration

### Phase 2 (Q1 2025)
- User authentication (Firebase)
- Episode library and history
- Export to MP3/WAV
- Embeddable player widget

### Phase 3 (Q2 2025)
- Multi-language support
- Custom voice training
- Video podcast generation
- Analytics dashboard

---

## 10. Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Gemini API Rate Limits | High | Medium | Implement queue system, fallback to Gemini 1.5 |
| TTS Quota Exhaustion | High | Low | Pre-purchase reserved capacity |
| Generated Content Quality | Medium | Medium | A/B test prompts, human-in-loop review |
| GCS Costs Escalation | Medium | High | Implement auto-deletion after 30 days |
| Copyright/Legal Issues | High | Low | Add content disclaimers, moderation filters |
