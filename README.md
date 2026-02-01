# McLeuker Fashion AI Platform V3.1

> **The Frontier Agentic AI for Fashion, Beauty, Lifestyle, and Culture**

A next-generation AI platform built to surpass Manus AI with real-time intelligence, professional file generation, and deep industry expertise.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE (Lovable)                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   V3.1 ORCHESTRATOR                          │
│              (Grok - Unified Reasoning Brain)                │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  SEARCH LAYER │   │  ACTION LAYER │   │ ANALYST LAYER │
│               │   │               │   │               │
│ • Google      │   │ • Browserless │   │ • E2B Sandbox │
│ • Bing        │   │ • Firecrawl   │   │ • Excel Gen   │
│ • Perplexity  │   │               │   │ • PDF Gen     │
│ • Exa.ai      │   │               │   │               │
└───────────────┘   └───────────────┘   └───────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      OUTPUT LAYER                            │
│                    (Nano Banana Images)                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATABASE (Supabase)                       │
│           Users • Credits • Conversations • Usage            │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Features

### Core Capabilities
- **Grok-Powered Reasoning**: Real-time X (Twitter) data access for instant trend detection
- **Parallel Search**: Simultaneous queries across Google, Bing, Perplexity, and Exa.ai
- **Web Automation**: Browserless.io integration for live web interaction
- **Professional Files**: E2B sandbox for Excel, PDF, and data analysis
- **Image Generation**: Nano Banana for fashion mood boards and visuals

### Industry Focus
- Fashion & Catwalks
- Beauty & Skincare
- Textile & Sustainability
- Lifestyle & Culture
- Tech & Innovation

## 📦 Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Brain** | Grok (XAI) | Unified reasoning with real-time data |
| **Search** | Google, Bing, Perplexity, Exa | Parallel information gathering |
| **Action** | Browserless, Firecrawl | Web automation and extraction |
| **Analyst** | E2B Sandbox | Code execution and file generation |
| **Output** | Nano Banana | AI image generation |
| **Database** | Supabase | Users, credits, conversations |
| **Backend** | FastAPI | High-performance API |
| **Deploy** | Railway | Scalable cloud hosting |

## 🛠️ Installation

### Local Development

```bash
# Clone the repository
git clone https://github.com/McLeuker/McLeuker_Agentic_AI.git
cd McLeuker_Agentic_AI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your API keys

# Run the server
uvicorn src.api.main:app --reload
```

### Docker Deployment

```bash
docker build -t mcleuker-ai .
docker run -p 8000:8000 --env-file .env mcleuker-ai
```

## 🔑 Environment Variables

See `.env.example` for all required variables:

```env
# Core Brain
XAI_API_KEY=your_grok_key

# Search Providers
PERPLEXITY_API_KEY=your_key
EXA_API_KEY=your_key
GOOGLE_SEARCH_API_KEY=your_key
BING_API_KEY=your_key

# Action Layer
BROWSERLESS_API_KEY=your_key
FIRECRAWL_API_KEY=your_key

# Analyst Layer
E2B_API_KEY=your_key

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

## 📊 Database Schema

Run the SQL in `src/database/supabase_client.py` to set up:
- `users` - User accounts and credit balances
- `credit_transactions` - Credit usage history
- `conversations` - Chat history
- `usage_logs` - API usage analytics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details.

---

**Built with ❤️ by McLeuker**
