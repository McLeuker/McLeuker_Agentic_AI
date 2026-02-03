# McLeuker Agentic AI Platform v2.0.0

## 🚀 Complete System Rebuild

This is a **frontier-level agentic AI platform** with capabilities comparable to Manus AI and ChatGPT.

---

## ✅ Issues Fixed

### 1. **Conversation Memory** (Previously Broken)
**Before:** AI couldn't remember previous messages ("What is the capital of France?" → "Paris" → "What about its population?" → "I don't know what you're referring to")

**After:** Full conversation context is maintained across all messages in a session.

```python
# New memory system
from src.memory.conversation_memory import ConversationMemoryStore

memory = get_memory_store()
conv = memory.get_or_create_conversation(conversation_id, user_id)
conv.add_message("user", message)
# All previous messages are available for context
```

### 2. **Real-Time Web Search** (Previously Missing)
**Before:** "I can't provide real-time updates or current information"

**After:** Multi-provider search using Perplexity, Google, Bing, and Firecrawl.

```python
# New search system
from src.search.web_search import MultiProviderSearch

search = get_search_system()
result = await search.smart_search("latest news on AI")
# Returns real-time information with sources
```

### 3. **File Generation** (Previously Broken)
**Before:** Excel files couldn't open, missing data, no formatting

**After:** Professional file generation with proper styling.

```python
# New file generators
from src.files.excel_generator import ProfessionalExcelGenerator
from src.files.pdf_generator import ProfessionalPDFGenerator
from src.files.word_generator import ProfessionalWordGenerator

# Creates properly formatted, styled documents
```

### 4. **Reasoning Display** (Previously Missing)
**Before:** Generic responses without visible thinking

**After:** Chain-of-thought reasoning with visible steps.

```python
# New reasoning engine
from src.reasoning.reasoning_engine import ReasoningEngine

engine = ReasoningEngine(llm_provider)
chain = await engine.analyze_query(query)
# Returns structured reasoning steps
```

### 5. **Output Formatting** (Previously Poor)
**Before:** Plain text responses, no structure

**After:** Manus AI-style formatting with emojis, sections, and sources.

```python
# New output formatter
from src.output.formatter import OutputFormatter

formatter = get_formatter()
formatted = formatter.format_response(content, style=OutputStyle.DETAILED)
# Returns beautifully formatted markdown
```

---

## 📁 New Module Structure

```
src/
├── api/
│   └── main.py              # Rebuilt FastAPI backend
├── memory/
│   ├── __init__.py
│   ├── conversation_memory.py  # Conversation storage & retrieval
│   └── context_extractor.py    # Entity & topic extraction
├── reasoning/
│   ├── __init__.py
│   └── reasoning_engine.py     # Chain-of-thought reasoning
├── search/
│   ├── __init__.py
│   └── web_search.py           # Multi-provider search
├── files/
│   ├── __init__.py
│   ├── excel_generator.py      # Professional Excel
│   ├── pdf_generator.py        # Professional PDF
│   └── word_generator.py       # Professional Word
├── output/
│   ├── __init__.py
│   └── formatter.py            # Manus AI-style formatting
├── config/
│   └── settings.py             # Configuration
└── utils/
    └── llm_provider.py         # LLM abstraction
```

---

## 🔧 API Endpoints

### Chat (Main Interaction)
```
POST /api/chat
{
    "message": "What is the weather in Paris?",
    "conversation_id": "optional-id",
    "user_id": "optional-user",
    "mode": "quick" | "deep"
}
```

### Search
```
POST /api/search
{
    "query": "latest AI news",
    "mode": "quick" | "deep",
    "num_results": 10
}
```

### File Generation
```
POST /api/files/generate
{
    "content": "Data to convert",
    "file_type": "excel" | "pdf" | "word",
    "title": "Document Title",
    "data": [{"col1": "val1"}]  // For Excel
}
```

### Conversation Management
```
GET /api/conversations/{conversation_id}
DELETE /api/conversations/{conversation_id}
GET /api/users/{user_id}/conversations
```

---

## 🔑 Required Environment Variables

```env
# LLM Providers
OPENAI_API_KEY=sk-...
GROK_API_KEY=xai-...
PERPLEXITY_API_KEY=pplx-...

# Search APIs
GOOGLE_SEARCH_API_KEY=...
BING_API_KEY=...
FIRECRAWL_API_KEY=fc-...

# Application
CORS_ORIGINS=*
OUTPUT_DIR=./outputs
```

---

## 🚀 Deployment

### Railway
1. Push to GitHub (already done)
2. Railway will auto-deploy from the repository
3. Ensure all environment variables are set in Railway

### Manual
```bash
cd /home/ubuntu/mcleuker_agentic_ai
pip install -r requirements.txt
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

---

## 📊 Test Results

All modules tested and working:

- ✅ Settings import
- ✅ Memory system (conversation persistence)
- ✅ Reasoning engine (query analysis)
- ✅ Search system (multi-provider)
- ✅ Excel generator (professional formatting)
- ✅ PDF generator (styled documents)
- ✅ Word generator (formatted documents)
- ✅ Output formatter (Manus AI-style)
- ✅ FastAPI app (all endpoints)

---

## 📝 Version History

- **v2.0.0** (2026-01-31): Complete rebuild with memory, search, reasoning, and file generation
- **v1.0.0**: Initial version (had issues with memory, search, and file generation)
