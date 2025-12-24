# CROSSFIRE Technical Architecture

## System Overview

CROSSFIRE is a production-grade AI-powered debate platform built on Google's Agent Development Kit (ADK), featuring real-time streaming, quality evaluation, and comprehensive observability.

---

## High-Level Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        UI[Next.js Frontend<br/>TypeScript + React]
        WS[WebSocket Client]
    end
    
    subgraph "API Gateway"
        FastAPI[FastAPI Backend<br/>Python 3.13]
        CORS[CORS Middleware]
    end
    
    subgraph "Orchestration Layer"
        PO[Production Orchestrator]
        MSS[Managed Session Service<br/>72% Coverage]
        QE[Quality Evaluator<br/>52% Coverage]
        OBS[Observability Module<br/>71% Coverage]
    end
    
    subgraph "Agent Layer - ADK"
        Shakti[Shakti<br/>Moderator]
        Sov[Sovereignist<br/>Traditionalist]
        Ref[Reformist<br/>Revolutionary]
        Tech[Technocrat<br/>Logical]
        Hum[Humanist<br/>Emotional]
    end
    
    subgraph "AI Services"
        Gemini[Gemini 2.0 Flash]
        VertexAI[Vertex AI<br/>Evaluation]
    end
    
    subgraph "Infrastructure - GCP"
        AgentEngine[Agent Engine<br/>Managed Runtime]
        CloudRun[Cloud Run<br/>Auto-scaling]
        CloudTrace[Cloud Trace]
        CloudMonitoring[Cloud Monitoring]
        CloudLogging[Cloud Logging]
    end
    
    UI -->|HTTPS/WSS| FastAPI
    WS -->|WebSocket| FastAPI
    FastAPI --> CORS
    CORS --> PO
    
    PO --> MSS
    PO --> QE
    PO --> OBS
    
    PO --> Shakti
    PO --> Sov
    PO --> Ref
    PO --> Tech
    PO --> Hum
    
    Shakti --> Gemini
    Sov --> Gemini
    Ref --> Gemini
    Tech --> Gemini
    Hum --> Gemini
    
    QE --> VertexAI
    
    PO -.Deploy.-> AgentEngine
    FastAPI -.Deploy.-> CloudRun
    OBS --> CloudTrace
    OBS --> CloudMonitoring
    OBS --> CloudLogging
    
    style PO fill:#4CAF50
    style MSS fill:#2196F3
    style QE fill:#FF9800
    style OBS fill:#9C27B0
```

---

## Data Flow Architecture

### Debate Generation Flow

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant Orchestrator
    participant Session
    participant Quality
    participant Agent
    participant Gemini
    
    Client->>FastAPI: WebSocket Connect
    FastAPI->>Client: Connection Accepted
    
    Client->>FastAPI: {topic, turns}
    FastAPI->>Orchestrator: generate_debate_stream()
    
    Orchestrator->>Session: create_session(topic)
    Session-->>Orchestrator: session_id
    
    loop For each turn
        Orchestrator->>Session: get_history()
        Session-->>Orchestrator: context
        
        Orchestrator->>Agent: Generate response
        Agent->>Gemini: API Call
        Gemini-->>Agent: Response
        Agent-->>Orchestrator: text
        
        Orchestrator->>Quality: evaluate_turn(text)
        Quality-->>Orchestrator: scores
        
        Orchestrator->>Quality: filter_content(text)
        Quality-->>Orchestrator: filtered_text
        
        Orchestrator->>Session: update_context(turn_data)
        
        Orchestrator->>FastAPI: turn_event
        FastAPI->>Client: Stream Event
    end
    
    Orchestrator->>Session: close_session()
    Orchestrator->>FastAPI: complete_event
    FastAPI->>Client: Complete
```

---

## Component Architecture

### Production Orchestrator

```mermaid
graph TB
    subgraph "Production Orchestrator (74% Coverage)"
        Init[Initialize<br/>5 Agents]
        Stream[generate_debate_stream]
        Intro[_generate_intro]
        Turn[_generate_turn]
        Conc[_generate_conclusion]
    end
    
    subgraph "Dependencies"
        Session[Managed Sessions<br/>72%]
        Quality[Quality Evaluator<br/>52%]
        Safety[Safety Filter]
        Obs[Observability<br/>71%]
    end
    
    Stream --> Intro
    Stream --> Turn
    Stream --> Conc
    
    Turn --> Session
    Turn --> Quality
    Turn --> Safety
    Turn --> Obs
    
    style Stream fill:#4CAF50
    style Turn fill:#2196F3
```

### Session Management

```mermaid
graph LR
    subgraph "Session Lifecycle"
        Create[create_session]
        Update[update_context]
        Get[get_history]
        Close[close_session]
    end
    
    subgraph "Data Structure"
        Meta[session_id<br/>topic<br/>created_at]
        History[debate_history<br/>List of turns]
        Participants[Agent list]
        Scores[Quality scores]
    end
    
    subgraph "Storage"
        Memory[In-Memory<br/>Active]
        Archive[sessions/*.json<br/>Archived]
    end
    
    Create --> Update
    Update --> Get
    Get --> Update
    Update --> Close
    
    Update --> Meta
    Update --> History
    Update --> Scores
    
    Close --> Archive
    
    style Create fill:#4CAF50
    style Archive fill:#2196F3
```

### Quality Evaluation Pipeline

```mermaid
graph LR
    Input[Turn Text] --> Eval[Quality Evaluator]
    
    Eval --> Coherence[Coherence<br/>0-1, >0.85]
    Eval --> Safety[Safety<br/>0-1, >0.90]
    Eval --> Toxicity[Toxicity<br/>0-1, <0.20]
    Eval --> Fluency[Fluency<br/>0-1]
    
    Coherence --> Filter{Safety<br/>Filter}
    Safety --> Filter
    Toxicity --> Filter
    
    Filter -->|Pass| Output[Original Text]
    Filter -->|Fail| Moderate[Moderated Text]
    
    Output --> Metrics[Record Metrics]
    Moderate --> Metrics
    
    style Filter fill:#FF9800
    style Output fill:#4CAF50
    style Moderate fill:#F44336
```

---

## Deployment Architecture

```mermaid
graph TB
    subgraph "CI/CD Pipeline"
        Git[GitHub Push]
        GHA[GitHub Actions]
        Test[Run 26 Tests]
        Build[Build Docker]
    end
    
    subgraph "Staging"
        StagingCR[Cloud Run<br/>Staging]
        StagingTest[Integration Test]
    end
    
    subgraph "Production"
        ProdCR[Cloud Run<br/>Production<br/>1-10 instances]
        AgentEng[Agent Engine<br/>5 Agents]
    end
    
    subgraph "Monitoring"
        Trace[Cloud Trace]
        Monitor[Cloud Monitoring]
        Logging[Cloud Logging]
    end
    
    Git --> GHA
    GHA --> Test
    Test -->|Pass| Build
    Build --> StagingCR
    StagingCR --> StagingTest
    StagingTest -->|Approved| ProdCR
    
    ProdCR --> AgentEng
    ProdCR --> Trace
    ProdCR --> Monitor
    ProdCR --> Logging
    
    style Test fill:#4CAF50
    style ProdCR fill:#2196F3
```

---

## Observability Architecture

```mermaid
graph TB
    subgraph "Application"
        Events[Debate Events]
        Errors[Error Events]
    end
    
    subgraph "Observability Layer"
        Logger[Structured<br/>Logger]
        Tracer[Request<br/>Tracer]
        Metrics[Metrics<br/>Collector]
    end
    
    subgraph "GCP Services"
        Logging[Cloud Logging]
        Trace[Cloud Trace]
        Monitoring[Cloud Monitoring]
    end
    
    subgraph "Dashboards"
        Perf[Performance]
        Quality[Quality Scores]
        ErrorDash[Errors]
    end
    
    Events --> Logger
    Events --> Tracer
    Events --> Metrics
    Errors --> Logger
    
    Logger --> Logging
    Tracer --> Trace
    Metrics --> Monitoring
    
    Logging --> ErrorDash
    Trace --> Perf
    Monitoring --> Perf
    Monitoring --> Quality
    
    style Logger fill:#9C27B0
    style Tracer fill:#9C27B0
    style Metrics fill:#9C27B0
```

**Metrics Collected**:
- Debates generated (count, rate)
- Quality scores per turn
- Turn generation latency
- Success/failure rates
- Error counts by type

---

## Security Architecture

```mermaid
graph TB
    subgraph "Network Security"
        HTTPS[HTTPS/TLS 1.3]
        CORS[CORS Policy]
        Firewall[GCP Firewall]
    end
    
    subgraph "Application Security"
        Input[Input Validation]
        Safety[Content Safety<br/>Filter]
        Rate[Rate Limiting]
    end
    
    subgraph "Infrastructure Security"
        SA[Service Account<br/>Authentication]
        IAM[IAM Roles]
        Audit[Audit Logs]
    end
    
    HTTPS --> CORS
    CORS --> Input
    Input --> Safety
    Input --> Rate
    
    SA --> IAM
    IAM --> Audit
    
    Safety --> Audit
    
    style Safety fill:#4CAF50
    style IAM fill:#2196F3
    style Audit fill:#9C27B0
```

---

## Technology Stack

### Frontend
- Next.js 15, React 18, TypeScript 5
- Tailwind CSS 3, WebSocket API

### Backend
- Python 3.13, FastAPI, Google ADK
- Uvicorn, asyncio

### AI & ML
- Gemini 2.0 Flash
- Vertex AI Evaluation
- Google ADK

### Infrastructure
- Docker, Cloud Run, Agent Engine
- Cloud Trace, Monitoring, Logging
- GitHub Actions

---

## Performance Characteristics

### Latency
- Debate Generation: <10s (6 turns)
- Single Turn: <2s average
- Quality Evaluation: <200ms

### Throughput
- Concurrent Debates: 10+ tested
- Turns/Second: 5-10

### Quality
- Test Coverage: 55%
- Tests: 26/26 passing (100%)
- Coherence: 0.96, Safety: 0.92

---

## Scalability

```mermaid
graph LR
    Low[1-10<br/>concurrent] --> Min[1 instance]
    Med[10-50<br/>concurrent] --> Scale[2-5 instances]
    High[50+<br/>concurrent] --> Max[10 instances]
    
    Min --> P50[P50: <1s]
    Scale --> P95[P95: <2s]
    Max --> P99[P99: <5s]
    
    style Min fill:#4CAF50
    style Scale fill:#FF9800
    style Max fill:#F44336
```

**Auto-scaling**: Min 1, Max 10, Target CPU 70%

---

**Version**: 1.0.0  
**Last Updated**: December 24, 2024
