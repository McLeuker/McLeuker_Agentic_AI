# McLeuker AI V2 - Deployment Guide

## Overview

This guide covers deploying the complete McLeuker AI V2 system with:
- Full Kimi-2.5 capabilities
- Hybrid LLM architecture (Kimi-2.5 + Grok)
- Agent swarm
- Fixed file generation
- Proper memory system

## Prerequisites

- Python 3.10+
- Node.js 18+
- Supabase account
- API keys for:
  - Kimi (Moonshot AI)
  - Grok (X AI)
  - Perplexity
  - Exa
  - SerpAPI
  - YouTube (optional)

---

## Step 1: Supabase Setup

### 1.1 Create New Project (or use existing)

```bash
# If using Supabase CLI
supabase login
supabase projects create mcleuker-ai-v2
```

### 1.2 Apply Schema

```bash
# Connect to your Supabase project
supabase link --project-ref your-project-ref

# Apply the schema
supabase db reset
# Or run SQL directly in Supabase dashboard
```

### 1.3 Schema SQL

Copy the contents of `supabase/schema_v2.sql` and run in Supabase SQL Editor.

### 1.4 Set Environment Variables

In your Supabase dashboard:
- Go to Project Settings > API
- Copy `Project URL` and `anon/public` key
- These will be used in backend environment variables

---

## Step 2: Backend Deployment

### 2.1 Environment Variables

Create `.env` file in backend directory:

```bash
# API Keys
KIMI_API_KEY=your_kimi_api_key
GROK_API_KEY=your_grok_api_key
PERPLEXITY_API_KEY=your_perplexity_key
EXA_API_KEY=your_exa_key
SERPAPI_KEY=your_serpapi_key
YOUTUBE_API_KEY=your_youtube_key_optional

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key

# Server
PORT=8000
```

### 2.2 Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Create `requirements.txt`:

```
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.0
openai==1.10.0
httpx==0.26.0
supabase==2.3.0
python-multipart==0.0.6
pandas==2.1.4
openpyxl==3.1.2
python-docx==1.1.0
reportlab==4.0.8
python-pptx==0.6.23
```

### 2.3 Test Locally

```bash
python main_v2.py
```

Test endpoints:

```bash
# Health check
curl http://localhost:8000/health

# Chat
curl -N -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello"}], "mode": "thinking"}'
```

### 2.4 Deploy to Railway/Render

**Railway:**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create project
railway init

# Add environment variables
railway variables set KIMI_API_KEY=your_key
railway variables set GROK_API_KEY=your_key
# ... etc

# Deploy
railway up
```

**Render:**

1. Create `render.yaml`:

```yaml
services:
  - type: web
    name: mcleuker-ai-backend
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main_v2:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: KIMI_API_KEY
        sync: false
      - key: GROK_API_KEY
        sync: false
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_SERVICE_KEY
        sync: false
```

2. Push to GitHub and connect to Render

---

## Step 3: Frontend Deployment

### 3.1 Environment Variables

Create `.env.local` in frontend directory:

```bash
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
```

### 3.2 Update Components

Replace the following files in your frontend:

1. `components/chat/ModeSelector.tsx` → Use our updated version
2. `services/api.ts` (or create) → Use our API service

### 3.3 Install Dependencies

```bash
cd frontend
npm install
```

### 3.4 Test Locally

```bash
npm run dev
```

### 3.5 Deploy to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Set environment variables
vercel env add NEXT_PUBLIC_API_URL
vercel env add NEXT_PUBLIC_SUPABASE_URL
vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY
```

---

## Step 4: Testing

### 4.1 Backend Tests

```bash
# Test health
curl https://your-backend-url/health

# Test chat
curl -N -X POST https://your-backend-url/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "What is AI?"}], "mode": "thinking"}'

# Test file generation
curl -N -X POST https://your-backend-url/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Create an Excel with top tech companies"}], "mode": "agent"}'

# Test search
curl -X POST https://your-backend-url/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "latest AI news", "sources": ["web", "news"]}'
```

### 4.2 Frontend Tests

1. Open your deployed frontend
2. Test each mode:
   - Instant: Quick response
   - Thinking: Shows reasoning
   - Agent: Uses tools and search
   - Swarm: Multiple agents
   - Research: Deep research
   - Code: Code generation
   - Hybrid: Kimi + Grok

3. Test file generation:
   - "Create an Excel with top fashion influencers"
   - "Generate a PDF report on AI trends"
   - "Make a PowerPoint about climate change"

4. Test conversation memory:
   - Start conversation
   - Send multiple messages
   - Refresh page
   - Verify conversation persists

---

## Step 5: Monitoring

### 5.1 Backend Logs

**Railway:**
```bash
railway logs
```

**Render:**
View logs in Render dashboard

### 5.2 Supabase Monitoring

- Go to Supabase Dashboard > Database
- Monitor connection count
- Check slow queries

### 5.3 Health Checks

Set up periodic health checks:

```bash
# Cron job every 5 minutes
curl -f https://your-backend-url/health || echo "Backend down"
```

---

## Troubleshooting

### Issue: Backend won't start

**Check:**
1. All environment variables set
2. Python version >= 3.10
3. All dependencies installed

```bash
# Check Python version
python --version

# Check dependencies
pip list | grep -E "fastapi|openai|supabase"
```

### Issue: File generation fails

**Check:**
1. `/tmp/mcleuker_outputs` directory exists and is writable
2. Required libraries installed (openpyxl, python-docx, etc.)
3. Search APIs returning results

### Issue: Supabase connection fails

**Check:**
1. SUPABASE_URL is correct
2. SUPABASE_SERVICE_KEY has correct permissions
3. Database schema applied correctly

```bash
# Test Supabase connection
python -c "from supabase import create_client; c = create_client('url', 'key'); print(c.table('conversations').select('*').limit(1).execute())"
```

### Issue: Kimi/Grok not responding

**Check:**
1. API keys are valid
2. Rate limits not exceeded
3. Network connectivity

```bash
# Test Kimi
curl https://api.moonshot.ai/v1/models \
  -H "Authorization: Bearer $KIMI_API_KEY"
```

### Issue: Frontend can't connect to backend

**Check:**
1. CORS settings in backend
2. NEXT_PUBLIC_API_URL is correct
3. Backend is running

---

## Migration from V1

### Database Migration

1. Backup existing data
2. Run new schema (adds new columns, tables)
3. Migrate existing data

```sql
-- Example: Add new columns to existing table
ALTER TABLE conversations ADD COLUMN IF NOT EXISTS memory_summary TEXT;
ALTER TABLE conversations ADD COLUMN IF NOT EXISTS memory_context JSONB DEFAULT '[]';
```

### Code Migration

1. Replace `main.py` with `main_v2.py`
2. Update frontend API service
3. Update ModeSelector component
4. Test thoroughly

---

## Performance Optimization

### Backend

1. **Enable caching:**
```python
# Add to main_v2.py
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="mcleuker-cache")
```

2. **Connection pooling:**
```python
# Already implemented in httpx.AsyncClient
```

3. **File cleanup:**
```bash
# Add cron job to clean old files
0 0 * * * find /tmp/mcleuker_outputs -mtime +7 -delete
```

### Frontend

1. **Enable SSR caching:**
```javascript
// next.config.js
module.exports = {
  experimental: {
    incrementalCacheHandlerPath: require.resolve('./cache-handler.js'),
  },
}
```

2. **Optimize images:**
```javascript
// Use next/image
import Image from 'next/image';
```

---

## Security Checklist

- [ ] API keys stored in environment variables
- [ ] Supabase RLS policies enabled
- [ ] CORS configured for production domains only
- [ ] Rate limiting implemented
- [ ] File upload size limits set
- [ ] Input validation on all endpoints
- [ ] HTTPS enforced
- [ ] Secrets not logged

---

## Support

For issues:
1. Check logs
2. Review this guide
3. Check GitHub issues
4. Contact support
