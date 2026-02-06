# McLeuker AI - Kimi 2.5 Upgrade

This document describes the upgrade from Grok to Kimi 2.5 and how to deploy it.

## What's New

### Core Capabilities
- **Kimi 2.5 Model**: 1T MoE architecture, 32B active parameters, 256K context window
- **Multiple Modes**:
  - `instant`: Fast responses (temp 0.6)
  - `thinking`: Step-by-step reasoning visible (temp 1.0)
  - `agent`: Tool use with web search, code generation, data analysis
  - `swarm`: Multi-agent parallel execution
  - `vision_code`: Convert UI images to code

### New Features
1. **Agent Swarm**: Coordinate up to 20 parallel agents for complex tasks
2. **Vision-to-Code**: Upload UI mockups, get complete HTML/React/Vue code
3. **Multimodal**: Text + image inputs in single request
4. **Tool Integration**: Web search, Perplexity research, code generation
5. **Reasoning Display**: See Kimi's thinking process in thinking mode

### Backward Compatibility
- The existing `/api/chat/stream` endpoint is fully preserved
- All SSE streaming events (`layer_start`, `sub_step`, `content`, `source`, `complete`) work as before
- Image generation (`/api/image/generate`) and document generation (`/api/document/generate`) are unchanged
- The frontend requires zero changes to continue working

## File Changes

### Backend (`apps/backend/`)
- **main.py**: New standalone Kimi 2.5 engine (alternative entry point)
- **src/api/main_v8.py**: Integrated Kimi 2.5 + legacy streaming (primary entry point)
- **requirements.txt**: Updated dependencies

### Frontend (`apps/frontend/src/lib/`)
- **api.ts**: Added new Kimi 2.5 API client functions alongside existing ones

### Root
- **deploy.sh**: Deployment script
- **.github/workflows/deploy.yml**: CI/CD workflow
- **KIMI_UPGRADE_README.md**: This file

## Environment Variables

Add to Railway:
```
KIMI_API_KEY=<your-kimi-api-key>
```

Keep existing:
```
PERPLEXITY_API_KEY=<your-key>
EXA_API_KEY=<your-key>
XAI_API_KEY=<your-key>
OPENAI_API_KEY=<your-key>
GROK_API_KEY=<your-key>
```

## API Endpoints

### Legacy (Backward Compatible)
```bash
POST /api/chat/stream     # SSE streaming chat (Quick/Deep modes)
POST /api/image/generate  # Image generation (xAI + OpenAI DALL-E)
POST /api/document/generate  # Document generation (MD, PDF, XLSX, DOCX, PPTX)
POST /api/kimi/execute    # Kimi tool execution
GET  /health              # Health check
```

### New Kimi 2.5 Endpoints
```bash
POST /api/v1/chat
{
  "messages": [{"role": "user", "content": "Hello"}],
  "mode": "thinking",  // instant | thinking | agent | swarm | vision_code
  "stream": false
}
```

### Agent Swarm
```bash
POST /api/v1/swarm
{
  "master_task": "Research quantum computing applications",
  "context": {},
  "num_agents": 5,
  "auto_synthesize": true
}
```

### Vision to Code
```bash
POST /api/v1/vision-to-code
{
  "image_base64": "base64_encoded_image...",
  "requirements": "Modern, responsive design",
  "framework": "html"  // html | react | vue | svelte
}
```

### Multimodal
```bash
POST /api/v1/multimodal
FormData:
  - text: "Describe this image"
  - mode: "thinking"
  - image: [File]
```

### Research
```bash
POST /api/v1/research
FormData:
  - query: "Latest AI trends"
  - depth: "deep"
```

### Health Check
```bash
GET /api/v1/health
```

## Deployment Steps

### Option 1: Automated Script
```bash
./deploy.sh
```

### Option 2: Manual Deployment

1. **Commit changes**:
```bash
git add -A
git commit -m "Upgrade to Kimi 2.5"
git push origin main
```

2. **Railway auto-deploys** from GitHub

3. **Verify deployment**:
```bash
curl https://web-production-29f3c.up.railway.app/api/v1/health
```

## Model Fallback Chain

The backend uses a 3-tier fallback system:
1. **Primary**: Kimi 2.5 (via `KIMI_API_KEY`)
2. **Fallback 1**: ChatGPT (via `OPENAI_API_KEY`)
3. **Fallback 2**: Grok (via `GROK_API_KEY` or `XAI_API_KEY`)

If all three are unavailable, the API returns a friendly error message.

## Troubleshooting

### Issue: API returns 500
- Check Kimi API key is set in Railway
- Check Railway logs: `railway logs --tail`

### Issue: CORS errors
- Verify Vercel URL is in CORS origins in main_v8.py

### Issue: Tool calls not working
- Check PERPLEXITY_API_KEY and EXA_API_KEY are set

## Rollback

If needed, rollback to previous version:
```bash
git log --oneline  # Find previous commit
git revert HEAD    # Revert last commit
git push origin main
```

## Support

For issues with this upgrade, check:
1. Railway logs
2. Kimi API status: https://status.moonshot.cn
3. Health endpoint response
