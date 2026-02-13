# McLeuker AI - Quick Start Guide

## ✅ Project is Running!

Your McLeuker AI Fashion Intelligence Platform is now up and running.

### 🌐 Access URLs

- **Frontend (Next.js)**: http://localhost:3000
- **Backend API (FastAPI)**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 🔧 What Was Fixed

1. **Created `.env.local` file** with environment variables
2. **Modified middleware** to gracefully handle missing Supabase credentials
3. **Authentication is now optional** - the app works without Supabase setup

### 📝 Environment Variables

The `.env.local` file has been created with:

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Supabase Configuration (Optional - currently disabled)
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
```

### 🚀 Running the Project

**Frontend:**
```bash
cd apps/frontend
pnpm dev
```

**Backend:**
```bash
cd apps/backend
.\venv\Scripts\Activate.ps1
python -m uvicorn src.api.main_v2:app --reload --host 0.0.0.0 --port 8000
```

**Or from root:**
```bash
# Frontend
pnpm dev:frontend

# Backend
pnpm dev:backend
```

### 🔐 Setting Up Supabase (Optional)

If you want to enable authentication:

1. Go to https://supabase.com/dashboard
2. Create a new project
3. Go to Settings → API
4. Copy your Project URL and anon/public key
5. Update `.env.local` with real credentials:
   ```env
   NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your-actual-anon-key
   ```
6. Restart the frontend server

### 📦 Tech Stack

- **Frontend**: Next.js 16, TypeScript, Tailwind CSS, Radix UI
- **Backend**: FastAPI, Python, Grok AI
- **Build System**: Turborepo, PNPM
- **State Management**: Zustand
- **Authentication**: Supabase (optional)

### 🎨 Features

- Premium dark theme inspired by ChatGPT
- AI-powered fashion intelligence
- Trend forecasting
- Supplier research
- Market analysis
- Sustainability consulting

### 🛑 Stopping the Services

To stop the running services, press `Ctrl+C` in each terminal window.

---

**Built with ❤️ by McLeuker**
