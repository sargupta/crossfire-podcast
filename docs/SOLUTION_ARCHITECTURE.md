# CROSSFIRE Solution Architecture

## Enterprise Solution Diagram

![CROSSFIRE Solution Architecture](images/solution_architecture.png)

This diagram represents the complete **Solution Architecture** for the CROSSFIRE platform, designed following **Google Cloud Architecture Framework** principles.

```mermaid
flowchart TB
    %% Definitions and Styles
    classDef client fill:#e8f0fe,stroke:#1a73e8,stroke-width:2px;
    classDef network fill:#f1f3f4,stroke:#5f6368,stroke-width:2px,stroke-dasharray: 5 5;
    classDef app fill:#e6f4ea,stroke:#34a853,stroke-width:2px;
    classDef ai fill:#f3e8fd,stroke:#9334e6,stroke-width:2px;
    classDef data fill:#fce8e6,stroke:#ea4335,stroke-width:2px;
    classDef ops fill:#fff8e1,stroke:#fbbc04,stroke-width:2px;

    %% TOP LAYER: ACCESS & CLIENTS
    subgraph Access_Layer ["📱 Client Access Layer"]
        direction TB
        Web([💻 Web Client<br/>Next.js/React])
        Mobile([📱 Mobile Client<br/>iOS/Android])
    end

    %% NETWORK LAYER
    subgraph Network_Layer ["🌐 Network & Content Delivery"]
        GLB{{"⚖️ Global Load Balancer<br/>Cloud Load Balancing"}}
        CDN[("⚡ Cloud CDN<br/>Edge Caching")]
    end

    %% SERVICE LAYER
    subgraph Service_Layer ["⚙️ Application Service Layer"]
        subgraph Cloud_Run ["🚀 Cloud Run (Serverless Compute)"]
            FE["Frontend Service<br/>Next.js SSR"]
            BE["Backend Service<br/>FastAPI / Python"]
            WS["WebSocket Handler<br/>Real-time Events"]
        end
    end

    %% INTELLIGENCE LAYER
    subgraph Intelligence_Layer ["🧠 Intelligence & Orchestration"]
        subgraph Agent_Engine ["🤖 Agent Engine (Runtime)"]
            Orch["🎼 Production Orchestrator"]
            
            subgraph Agents ["Debate Agents"]
                A1["🛡️ Shakti<br/>(Moderator)"]
                A2["🏛️ Sovereignist"]
                A3["🚀 Reformist"]
                A4["🔬 Technocrat"]
                A5["❤️ Humanist"]
            end
        end
        
        subgraph AI_Services ["🔮 AI Services"]
            Gemini["✨ Gemini 2.0 Flash<br/>(LLM)"]
            Vertex["✅ Vertex AI<br/>Evaluation"]
            Filter["🛡️ Safety Filter<br/>Guardrails"]
            TTS["🗣️ Cloud TTS<br/>Audio Synthesis"]
        end
    end

    %% DATA LAYER
    subgraph Data_Layer ["💾 Data & Persistence"]
        SessionStore[("🗄️ Session Store<br/>Managed Memory")]
        AssetStore[("📦 Artifact Store<br/>Google Cloud Storage")]
    end

    %% OPERATIONS LAYER
    subgraph Ops_Layer ["🛠️ Operations & Observability"]
        direction TB
        Log["📜 Cloud Logging"]
        Mon["📈 Cloud Monitoring"]
        Trace["🕵️ Cloud Trace"]
    end

    %% CONNECTIONS
    Web & Mobile ==> GLB
    GLB ==> CDN
    CDN ==> FE
    GLB ==> BE
    
    FE <==> |"WSS / Real-time"| WS
    BE <==> WS
    
    WS ==> Orch
    Orch ==> Agents
    
    Agents <==> |"Generate (Stream)"| Gemini
    Orch ==> |"Validate"| Vertex
    Orch ==> |"Check"| Filter
    
    FE ==> |"Audio Req"| TTS
    
    Orch ==> |"Persist State"| SessionStore
    Orch ==> |"Archive"| AssetStore
    
    %% TELEMETRY
    Cloud_Run -.-> |"Metrics/Logs"| Ops_Layer
    Agent_Engine -.-> |"Tracing"| Ops_Layer
    AI_Services -.-> |"Audit"| Ops_Layer

    %% Styling Application
    class Web,Mobile client;
    class GLB,CDN network;
    class FE,BE,WS app;
    class Orch,A1,A2,A3,A4,A5,Gemini,Vertex,Filter ai;
    class SessionStore,AssetStore data;
    class Log,Mon,Trace ops;
```

## Architectural Decisions

### 1. Hybrid Compute Strategy
Leverages **Cloud Run** for stateless application serving (Frontend/Backend) to ensure zero-scale cost and instant burst capability, while utilizing the specialized **Agent Engine** for long-running, stateful agent processes.

### 2. Event-Driven Real-time Architecture
Uses **WebSocket** connections terminated at the service layer to provide <200ms latency for debate streams, essential for the "live" feel of the platform.

### 3. Multi-Layer Intelligence
Separates **Generation** (Gemini) from **Evaluation** (Vertex AI) to ensure independent quality checks. The **Safety Filter** acts as a strict gateway before any content reaches the user.

### 4. Observability-First Design
Instrumentation is baked into the core `Orchestrator` and `Agent` classes, ensuring that every AI decision, latency spike, and quality score is captured in **Cloud Operations Suite**.

---

**Generated**: December 24, 2024
**Standard**: Google Cloud Enterprise Architecture
