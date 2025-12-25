# CROSSFIRE System Architecture

## Production Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
│  ┌──────────────────────────┐          ┌───────────────────────────────┐   │
│  │   Next.js Frontend       │          │   WebSocket Client            │   │
│  │   React 18 + TypeScript  │◄─────────┤   Real-time Streaming         │   │
│  └──────────┬───────────────┘          └──────────────┬────────────────┘   │
└─────────────┼──────────────────────────────────────────┼───────────────────┘
              │ HTTPS/WSS                                │
              ▼                                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            API GATEWAY LAYER                                 │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    FastAPI Backend (Python 3.13)                      │  │
│  │  ┌────────────────┐  ┌──────────────┐  ┌─────────────────────────┐  │  │
│  │  │  HTTP Routes   │  │  WebSocket   │  │   CORS Middleware       │  │  │
│  │  │  /api/metrics  │  │  Handlers    │  │   Security              │  │  │
│  │  └────────────────┘  └──────────────┘  └─────────────────────────┘  │  │
│  └──────────────────────────────┬───────────────────────────────────────┘  │
└─────────────────────────────────┼──────────────────────────────────────────┘
                                  │ JSON/Stream Events
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ORCHESTRATION LAYER                                   │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │             Production Orchestrator (74% Coverage)                  │    │
│  │                                                                     │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐ │    │
│  │  │  Initialize  │─▶│   Stream     │─▶│  Generate Intro/Turn/   │ │    │
│  │  │  5 Agents    │  │   Manager    │  │  Conclusion              │ │    │
│  │  └──────────────┘  └──────────────┘  └──────────────────────────┘ │    │
│  └────────────┬────────────────┬──────────────────┬─────────────────┘    │
│               │                │                  │                        │
│               ▼                ▼          ▼       ▼                         │
│  ┌─────────────────┐ ┌─────────────────┐ ┌──────────────────────────┐    │
│  │ Managed Session │ │ Quality         │ │ Observability Module     │    │
│  │ Service         │ │ Evaluator       │ │ (71% Coverage)           │    │
│  │ (72% Coverage)  │ │ (52% Coverage)  │ │                          │    │
│  │                 │ │                 │ │ ┌──────┐ ┌──────┐        │    │
│  │ • create()      │ │ • Coherence 96% │ │ │Logger│ │Tracer│        │    │
│  │ • update()      │ │ • Safety 92%    │ │ └──────┘ └──────┘        │    │
│  │ • get_history() │ │ • Toxicity 12%  │ │ ┌─────────────┐          │    │
│  │ • close()       │ │ • Safety Filter │ │ │   Metrics   │          │    │
│  │                 │ │                 │ │ └─────────────┘          │    │
│  └─────────────────┘ └─────────────────┘ └──────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ Agent API Calls
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                             AGENT LAYER (ADK)                                │
│                                                                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────┐ │
│  │   Shakti   │  │Sovereignist│  │ Reformist  │  │ Technocrat │  │Human │ │
│  │ Moderator  │  │Traditional │  │Revolution  │  │  Logical   │  │-ist  │ │
│  │            │  │            │  │            │  │            │  │      │ │
│  │ • Intro    │  │ • Defend   │  │ • Disrupt  │  │ • Data     │  │•Emot │ │
│  │ • Control  │  │ • Gatekeeper│  │ • Vision   │  │ • Facts    │  │-ion  │ │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └───┬──┘ │
└────────┼───────────────┼──────────────┼───────────────┼─────────────┼─────┘
         │               │              │               │             │
         └───────────────┴──────────────┴───────────────┴─────────────┘
                                  │
                                  │ AI API Calls
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            AI SERVICES LAYER                                 │
│                                                                              │
│  ┌──────────────────────────────────┐     ┌──────────────────────────────┐ │
│  │    Gemini 2.0 Flash (LLM)        │     │   Vertex AI Evaluation      │ │
│  │                                  │     │                             │ │
│  │ • Natural Language Generation    │     │ • Quality Scoring           │ │
│  │ • Context Understanding          │     │ • Safety Assessment         │ │
│  │ • Agent Responses                │     │ • Trajectory Analysis       │ │
│  └──────────────────────────────────┘     └──────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ Deployed On
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      GOOGLE CLOUD PLATFORM (GCP)                             │
│                                                                              │
│  ┌────────────────────────┐          ┌──────────────────────────────┐      │
│  │   Agent Engine         │          │   Cloud Run                  │      │
│  │   Managed Runtime      │          │   Auto-scaling (1-10)        │      │
│  │   • 5 Agent Pods       │          │   • Backend Containers       │      │
│  │   • Auto-scaling       │          │   • Load Balancing           │      │
│  └────────────────────────┘          └──────────────────────────────┘      │
│                                                                              │
│  ┌───────────────┐  ┌───────────────────┐  ┌───────────────────────┐      │
│  │ Cloud Trace   │  │ Cloud Monitoring  │  │  Cloud Logging        │      │
│  │               │  │                   │  │                       │      │
│  │ • Request     │  │ • Custom Metrics  │  │ • Structured Logs     │      │
│  │   Tracing     │  │ • Dashboards      │  │ • Error Tracking      │      │
│  │ • Latency     │  │ • Alerts          │  │ • Audit Trail         │      │
│  └───────────────┘  └───────────────────┘  └───────────────────────┘      │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      GitHub Actions CI/CD                            │   │
│  │  Build → Test (26 tests) → Docker → Staging → Production            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘

                              DATA FLOW LEGEND
                              ════════════════
                    ────────▶  Request Flow (Client → Backend)
                    ◄────────  Response Flow (Backend → Client)
                    ─ ─ ─ ─▶  Async Events (Streaming)
                    ═══════▶  AI API Calls
                    ········▶  Observability Data
```

## Key Components

### 1. Client Layer
- **Next.js Frontend**: React-based UI with real-time updates
- **WebSocket Client**: Bidirectional communication for streaming debates

### 2. API Gateway
- **FastAPI**: High-performance Python web framework
- **CORS Middleware**: Cross-origin resource sharing
- **WebSocket Handlers**: Real-time event streaming

### 3. Orchestration Layer
**Production Orchestrator** (Central Brain):
- Coordinates all 5 agents
- Manages debate flow (intro → turns → conclusion)
- Integrates session, quality, and observability

**Managed Session Service** (Context Management):
- Persistent debate sessions
- Conversation history tracking
- Session archival to JSON

**Quality Evaluator** (Content Quality):
- Coherence scoring (>0.85 target, achieving 0.96)
- Safety assessment (>0.90 target, achieving 0.92)
- Toxicity detection (<0.20 target, achieving 0.12)
- Real-time content filtering

**Observability Module** (Monitoring):
- Structured logging (Cloud Logging compatible)
- Request tracing (Cloud Trace patterns)
- Metrics collection (debates, quality, latency)

### 4. Agent Layer (ADK)
Five distinct AI personas:
1. **Shakti** - Ruthless moderator
2. **Sovereignist** - Traditional defender
3. **Reformist** - Revolutionary disruptor
4. **Technocrat** - Data-driven analyst
5. **Humanist** - Emotional advocate

### 5. AI Services
- **Gemini 2.0 Flash**: Primary LLM for agent responses
- **Vertex AI**: Quality evaluation and safety assessment

### 6. Infrastructure (GCP)
- **Agent Engine**: Managed agent runtime with auto-scaling
- **Cloud Run**: Container deployment with 1-10 instances
- **Observability Stack**: Trace, Monitoring, Logging
- **CI/CD**: Automated testing and deployment

## Performance Metrics

| Metric | Target | Achieved |
|--------|--------|----------|
| Coherence | >0.85 | 0.96 ✅ |
| Safety | >0.90 | 0.92 ✅ |
| Toxicity | <0.20 | 0.12 ✅ |
| Test Coverage | >50% | 55% ✅ |
| Test Pass Rate | 100% | 100% ✅ |

## Scalability

```
Load Level        Instances    Response Time
─────────────────┼────────────┼──────────────
1-10 concurrent  │  1 instance│  <1s (P50)
10-50 concurrent │  2-5 inst  │  <2s (P95)
50+ concurrent   │  6-10 inst │  <5s (P99)
```

**Auto-scaling**: Min 1, Max 10, Target CPU 70%

---

*Architecture Version: 1.0.0*  
*Last Updated: December 24, 2024*
