# McLeuker AI Monorepo

A unified repository containing both the frontend and backend for McLeuker AI - the Fashion Intelligence Platform.

## Architecture

```
mcleuker-ai/
├── apps/
│   ├── frontend/          # Next.js 16 + TypeScript + Tailwind CSS
│   └── backend/           # FastAPI + Python (V5.1 API)
├── packages/
│   └── shared-types/      # Shared TypeScript types (V5.1 Response Contract)
├── turbo.json             # Turborepo configuration
├── pnpm-workspace.yaml    # PNPM workspace config
└── package.json           # Root package.json
```

## Tech Stack

| Component | Technology | Deployment |
|-----------|------------|------------|
| **Frontend** | Next.js 16, TypeScript, Tailwind CSS, Zustand | Vercel |
| **Backend** | FastAPI, Python, Grok AI, Supabase | Railway |
| **Shared Types** | TypeScript | Internal package |
| **Build System** | Turborepo, PNPM | - |

## Quick Start

### Prerequisites

- Node.js 18+
- PNPM 9+
- Python 3.11+

### Installation

```bash
# Clone the repository
git clone https://github.com/mcleuker/mcleuker-ai.git
cd mcleuker-ai

# Install all dependencies
pnpm install

# Set up environment variables
cp apps/frontend/.env.example apps/frontend/.env.local
cp apps/backend/.env.example apps/backend/.env
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

## Deployment

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

## Project Structure

### Frontend (`apps/frontend`)

The Next.js application that provides the user interface.

```
apps/frontend/
├── src/
│   ├── app/              # Next.js App Router pages
│   ├── components/       # React components
│   │   ├── chat/        # Chat interface components
│   │   └── layout/      # Layout components
│   ├── lib/             # Utilities and API client
│   ├── stores/          # Zustand state management
│   └── types/           # TypeScript types (re-exports shared-types)
└── public/              # Static assets
```

### Backend (`apps/backend`)

The FastAPI application that powers the AI functionality.

```
apps/backend/
├── src/
│   ├── api/             # API routes and main application
│   ├── core/            # Core business logic
│   ├── layers/          # AI processing layers
│   ├── database/        # Database connections
│   └── services/        # External service integrations
├── Dockerfile           # Container configuration
└── requirements.txt     # Python dependencies
```

### Shared Types (`packages/shared-types`)

TypeScript types shared between frontend and backend, including the V5.1 Response Contract.

```
packages/shared-types/
└── src/
    └── index.ts         # All shared type definitions
```

## Environment Variables

### Frontend

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Backend API URL (Railway deployment) |

### Backend

| Variable | Description |
|----------|-------------|
| `XAI_API_KEY` | Grok API key |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_KEY` | Supabase anon key |
| `PERPLEXITY_API_KEY` | Perplexity search API |
| `EXA_API_KEY` | Exa.ai search API |

See `apps/backend/.env.example` for the complete list.

## Scripts

| Command | Description |
|---------|-------------|
| `pnpm dev` | Run all apps in development mode |
| `pnpm dev:frontend` | Run frontend only |
| `pnpm dev:backend` | Run backend only |
| `pnpm build` | Build all packages |
| `pnpm build:frontend` | Build frontend only |
| `pnpm lint` | Lint all packages |
| `pnpm clean` | Clean all build artifacts |

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Built with ❤️ by McLeuker**
