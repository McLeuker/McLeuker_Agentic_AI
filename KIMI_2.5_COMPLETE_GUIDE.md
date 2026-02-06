# McLeuker AI - Kimi 2.5 Complete Implementation

## Overview

This is the complete Kimi 2.5 implementation with:
- **Real-time data search** (Perplexity, Exa, YouTube, Grok)
- **File generation** (Excel, Word, PDF)
- **Agent Swarm** (5-20 parallel agents)
- **Streaming responses**
- **Multimodal inputs** (text + image)
- **Deep research mode**

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Chat Interface│  │ Mode Selector │  │ Download Btn │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      KIMI 2.5 BACKEND                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Chat Engine  │  │ Tool Executor │  │ File Generator│          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Agent Swarm  │  │ Search APIs  │  │ Stream Handler│          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     EXTERNAL APIs                                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │ Kimi 2.5 │ │Perplexity│ │   Exa    │ │ YouTube  │           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
│  ┌──────────┐                                                    │
│  │   Grok   │                                                    │
│  └──────────┘                                                    │
└─────────────────────────────────────────────────────────────────┘
```

## Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **Instant** | Fast responses, no reasoning shown | Quick questions |
| **Thinking** | Step-by-step reasoning visible | Complex problems |
| **Agent** | Tools + real-time search | Current events, data requests |
| **Swarm** | 5-20 parallel agents | Complex multi-faceted tasks |
| **Research** | Deep research + report generation | Comprehensive analysis |

## API Endpoints

### Chat
```http
POST /api/v1/chat
{
  "messages": [{"role": "user", "content": "..."}],
  "mode": "agent",
  "enable_tools": true
}
```

### Streaming Chat
```http
POST /api/v1/chat/stream
{
  "messages": [...],
  "mode": "thinking"
}
# Returns SSE stream
```

### Agent Swarm
```http
POST /api/v1/swarm
{
  "master_task": "Research quantum computing",
  "num_agents": 5,
  "enable_search": true
}
```

### Search
```http
POST /api/v1/search
{
  "query": "Paris Fashion Week 2026",
  "sources": ["web", "news", "youtube"]
}
```

### Research with Report
```http
POST /api/v1/research
{
  "query": "AI in healthcare",
  "depth": "deep",
  "generate_report": true
}
```

### Generate File
```http
POST /api/v1/generate-file
{
  "content": "{\"brands\": [{\"name\": \"Dior\", \"country\": \"France\"}]}",
  "file_type": "excel",
  "title": "Fashion Brands"
}
```

### Download File
```http
GET /api/v1/download/{file_id}
```

## Environment Variables

Add these to Railway:

```bash
# Required
KIMI_API_KEY=your_kimi_api_key

# For real-time search (add as many as you have)
PERPLEXITY_API_KEY=your_perplexity_key
EXA_API_KEY=your_exa_key
YOUTUBE_API_KEY=your_youtube_key
GROK_API_KEY=your_grok_key
```

## Tool Execution Flow

```
User Query → Kimi 2.5 → Detects Tool Need → Executes Tool → Returns Result
                ↓
         "Generate Excel with..."
                ↓
         FileGenerator.generate_excel()
                ↓
         Returns file_id + download_url
```

## Example Queries

### Real-time Information
```
"What's happening at Paris Fashion Week 2026?"
→ Agent mode triggers realtime_search
→ Searches Perplexity, Exa, YouTube
→ Returns current information with sources
```

### File Generation
```
"Generate an Excel sheet of top 10 European fashion brands"
→ Agent mode detects file request
→ Calls generate_excel tool
→ Returns downloadable file
```

### Deep Research
```
"Research the latest AI trends and create a report"
→ Research mode uses Agent Swarm
→ Multiple agents analyze different aspects
→ Generates Word document report
```

### Complex Task
```
"Analyze the future of electric vehicles"
→ Swarm mode activates 5 agents
- Researcher: Market data
- Analyst: Technical trends
- Writer: Summary
- Critic: Challenges
- Synthesizer: Final report
```

## Frontend Components

```
src/components/chat/
├── ChatInterface.tsx    # Main chat container
├── ModeSelector.tsx     # Mode dropdown
├── MessageList.tsx      # Message display
├── InputArea.tsx        # Input with quick actions
├── ToolIndicator.tsx    # Shows active tools
├── DownloadButton.tsx   # File download buttons
└── SearchResults.tsx    # Collapsible search sources
```

## Deployment

### 1. Update Environment Variables
```bash
# Railway Dashboard → Variables
KIMI_API_KEY=sk-...
PERPLEXITY_API_KEY=pplx-...
EXA_API_KEY=...
```

### 2. Deploy Backend
```bash
git add apps/backend/main.py apps/backend/requirements.txt
git commit -m "feat: Complete Kimi 2.5 with tools and real-time search"
git push origin main
# Railway auto-deploys
```

### 3. Deploy Frontend
```bash
git add apps/frontend/src/lib/api.ts apps/frontend/src/components/chat/
git commit -m "feat: Chat UI with downloads and tool indicators"
git push origin main
# Vercel auto-deploys
```

### 4. Verify
```bash
curl https://your-railway-url/api/v1/health
```

## Response Format

### Chat Response
```json
{
  "success": true,
  "response": {
    "answer": "...",
    "reasoning": "...",
    "mode": "agent",
    "downloads": [
      {
        "filename": "brands.xlsx",
        "download_url": "/api/v1/download/abc123",
        "file_id": "abc123"
      }
    ],
    "search_results": [...],
    "metadata": {
      "tokens": {...},
      "latency_ms": 2500,
      "tool_calls": 2
    }
  }
}
```

## Troubleshooting

### API Returns 401
- Check KIMI_API_KEY is set correctly
- Verify key is valid at platform.moonshot.cn

### Search Not Working
- Check Perplexity/Exa keys are configured
- Check health endpoint: `/api/v1/health`

### File Download Fails
- Files stored in `/tmp/mcleuker_outputs`
- Files expire when container restarts

### CORS Errors
- Verify frontend URL in CORS origins
- Check `NEXT_PUBLIC_API_URL` is correct

## Performance

| Mode | Avg Latency | Tokens/req |
|------|-------------|------------|
| Instant | 1-2s | 500-1000 |
| Thinking | 3-5s | 1000-3000 |
| Agent | 5-10s | 2000-5000 |
| Swarm (5) | 10-20s | 5000-15000 |
| Research | 15-30s | 10000-25000 |

## Next Steps

1. Add user authentication
2. Persist chat history to Supabase
3. Add more file types (PPTX, CSV)
4. Implement rate limiting
5. Add usage analytics
