# Railway Deployment Guide (v2.0.0)

Follow these steps to deploy the new Agentic AI backend to Railway.

## 1. Prepare Repository
The code is already pushed to your GitHub repository. Railway will automatically detect the `Dockerfile` or `requirements.txt`.

## 2. Railway Configuration
1. Go to your [Railway Dashboard](https://railway.app/dashboard).
2. Select your project and the backend service.
3. In the **Settings** tab:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8000}`
   - **Root Directory**: `/` (or the folder containing `src`)

## 3. Environment Variables (CRITICAL)
You must add these variables in the **Variables** tab for the system to work:

### Required for AI
- `OPENAI_API_KEY`: Your OpenAI key.
- `PERPLEXITY_API_KEY`: Required for real-time search.
- `GROK_API_KEY`: (Optional) For Grok models.

### Required for Search
- `GOOGLE_SEARCH_API_KEY`: For Google search results.
- `BING_API_KEY`: For Bing search results.
- `FIRECRAWL_API_KEY`: For web scraping.

### Application Settings
- `CORS_ORIGINS`: Set to `*` or your Lovable frontend URL.
- `PORT`: Railway sets this automatically, but ensure your code uses it.
- `OUTPUT_DIR`: Set to `/tmp/outputs` (Railway has a read-only filesystem, `/tmp` is writable).

## 4. Persistent Storage (Optional)
Since Railway's filesystem is ephemeral, generated files in `OUTPUT_DIR` will be deleted on restart. 
- **Recommendation**: For production, connect an S3 bucket or use Railway's Volume feature to persist the `outputs` folder.

## 5. Health Check
Once deployed, visit `https://your-railway-url.up.railway.app/health` to verify the system is operational.
