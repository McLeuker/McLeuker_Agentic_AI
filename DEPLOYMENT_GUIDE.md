# McLeuker AI - Complete Kimi 2.5 Deployment Guide

## Overview

This guide covers deploying the complete Kimi 2.5 implementation with all capabilities:
- Real-time search (Perplexity, Exa, YouTube, Grok)
- File generation (Excel, Word, PDF, PowerPoint)
- Vision-to-code (image to HTML/React/Vue)
- Code execution sandbox
- Agent Swarm (up to 50 parallel agents)
- Multimodal inputs
- Streaming responses

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND (Vercel)                     │
│  React + TypeScript + Tailwind + shadcn/ui                  │
│  - Chat Interface                                           │
│  - File Upload/Download                                     │
│  - Real-time streaming                                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        BACKEND (Railway)                     │
│  FastAPI + Kimi 2.5 + All Tools                             │
│  - Chat Engine                                              │
│  - File Generator (Excel/Word/PDF/PPTX)                    │
│  - Search APIs (Perplexity/Exa/YouTube/Grok)               │
│  - Code Sandbox                                             │
│  - Agent Swarm                                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        DATABASE (Supabase)                   │
│  - Conversations                                            │
│  - Messages                                                 │
│  - Generated Files                                          │
│  - Usage Stats                                              │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

### API Keys Required

1. **Kimi API Key** (Required)
   - Get from: https://platform.moonshot.cn
   - Variable: `KIMI_API_KEY`

2. **Perplexity API Key** (Recommended)
   - Get from: https://perplexity.ai/settings
   - Variable: `PERPLEXITY_API_KEY`

3. **Exa API Key** (Recommended)
   - Get from: https://exa.ai
   - Variable: `EXA_API_KEY`

4. **YouTube Data API Key** (Optional)
   - Get from: https://console.cloud.google.com
   - Variable: `YOUTUBE_API_KEY`

5. **Grok API Key** (Optional)
   - Get from: https://x.ai
   - Variable: `GROK_API_KEY`

6. **Supabase** (Required for persistence)
   - Get from: https://supabase.com
   - Variables: `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`

## Deployment Steps

### Step 1: Database Setup (Supabase)

1. Create a new Supabase project
2. Go to SQL Editor
3. Run the schema from `supabase/schema.sql`
4. Note your project URL and service role key

### Step 2: Backend Deployment (Railway)

1. **Connect GitHub Repository**
   ```bash
   # In Railway dashboard
   New Project → Deploy from GitHub repo
   Select: McLeuker/McLeuker_Agentic_AI
   ```

2. **Configure Service**
   - Root Directory: `apps/backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Add Environment Variables**
   ```
   KIMI_API_KEY=sk-your-key
   PERPLEXITY_API_KEY=pplx-your-key
   EXA_API_KEY=your-key
   YOUTUBE_API_KEY=your-key
   GROK_API_KEY=xai-your-key
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_SERVICE_KEY=your-service-key
   ```

4. **Deploy**
   - Railway will auto-deploy on git push
   - Verify: `curl https://your-railway-url/api/v1/health`

### Step 3: Frontend Deployment (Vercel)

1. **Connect Repository**
   ```bash
   # In Vercel dashboard
   Add New Project → Import Git Repository
   Select: McLeuker/McLeuker_Agentic_AI
   ```

2. **Configure Build**
   - Framework Preset: Next.js
   - Root Directory: `apps/frontend`
   - Build Command: `npm run build`
   - Output Directory: `.next`

3. **Add Environment Variables**
   ```
   NEXT_PUBLIC_API_URL=https://your-railway-url
   NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
   ```

4. **Deploy**
   - Vercel auto-deploys on git push

### Step 4: GitHub Actions (Optional)

Add these secrets to your GitHub repository:

```
RAILWAY_TOKEN=your-railway-token
VERCEL_TOKEN=your-vercel-token
VERCEL_ORG_ID=your-org-id
VERCEL_PROJECT_ID=your-project-id
NEXT_PUBLIC_API_URL=your-railway-url
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

## File Structure

```
mcleuker-complete/
├── apps/
│   ├── backend/
│   │   ├── main.py              # Complete backend (45KB)
│   │   ├── requirements.txt     # Python dependencies
│   │   └── Dockerfile           # Container config
│   └── frontend/
│       ├── src/
│       │   ├── components/
│       │   │   └── chat/        # All chat components
│       │   ├── lib/
│       │   │   └── api.ts       # API client
│       │   └── ...
│       └── package.json
├── supabase/
│   └── schema.sql               # Database schema
├── .github/
│   └── workflows/
│       └── deploy.yml           # CI/CD pipeline
├── railway.json                 # Railway config
└── DEPLOYMENT_GUIDE.md          # This guide
```

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
# Returns SSE stream
```

### Agent Swarm
```http
POST /api/v1/swarm
{
  "master_task": "Research topic",
  "num_agents": 5,
  "generate_deliverable": true
}
```

### File Generation
```http
POST /api/v1/generate-file
{
  "content": {...},
  "file_type": "excel",
  "title": "Report"
}
```

### Vision to Code
```http
POST /api/v1/vision-to-code
{
  "image_base64": "...",
  "framework": "react"
}
```

### Code Execution
```http
POST /api/v1/execute-code
{
  "code": "print('hello')",
  "language": "python"
}
```

## Testing

### Health Check
```bash
curl https://your-railway-url/api/v1/health
```

### Test Chat
```bash
curl -X POST https://your-railway-url/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello"}],
    "mode": "thinking"
  }'
```

### Test File Generation
```bash
curl -X POST https://your-railway-url/api/v1/generate-file \
  -H "Content-Type: application/json" \
  -d '{
    "content": {"data": [{"name": "Item 1", "value": 100}]},
    "file_type": "excel",
    "title": "Test Report"
  }'
```

## Troubleshooting

### Backend Issues

**Import Error: No module named 'xxx'**
```bash
# Rebuild with updated requirements
pip install -r requirements.txt --upgrade
```

**Kimi API 401 Error**
- Verify `KIMI_API_KEY` is set correctly
- Check key is valid at platform.moonshot.cn

**CORS Errors**
- Add your frontend URL to CORS origins in `main.py`
- Verify `NEXT_PUBLIC_API_URL` is correct

### Frontend Issues

**Build Fails**
```bash
cd apps/frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

**API Calls Fail**
- Check `NEXT_PUBLIC_API_URL` is set
- Verify backend is running

### Database Issues

**RLS Policy Errors**
- Ensure user is authenticated
- Check policies in Supabase dashboard

## Performance Optimization

### Backend
- Use Redis for caching (add to requirements)
- Enable connection pooling
- Set appropriate timeouts

### Frontend
- Enable Next.js image optimization
- Use React.memo for message components
- Implement virtual scrolling for long conversations

### Database
- Add indexes for frequent queries
- Use connection pooling (PgBouncer)
- Archive old conversations

## Monitoring

### Logs
```bash
# Railway logs
railway logs --tail

# Vercel logs
vercel logs --tail
```

### Metrics
- Token usage per user
- API response times
- File generation counts
- Error rates

## Security Checklist

- [ ] API keys stored in environment variables
- [ ] Database RLS policies enabled
- [ ] CORS configured for production domains
- [ ] Rate limiting implemented
- [ ] Input validation on all endpoints
- [ ] File upload size limits
- [ ] Code execution sandboxed
- [ ] Sensitive data encrypted

## Support

For issues:
1. Check logs in Railway/Vercel dashboard
2. Verify all environment variables
3. Test API endpoints directly
4. Check Supabase connection

## Next Steps

1. Add user authentication with Supabase Auth
2. Implement rate limiting
3. Add usage analytics dashboard
4. Set up monitoring (Sentry, LogRocket)
5. Add more file types (CSV, JSON)
6. Implement conversation sharing
