# McLeuker AI V9.0 — Agentic Execution Platform

A unified monorepo containing the full-stack McLeuker AI platform: an end-to-end agentic AI system with multi-layer reasoning, web automation, domain agents, and real-time execution streaming.

## Architecture

```
McLeuker_Agentic_AI/
├── apps/
│   ├── frontend/                    # Next.js 16 + TypeScript + Tailwind CSS
│   │   ├── src/
│   │   │   ├── app/                 # App Router pages (dashboard, auth, domains, etc.)
│   │   │   ├── components/
│   │   │   │   ├── agent/           # ExecutionPanel, LiveScreen, AgentSwarmPanel
│   │   │   │   ├── chat/            # AgenticExecutionPanel, ModeSelector
│   │   │   │   ├── reasoning/       # Multi-layer reasoning display
│   │   │   │   ├── workspace/       # DomainStarterPanel, WorkspaceNavigation
│   │   │   │   └── ui/             # 40+ reusable UI components
│   │   │   ├── hooks/               # useExecutionWebSocket, useConversations, etc.
│   │   │   ├── lib/                 # api.ts, agenticAPI.ts (V9 execution client)
│   │   │   ├── contexts/            # AuthContext, ChatContext, SectorContext
│   │   │   └── stores/              # Zustand state management
│   │   └── public/                  # Static assets
│   │
│   └── backend/                     # FastAPI + Python (V9 Agentic API)
│       ├── src/
│       │   ├── api/                 # main.py (V9), v2/ (legacy endpoints)
│       │   ├── core/                # ReasoningOrchestrator, settings
│       │   ├── enhancement/         # V9 Enhancement System
│       │   │   ├── domain_agents/   # Fashion, Beauty, Tech, Culture, etc.
│       │   │   ├── execution/       # ExecutionEngine, TaskDecomposer, WebExecutor
│       │   │   ├── file_analysis/   # Document, Image, Code, Data analyzers
│       │   │   └── tool_stability/  # StabilityManager, StatePersistence
│       │   ├── agentic/             # Execution orchestrator, schemas
│       │   ├── agents/              # Agent Swan, reasoning agent
│       │   ├── layers/              # Intent, Search, Action, Output layers
│       │   ├── memory/              # MemoryManager, KnowledgeGraph
│       │   ├── providers/           # Kimi provider
│       │   ├── services/            # NanoBanana, FileGeneration
│       │   ├── specialized_agents/  # DeepResearch, Document, Excel, Slides
│       │   ├── tools/               # Browser, Code, Search, File tools
│       │   └── workspace/           # ArtifactStore, CodeSandbox
│       ├── Dockerfile
│       └── requirements.txt
│
├── packages/
│   └── shared-types/                # Shared TypeScript types
├── .github/workflows/deploy.yml     # CI/CD pipeline
├── turbo.json
├── pnpm-workspace.yaml
└── package.json
```

## Tech Stack

| Component | Technology | Deployment |
|-----------|------------|------------|
| **Frontend** | Next.js 16, TypeScript, Tailwind CSS, Zustand | Vercel |
| **Backend** | FastAPI, Python 3.11, Grok AI (grok-4-1-fast-reasoning) | Railway |
| **Database** | Supabase (PostgreSQL + Auth + RLS) | Supabase Cloud |
| **AI Models** | Grok 4.1, Kimi 2.5, Gemini (Nano Banana) | xAI, Moonshot, Google |
| **Browser** | Playwright, Browserless | Railway |
| **Build** | Turborepo, PNPM | GitHub Actions |

## Three-Mode Architecture

McLeuker AI operates in three distinct modes, each optimized for different use cases:

| Mode | Internal Name | Model Config | Behavior |
|------|---------------|-------------|----------|
| **Instant** | `instant` | Kimi 2.5 (temperature 0.7) | Fast reasoning-first responses. Always thinks before answering. No content length limits. Engaging, conversational style. |
| **Auto** | `thinking` | Kimi 2.5 (thinking mode) | Full search + file generation + transparent reasoning. Comprehensive analysis with headers, tables, data. Maps to Kimi 2.5's thinking mode. |
| **Agent** | `agent` | Kimi 2.5 + Orchestrator | Full agentic execution with browser automation, code execution, and 124 specialized agents. Always reasons first, asks for clarification if needed, creates execution plan before acting. |

### Reasoning-First Architecture

All three modes follow a **reasoning-first** approach:
1. **Analyze** — Understand the user's intent and context
2. **Plan** — Determine the optimal approach (search, file generation, execution)
3. **Execute** — Only proceed with execution after reasoning is complete
4. **Verify** — Quality-check outputs before delivery

In Agent mode, if the prompt is unclear or missing information, the system will ask for clarification instead of blindly executing.

## V9 Capabilities

### Execution Engine
- **Task Decomposition** — Grok-powered planning that breaks user requests into executable steps
- **Web Automation** — Full Playwright-based browser control (navigate, click, type, scroll, screenshot)
- **Credential Management** — Encrypted credential storage for third-party service automation
- **Real-time Streaming** — SSE-based execution progress with live screenshots
- **Error Recovery** — Automatic retry with fallback strategies

### Domain Agents
Specialized agents for fashion industry intelligence:
- Fashion, Beauty, Skincare, Sustainability, Tech, Catwalk, Culture, Textile, Lifestyle

### Multi-Layer Reasoning
- Understanding → Planning → Research → Analysis → Synthesis → Writing
- Real-time reasoning transparency with sub-step display

### File Generation
- Excel, Word, PowerPoint, PDF, Markdown
- Persistent file storage with download URLs

### Image Generation
- Nano Banana (Gemini-powered) image generation, editing, and analysis

## API Endpoints

### Core
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check with feature flags |
| `/api/capabilities` | GET | Full system capabilities |
| `/api/enhancement/status` | GET | Enhancement system status |

### Chat & Reasoning
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Non-streaming chat with reasoning |
| `/api/chat/stream` | POST | SSE streaming chat |

### Execution Engine (V9)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/execute` | POST | Execute task (non-streaming) |
| `/api/execute/stream` | POST | Execute task with SSE streaming |
| `/api/execute/{task_id}` | GET | Get execution status |
| `/api/execute/active/list` | GET | List active executions |

### Image & Documents
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/image/generate` | POST | Generate image |
| `/api/image/edit` | POST | Edit image |
| `/api/image/analyze` | POST | Analyze image |
| `/api/v1/files/generate` | POST | Generate document (PDF, Excel, Word, PPTX) |
| `/api/v1/upload` | POST | Upload file |
| `/api/v1/download/{file_id}` | GET | Download generated file |
| `/api/v1/download/package` | POST | Download multiple files as ZIP package |
| `/api/v1/files/generated` | GET | List generated files |

## Quick Start

### Prerequisites
- Node.js 18+
- PNPM 9+
- Python 3.11+

### Installation

```bash
git clone https://github.com/McLeuker/McLeuker_Agentic_AI.git
cd McLeuker_Agentic_AI

# Install all dependencies
pnpm install

# Set up environment variables
cp apps/frontend/.env.example apps/frontend/.env.local
cp apps/backend/.env.example apps/backend/.env
```

### Development

```bash
# Run frontend
pnpm dev:frontend

# Run backend
pnpm dev:backend
```

## Deployment

### Frontend (Vercel)
1. Import repository on [Vercel](https://vercel.com/dashboard)
2. Set **Root Directory** to `apps/frontend`
3. Add environment variables: `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`

### Backend (Railway)
1. Create project on [Railway](https://railway.app/dashboard)
2. Deploy from root — the `railway.json`, `nixpacks.toml`, and `Procfile` are configured to `cd apps/backend` before starting
3. Add environment variables (see `.env.example`)
4. The backend Dockerfile in `apps/backend/Dockerfile` includes Playwright + Chromium for browser automation

### Database (Supabase)
1. Run `apps/backend/src/agentic/schema_execution.sql` in SQL Editor
2. Run `apps/backend/src/agentic/schema_v9_migration.sql` for V9 tables

## Environment Variables

### Frontend
| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Backend API URL (Railway) |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anon key |

### Backend
| Variable | Description |
|----------|-------------|
| `XAI_API_KEY` | xAI Grok API key |
| `KIMI_API_KEY` | Moonshot Kimi API key |
| `BRAVE_API_KEY` | Brave Search API key |
| `SERPER_API_KEY` | Serper search API key |
| `PERPLEXITY_API_KEY` | Perplexity API key |
| `GEMINI_API_KEY` | Google Gemini API key |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_KEY` | Supabase service role key |
| `BROWSERLESS_API_KEY` | Browserless API key |
| `E2B_API_KEY` | E2B sandbox API key |
| `CREDENTIAL_ENCRYPTION_KEY` | 32-byte key for credential encryption |

## License

MIT License

---

**McLeuker AI — Built for the future of fashion intelligence.**
