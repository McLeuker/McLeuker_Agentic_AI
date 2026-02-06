# McLeuker AI - Fashion Intelligence Platform

> **The Frontier Agentic AI for Fashion, Beauty, Lifestyle, and Culture**

A next-generation AI platform combining real-time intelligence, professional file generation, and deep industry expertise with a modern monorepo architecture.

## 🏗️ Architecture

```
McLeuker AI Platform
├── Frontend (Next.js 16 + TypeScript + Tailwind)
│   └── Premium dark theme with Radix UI components
├── Backend (FastAPI + Python)
│   ├── V7 Multi-Model Orchestrator
│   │   ├── Grok (xAI) - Reasoning Brain
│   │   └── Kimi K2.5 - Execution Engine
│   ├── Search Layer (Google, Bing, Perplexity, Exa)
│   ├── Action Layer (Browserless, Firecrawl)
│   └── Output Layer (Nano Banana Images)
└── Database (Supabase)
    └── Users, Credits, Conversations, Memory
```

## 🚀 Features

### Core Capabilities

- **Dual-Model AI**: Grok for reasoning + Kimi K2.5 for execution
- **Real-time Intelligence**: X (Twitter) data access via Grok
- **Parallel Search**: Simultaneous queries across multiple providers
- **Web Automation**: Browserless.io integration for live web interaction
- **Professional Files**: E2B sandbox for Excel, PDF, and data analysis
- **Image Generation**: Nano Banana for fashion mood boards and visuals
- **Persistent Memory**: Supabase integration for user context

### Industry Focus

- Fashion & Catwalks
- Beauty & Skincare
- Textile & Sustainability
- Lifestyle & Culture
- Tech & Innovation

## 📦 Tech Stack

| Component        | Technology                                    | Deployment       |
| ---------------- | --------------------------------------------- | ---------------- |
| **Frontend**     | Next.js 16, TypeScript, Tailwind CSS, Zustand | Vercel           |
| **Backend**      | FastAPI, Python, Grok AI, Kimi AI             | Railway          |
| **Shared Types** | TypeScript                                    | Internal package |
| **Build System** | Turborepo, PNPM                               | -                |
| **Database**     | Supabase                                      | Cloud            |

## 🛠️ Installation

### Prerequisites

- Node.js 18+
- PNPM 9+
- Python 3.11+

### Quick Start

```bash
# Clone the repository
git clone https://github.com/McLeuker/McLeuker_Agentic_AI.git
cd McLeuker_Agentic_AI

# Install all dependencies
pnpm install

# Set up environment variables
cp apps/frontend/.env.example apps/frontend/.env.local
cp apps/backend/.env.example apps/backend/.env

# Edit .env files with your API keys
```

### Development

```bash
# Run frontend only
pnpm dev:frontend

# Run backend only
pnpm dev:backend

# Run both (in separate terminals)
pnpm dev:frontend  # Terminal 1
pnpm dev:backend   # Terminal 2
```

### Building

```bash
# Build all packages
pnpm build

# Build frontend only
pnpm build:frontend
```

## 🔑 Environment Variables

### Frontend

| Variable              | Description                          |
| --------------------- | ------------------------------------ |
| `NEXT_PUBLIC_API_URL` | Backend API URL (Railway deployment) |

### Backend

See `apps/backend/.env.example` for the complete list:

```env
# Core AI Models
XAI_API_KEY=your_grok_key
MOONSHOT_API_KEY=your_kimi_key

# Search Providers
PERPLEXITY_API_KEY=your_key
EXA_API_KEY=your_key
GOOGLE_SEARCH_API_KEY=your_key
BING_API_KEY=your_key

# Action Layer
BROWSERLESS_API_KEY=your_key
FIRECRAWL_API_KEY=your_key

# Output Layer
NANO_BANANA_API_KEY=your_key

# Database
SUPABASE_URL=your_url
SUPABASE_KEY=your_key
```

## 📡 API Endpoints

### Chat

```
POST /api/chat
{
  "message": "What are the latest fashion trends?",
  "session_id": "optional-session-id",
  "mode": "auto"
}
```

### Search

```
POST /api/search
{
  "query": "sustainable fashion 2026"
}
```

### File Generation

```
POST /api/generate/file
{
  "type": "excel",
  "title": "Trend Report",
  "data": {...}
}
```

### Image Generation

```
POST /api/generate/image
{
  "prompt": "minimalist fashion mood board",
  "style": "luxury"
}
```

## 💳 Credit System

The platform uses a credit-based model:

- **Free Tier**: 100 credits/month
- **Pro Tier**: 1000 credits/month
- **Enterprise**: Unlimited

Credit costs:

- Simple query: 1 credit
- Deep research: 10 credits
- File generation: 5 credits
- Image generation: 10 credits

## 📊 Project Structure

### Frontend (`apps/frontend`)

```
apps/frontend/
├── src/
│   ├── app/              # Next.js App Router pages
│   ├── components/
│   │   ├── ui/          # Reusable UI components (40+ components)
│   │   └── dashboard/   # Dashboard-specific components
│   ├── hooks/           # Custom React hooks
│   ├── lib/             # Utilities and API client
│   ├── stores/          # Zustand state management
│   └── types/           # TypeScript types
└── public/              # Static assets
```

### Backend (`apps/backend`)

```
apps/backend/
├── main.py              # FastAPI application entry
├── orchestrator.py      # V7 Multi-model orchestration
├── search_layer.py      # Search and research layer
├── settings.py          # Configuration settings
├── src/                 # Source modules
├── Dockerfile           # Container configuration
└── requirements.txt     # Python dependencies
```

### Shared Types (`packages/shared-types`)

TypeScript types shared between frontend and backend, including the V5.1 Response Contract.

```typescript
interface V51Response {
  success: boolean;
  response: {
    answer: string;
    key_insights?: KeyInsight[];
    sources?: Source[];
    follow_up_questions?: string[];
    metadata?: ResponseMetadata;
  };
  error?: string;
}
```

## 🚀 Deployment

### Frontend (Vercel)

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Import this repository
3. Set **Root Directory** to `apps/frontend`
4. Add environment variable: `NEXT_PUBLIC_API_URL`
5. Deploy

### Backend (Railway)

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Create new project from GitHub
3. Select this repository
4. Set **Root Directory** to `apps/backend`
5. Add environment variables from `.env.example`
6. Deploy

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Built with ❤️ by McLeuker**
