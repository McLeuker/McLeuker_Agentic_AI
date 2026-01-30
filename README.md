# McLeuker Agentic AI Platform

**The execution-first, agentic AI system that acts as a digital team member for professionals across various industries.**

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/McLeuker/McLeuker_Agentic_AI)

---

## 🚀 Quick Start

### One-Click Deploy

**Railway (Recommended):**
1. Click the "Deploy on Railway" button above
2. Add your API keys as environment variables
3. Deploy!

**Render:**
1. Fork this repository
2. Connect to Render and select the repo
3. Render will use the `render.yaml` configuration automatically

### Local Development

```bash
# Clone the repository
git clone https://github.com/McLeuker/McLeuker_Agentic_AI.git
cd McLeuker_Agentic_AI

# Run setup script
./scripts/setup.sh

# Add your API keys to .env
nano .env

# Start the server
./scripts/start.sh
```

Or with Docker:
```bash
docker-compose up
```

---

## 1. Overview

The McLeuker Agentic AI Platform is a sophisticated backend system designed to understand complex user prompts, perform real-time research, structure information, and execute tasks to generate ready-to-use deliverables. Unlike traditional AI chatbots that provide text-only responses, this platform gets the work done, delivering outputs in formats like Excel, PDF, PowerPoint, and more.

This repository contains the complete backend source code for the platform, built with a modular, scalable, and high-performance architecture using Python and FastAPI.

## 2. Architecture

The platform is built around a **Unified Agent Orchestrator** that coordinates a multi-layer pipeline to process requests. This ensures a clear separation of concerns and a robust workflow.

```
┌─────────────────────────────────────────────────────────────┐
│                    Unified Agent Orchestrator                │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: Task Interpretation                                │
│  • Understands user intent                                   │
│  • Detects domain (fashion, tech, finance, etc.)            │
│  • Determines required outputs                               │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: LLM Reasoning                                      │
│  • GPT-4 / Grok / Perplexity integration                    │
│  • Creates execution plans                                   │
│  • Generates research questions                              │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: Web Research                                       │
│  • Multi-provider search (Google, Bing, Perplexity)         │
│  • Web scraping with Firecrawl                              │
│  • Information synthesis                                     │
├─────────────────────────────────────────────────────────────┤
│  Layer 4: Logic & Structuring                                │
│  • Transforms research into structured data                  │
│  • Creates tables, reports, presentations                    │
│  • Applies industry-specific rules                           │
├─────────────────────────────────────────────────────────────┤
│  Layer 5: Execution                                          │
│  • Excel/CSV generation                                      │
│  • PDF/Word documents                                        │
│  • PowerPoint presentations                                  │
│  • HTML dashboards                                           │
│  • Code generation                                           │
└─────────────────────────────────────────────────────────────┘
```

For a more detailed breakdown, see the [Architecture Document](./docs/ARCHITECTURE.md).

## 3. Features

- **Multi-Layer Agentic System**: A robust pipeline that mimics a human workflow: understanding, planning, researching, structuring, and executing.
- **Multi-LLM Support**: Easily switch between top-tier LLMs like OpenAI's GPT-4 and xAI's Grok.
- **Multi-Search Provider**: Google, Bing, Perplexity, Firecrawl, and more.
- **Real-Time Intelligence**: Integrated web research capabilities to provide up-to-date and relevant information.
- **Execution-First Approach**: Delivers tangible outputs (files) rather than just text, making it a true productivity tool.
- **Multi-Format Output**: Dynamically generates a wide range of professional documents:
  - **Excel (`.xlsx`) & CSV (`.csv`)**: For datasets, tables, and lists.
  - **PDF (`.pdf`) & Word (`.docx`)**: For professional reports, briefs, and summaries.
  - **PowerPoint (`.pptx`)**: For presentations and slide decks.
  - **Web (`.html`)**: For web snippets and dashboards.
  - **Code (`.py`, `.js`, etc.)**: For scripts and automation pipelines.
- **AI-Powered Search**: A standalone search platform similar to Manus AI or Perplexity for advanced information retrieval.
- **Media Services**: ElevenLabs TTS, Hugging Face models integration.
- **Scalable & Modular**: Built with Python and FastAPI for high performance and easy extension.
- **Lovable Integration Ready**: Designed with CORS and WebSocket support for seamless integration with front-end platforms like Lovable.

## 4. Technology Stack

| Component                 | Technology                                       |
| ------------------------- | ------------------------------------------------ |
| **Backend Framework**     | FastAPI                                          |
| **LLM Providers**         | OpenAI (GPT-4), Grok, Perplexity                 |
| **Search Providers**      | Google, Bing, Perplexity, Firecrawl, DuckDuckGo  |
| **Agent Orchestration**   | Custom Orchestrator                              |
| **Web Research**          | Firecrawl, BeautifulSoup, HTTPX                  |
| **File Generation**       | Pandas, OpenPyXL, ReportLab, python-pptx, python-docx |
| **Media Services**        | ElevenLabs, Hugging Face                         |
| **Data Validation**       | Pydantic                                         |
| **Server**                | Uvicorn                                          |
| **Deployment**            | Docker, Railway, Render                          |

## 5. Installation

### Option A: Using Scripts (Recommended)

```bash
# Clone the repository
git clone https://github.com/McLeuker/McLeuker_Agentic_AI.git
cd McLeuker_Agentic_AI

# Run setup script
./scripts/setup.sh

# Start the server
./scripts/start.sh
```

### Option B: Manual Setup

```bash
# Clone the repository
git clone https://github.com/McLeuker/McLeuker_Agentic_AI.git
cd McLeuker_Agentic_AI

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install the dependencies
pip install -r requirements.txt
```

### Option C: Docker

```bash
# Build and run with Docker Compose
docker-compose up

# Or build manually
docker build -t mcleuker-ai .
docker run -p 8000:8000 --env-file .env mcleuker-ai
```

## 6. Configuration

1.  **Create a `.env` file** in the root directory of the project by copying the example file:
    ```bash
    cp .env.example .env
    ```

2.  **Edit the `.env` file** to add your API keys:
    ```env
    # --- LLM Providers (at least one required) ---
    OPENAI_API_KEY="sk-..."
    GROK_API_KEY="xai-..."

    # --- Search Providers (at least one recommended) ---
    GOOGLE_SEARCH_API_KEY="..."
    BING_API_KEY="..."
    PERPLEXITY_API_KEY="pplx-..."
    FIRECRAWL_API_KEY="fc-..."

    # --- Optional Services ---
    ELEVENLABS_API_KEY="sk_..."
    HUGGINGFACE_API_KEY="hf_..."
    STRIPE_SECRET_KEY="sk_..."

    # --- Settings ---
    DEFAULT_LLM_PROVIDER="openai"
    DEBUG=True
    ```

## 7. Usage

### Running the Server

```bash
# Development mode with auto-reload
./scripts/start.sh dev

# Production mode
./scripts/start.sh prod

# Or manually
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://127.0.0.1:8000`.

### API Documentation

Once the server is running, interactive API documentation (Swagger UI) is available at:

`http://127.0.0.1:8000/docs`

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/status` | GET | Platform status |
| `/api/config/status` | GET | Configuration status |
| `/api/tasks` | POST | Create async task |
| `/api/tasks/sync` | POST | Create sync task |
| `/api/tasks/{id}` | GET | Get task status |
| `/api/chat` | POST | Chat with AI |
| `/api/search` | POST | AI-powered search |
| `/api/search/quick` | POST | Quick answer |
| `/api/research` | POST | In-depth research |
| `/api/tts` | POST | Text-to-speech |
| `/api/summarize` | POST | Text summarization |
| `/ws/{user_id}` | WebSocket | Real-time updates |

### Example API Calls

#### 1. Process a Task Synchronously

```bash
curl -X POST "http://127.0.0.1:8000/api/tasks/sync" \
-H "Content-Type: application/json" \
-d '{
  "prompt": "Create a competitor analysis and trend report for sustainable fashion brands in Europe for SS26. Export Excel and PDF."
}'
```

#### 2. Perform an AI-Powered Search

```bash
curl -X POST "http://127.0.0.1:8000/api/search" \
-H "Content-Type: application/json" \
-d '{
  "query": "latest trends in AI-driven fashion design"
}'
```

#### 3. Chat with the Agent

```bash
curl -X POST "http://127.0.0.1:8000/api/chat" \
-H "Content-Type: application/json" \
-d '{
  "message": "What are the key sustainability certifications for textiles?"
}'
```

## 8. Lovable Integration

The `lovable_integration/` folder contains ready-to-use React components for your Lovable frontend:

### Quick Setup

1. Copy `lovable_integration/McLeukerAI.tsx` to your Lovable project's `src/components/` folder
2. Update the `API_BASE_URL` in the file to your deployed backend URL
3. Use the components:

```tsx
import { 
  McLeukerChatInterface,
  McLeukerSearchInterface,
  McLeukerTaskSubmitter,
  McLeukerStatusIndicator
} from './components/McLeukerAI';

// Chat interface
<McLeukerChatInterface />

// AI Search
<McLeukerSearchInterface />

// Task submission
<McLeukerTaskSubmitter onComplete={(result) => console.log(result)} />

// Status indicator
<McLeukerStatusIndicator />
```

See `lovable_integration/QUICK_START.md` for detailed instructions.

## 9. Project Structure

```
mcleuker_agentic_ai/
├── src/
│   ├── agents/              # Execution agents
│   │   ├── orchestrator.py  # Main orchestrator
│   │   ├── excel_agent.py   # Excel/CSV generation
│   │   ├── pdf_agent.py     # PDF/Word generation
│   │   ├── ppt_agent.py     # PowerPoint generation
│   │   └── web_code_agent.py # HTML/Code generation
│   ├── layers/              # 5 core layers
│   │   ├── task_interpretation.py
│   │   ├── llm_reasoning.py
│   │   ├── web_research.py
│   │   ├── logic_structuring.py
│   │   └── execution.py
│   ├── tools/               # AI tools
│   │   ├── ai_search.py     # AI search platform
│   │   └── media_services.py # TTS, summarization
│   ├── api/                 # FastAPI endpoints
│   │   └── main.py
│   ├── models/              # Pydantic schemas
│   │   └── schemas.py
│   ├── config/              # Configuration
│   │   └── settings.py
│   └── utils/               # Utilities
│       └── llm_provider.py
├── lovable_integration/     # Frontend components
│   ├── McLeukerAI.tsx       # All-in-one component
│   └── QUICK_START.md       # Integration guide
├── scripts/                 # Utility scripts
│   ├── setup.sh
│   └── start.sh
├── docs/                    # Documentation
├── tests/                   # Test files
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose
├── railway.json             # Railway config
├── render.yaml              # Render config
├── Procfile                 # Heroku/Railway
├── requirements.txt         # Python dependencies
└── .env.example             # Environment template
```

## 10. Running Tests

```bash
pytest tests/ -v
```

## 11. Deployment

### Railway

1. Connect your GitHub repository to Railway
2. Railway will automatically detect the Dockerfile
3. Add environment variables in the Railway dashboard
4. Deploy!

### Render

1. Connect your GitHub repository to Render
2. Render will use the `render.yaml` configuration
3. Add environment variables in the dashboard
4. Deploy!

### Docker

```bash
# Build the image
docker build -t mcleuker-ai .

# Run the container
docker run -p 8000:8000 --env-file .env mcleuker-ai
```

## 12. Contributing

Contributions are welcome! Please read the [CONTRIBUTING.md](./CONTRIBUTING.md) file for details on our code of conduct and the process for submitting pull requests.

## 13. License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

---

Built with ❤️ by McLeuker AI
