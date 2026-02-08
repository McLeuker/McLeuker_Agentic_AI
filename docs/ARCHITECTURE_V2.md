# McLeuker AI V2 - Complete Architecture Overhaul

## Executive Summary

This document outlines the complete architectural overhaul of McLeuker AI to deliver:
- **Full Kimi-2.5 capabilities** with proper reasoning, tool use, and agent swarm
- **Hybrid LLM architecture** - Kimi-2.5 + Grok working together
- **Fixed file generation** with real data extraction
- **Proper memory/conversation persistence** via Supabase
- **Working downloads** with proper file handling
- **Clean output structure** with standardized events

---

## Current Issues Analysis

### 1. File Generation Broken
- Excel files are empty (no data extraction from search)
- Downloads fail or return broken files
- No proper data pipeline from search to file generation

### 2. Kimi-2.5 Misconfigured
- Wrong `extra_body={"thinking": {...}}` format
- Reasoning not properly enabled
- Model capabilities not fully utilized

### 3. No Memory System
- Conversations not persisted properly
- No context across messages
- Supabase integration incomplete

### 4. Output Structure Messy
- Inconsistent streaming events
- No clear separation of concerns
- Frontend can't parse responses properly

### 5. Agent Swarm Not Working
- No proper agent orchestration
- Tools not executing correctly
- No parallel agent execution

---

## New Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           McLEUKER AI V2 ARCHITECTURE                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   FRONTEND   │────▶│   BACKEND    │────▶│   AGENT      │────▶│   EXTERNAL   │
│   (Next.js)  │◀────│   (FastAPI)  │◀────│   ORCH.      │◀────│   APIs       │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │   SUPABASE   │
                     │  (Postgres)  │
                     └──────────────┘
```

### Core Components

1. **Hybrid LLM Router** - Routes requests to Kimi-2.5 or Grok based on task
2. **Agent Orchestrator** - Manages agent swarm and tool execution
3. **Memory Manager** - Handles conversation persistence
4. **File Engine** - Proper file generation with data extraction
5. **Search Layer** - Unified search across all sources

---

## Hybrid LLM Architecture (Kimi-2.5 + Grok)

### When to Use Each Model

| Task Type | Primary Model | Secondary Model | Reason |
|-----------|---------------|-----------------|--------|
| Complex reasoning | Kimi-2.5 | - | Best reasoning capabilities |
| Real-time data | Grok | Kimi-2.5 | Grok has X/Twitter access |
| File generation | Kimi-2.5 | - | Better structured output |
| Code generation | Kimi-2.5 | Grok | Both are good, Kimi for structure |
| Quick responses | Grok | - | Faster for simple queries |
| Deep research | Kimi-2.5 + Grok | - | Hybrid for comprehensive results |

### Hybrid Mode Implementation

```python
class HybridLLMRouter:
    """Routes requests between Kimi-2.5 and Grok based on task analysis."""
    
    async def route(self, query: str, context: Dict) -> LLMResponse:
        # Analyze query intent
        intent = self._analyze_intent(query)
        
        # Route to appropriate model(s)
        if intent.requires_realtime:
            # Use Grok for real-time + Kimi for synthesis
            grok_result = await self.grok.search(query)
            kimi_result = await self.kimi.synthesize(grok_result, query)
            return self._merge_results(kimi_result, grok_result)
        elif intent.requires_reasoning:
            # Use Kimi-2.5 for complex reasoning
            return await self.kimi.reason(query, context)
        else:
            # Default to Kimi-2.5
            return await self.kimi.chat(query, context)
```

---

## Agent Swarm Architecture

### Agent Types

1. **Research Agent** - Gathers information from multiple sources
2. **Analysis Agent** - Analyzes data and finds patterns
3. **Synthesis Agent** - Combines multiple outputs into coherent response
4. **File Agent** - Generates files (Excel, PDF, etc.)
5. **Code Agent** - Generates and executes code
6. **Critique Agent** - Reviews and improves outputs

### Agent Orchestration Flow

```
User Query
    │
    ▼
[Intent Classifier] ──▶ Determines required agents
    │
    ▼
[Agent Dispatcher] ──▶ Spawns agents in parallel
    │
    ├──▶ Research Agent ──▶ Search APIs
    ├──▶ Analysis Agent ──▶ Data processing
    └──▶ File Agent ──▶ File generation (if needed)
    │
    ▼
[Result Aggregator] ──▶ Combines agent outputs
    │
    ▼
[Synthesis Agent] ──▶ Creates final response
    │
    ▼
[Output to User]
```

---

## Memory System Architecture

### Conversation Memory

```sql
-- conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    title TEXT,
    mode TEXT, -- instant, thinking, agent, swarm, research, code
    context JSONB, -- conversation context/state
    memory_summary TEXT, -- summarized memory for context window
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);

-- messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id),
    role TEXT, -- user, assistant, system, tool
    content TEXT,
    reasoning_content TEXT, -- Kimi-2.5 reasoning
    tool_calls JSONB,
    tool_results JSONB,
    tokens_used INTEGER,
    latency_ms INTEGER,
    metadata JSONB,
    created_at TIMESTAMPTZ
);

-- memory snapshots for long conversations
CREATE TABLE memory_snapshots (
    id UUID PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id),
    summary TEXT,
    key_points JSONB,
    created_at TIMESTAMPTZ
);
```

### Memory Management Flow

1. **Short-term memory**: Last N messages kept in context
2. **Long-term memory**: Older messages summarized and stored
3. **Context injection**: Relevant past context injected into new queries

---

## File Generation Architecture

### Fixed Data Pipeline

```
User Request ("Create Excel with top influencers")
    │
    ▼
[Search APIs] ──▶ Perplexity, Google, Exa
    │
    ▼
[Data Extractor] ──▶ Structured data extraction
    │
    ├──▶ entities: [{name, handle, followers, ...}]
    ├──▶ sources: [{title, url, source}]
    └──▶ metrics: {count, avg_followers, ...}
    │
    ▼
[Content Generator] ──▶ Kimi-2.5 creates structure
    │
    ▼
[File Builder] ──▶ Creates actual Excel file
    │
    ▼
[Storage] ──▶ Save to disk + Supabase
    │
    ▼
[Download URL] ──▶ Return to user
```

### Data Extraction Strategy

```python
class DataExtractor:
    """Extracts structured data from search results for file generation."""
    
    def extract(self, search_results: Dict, query: str) -> StructuredData:
        # Extract entities based on query type
        if self._is_influencer_query(query):
            return self._extract_influencers(search_results)
        elif self._is_company_query(query):
            return self._extract_companies(search_results)
        elif self._is_product_query(query):
            return self._extract_products(search_results)
        else:
            return self._extract_generic(search_results)
```

---

## Output Structure Standardization

### Streaming Event Types

```typescript
// All events follow this structure
interface StreamEvent {
    type: 'task_progress' | 'reasoning' | 'content' | 'tool_call' | 
          'search_sources' | 'download' | 'follow_up' | 'complete' | 'error';
    data: any;
    timestamp: string;
}

// Task progress
interface TaskProgressEvent {
    type: 'task_progress';
    data: {
        step: string;
        title: string;
        status: 'pending' | 'active' | 'complete' | 'error';
        detail?: string;
        progress?: number; // 0-100
    };
}

// Reasoning (Kimi-2.5 thinking)
interface ReasoningEvent {
    type: 'reasoning';
    data: {
        chunk: string;
        step?: string;
    };
}

// Content
interface ContentEvent {
    type: 'content';
    data: {
        chunk: string;
    };
}

// Tool call
interface ToolCallEvent {
    type: 'tool_call';
    data: {
        tool: string;
        input: any;
        status: 'started' | 'completed' | 'error';
        output?: any;
    };
}

// Search sources
interface SearchSourcesEvent {
    type: 'search_sources';
    data: {
        sources: Array<{
            title: string;
            url: string;
            snippet?: string;
            source: string;
        }>;
    };
}

// Download
interface DownloadEvent {
    type: 'download';
    data: {
        file_id: string;
        filename: string;
        file_type: string;
        download_url: string;
        size?: number;
    };
}

// Follow-up questions
interface FollowUpEvent {
    type: 'follow_up';
    data: {
        questions: string[];
    };
}

// Complete
interface CompleteEvent {
    type: 'complete';
    data: {
        content: string;
        reasoning?: string;
        downloads: DownloadInfo[];
        sources: SourceInfo[];
        follow_up_questions: string[];
        usage: {
            prompt_tokens: number;
            completion_tokens: number;
            total_tokens: number;
        };
    };
}

// Error
interface ErrorEvent {
    type: 'error';
    data: {
        message: string;
        code?: string;
        recoverable?: boolean;
    };
}
```

---

## Mode Definitions

### 1. Instant Mode
- **Model**: Grok (fast) or Kimi-2.5 (if Grok unavailable)
- **Features**: Quick responses, no reasoning shown
- **Use case**: Simple questions, quick lookups
- **Tools**: Minimal

### 2. Thinking Mode
- **Model**: Kimi-2.5
- **Features**: Step-by-step reasoning visible
- **Use case**: Complex problems, explanations
- **Tools**: Search, analysis

### 3. Agent Mode
- **Model**: Kimi-2.5 with tool use
- **Features**: Tools + real-time search + file generation
- **Use case**: Research, data gathering, file creation
- **Tools**: All available tools

### 4. Swarm Mode
- **Model**: Kimi-2.5 with parallel agents
- **Features**: 5-50 parallel agents for complex tasks
- **Use case**: Comprehensive research, multi-faceted analysis
- **Tools**: All tools with parallel execution

### 5. Research Mode
- **Model**: Hybrid (Kimi-2.5 + Grok)
- **Features**: Deep research with report generation
- **Use case**: In-depth analysis, comprehensive reports
- **Tools**: All search sources, file generation

### 6. Code Mode
- **Model**: Kimi-2.5 (primary) + Grok (secondary)
- **Features**: Code generation and execution
- **Use case**: Programming, data analysis
- **Tools**: Code sandbox, file generation

---

## API Endpoints

### Chat Endpoints

```
POST /api/v1/chat              # Non-streaming chat
POST /api/v1/chat/stream       # Streaming chat (SSE)
POST /api/v1/chat/with-memory  # Chat with conversation memory
```

### Agent Endpoints

```
POST /api/v1/agent/execute     # Execute single agent
POST /api/v1/swarm/execute     # Execute agent swarm
GET  /api/v1/agent/status/{id} # Get agent execution status
```

### File Endpoints

```
POST /api/v1/files/generate    # Generate file
GET  /api/v1/files/{id}        # Get file info
GET  /api/v1/files/{id}/download  # Download file
DELETE /api/v1/files/{id}      # Delete file
```

### Memory Endpoints

```
GET    /api/v1/conversations           # List conversations
POST   /api/v1/conversations           # Create conversation
GET    /api/v1/conversations/{id}      # Get conversation
DELETE /api/v1/conversations/{id}      # Delete conversation
GET    /api/v1/conversations/{id}/messages  # Get messages
POST   /api/v1/conversations/{id}/messages  # Add message
```

### Search Endpoints

```
POST /api/v1/search            # Multi-source search
POST /api/v1/search/perplexity # Perplexity search
POST /api/v1/search/grok       # Grok search
POST /api/v1/search/google     # Google search
```

---

## Implementation Phases

### Phase 1: Core Backend (Week 1)
- [ ] Fix Kimi-2.5 configuration
- [ ] Implement proper data extraction
- [ ] Fix file generation pipeline
- [ ] Standardize output structure

### Phase 2: Memory System (Week 1-2)
- [ ] Update Supabase schema
- [ ] Implement conversation persistence
- [ ] Add memory management
- [ ] Test memory retrieval

### Phase 3: Agent Swarm (Week 2)
- [ ] Implement agent orchestrator
- [ ] Create agent types
- [ ] Add parallel execution
- [ ] Test agent coordination

### Phase 4: Hybrid LLM (Week 2-3)
- [ ] Implement LLM router
- [ ] Add Grok integration
- [ ] Create hybrid mode
- [ ] Test model coordination

### Phase 5: Frontend Updates (Week 3)
- [ ] Update mode selector
- [ ] Add memory UI
- [ ] Fix download handling
- [ ] Update event parsing

### Phase 6: Testing & Deployment (Week 4)
- [ ] Comprehensive testing
- [ ] Performance optimization
- [ ] Documentation
- [ ] Production deployment

---

## Success Metrics

### File Generation
- Excel files contain real data: >95% success rate
- Download success rate: >99%
- Average generation time: <30 seconds

### Chat Quality
- Reasoning visible in thinking mode: 100%
- Tool execution success: >95%
- Context retention: Full conversation history

### Agent Swarm
- Parallel agent execution: Working
- Result aggregation: Accurate
- Task completion: >90%

### Memory
- Conversation persistence: 100%
- Memory retrieval: <100ms
- Context injection: Relevant

---

## Next Steps

1. Review this architecture document
2. Approve the approach
3. Begin Phase 1 implementation
4. Test each phase before proceeding
5. Deploy incrementally
