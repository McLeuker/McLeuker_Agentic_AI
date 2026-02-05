# Kimi K2.5 Integration Guide

## Overview

McLeuker AI now uses a **dual-model architecture**:

- **Grok (xAI)**: Primary reasoning model for intent understanding, planning, and response synthesis
- **Kimi K2.5 (Moonshot AI)**: Execution model for code generation, tool calling, and agentic workflows

This provides best-in-class capabilities while reducing costs by 77%.

---

## Quick Start

### 1. Get Your Kimi API Key

1. Visit [platform.moonshot.cn](https://platform.moonshot.cn)
2. Sign up for an account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-...`)

### 2. Add to Environment

Edit `apps/backend/.env`:

```bash
# Add your Kimi API key
MOONSHOT_API_KEY=sk-your-actual-kimi-api-key-here
```

### 3. Verify Configuration

```bash
cd apps/backend
python -c "from src.config.settings import settings; print(f'Kimi configured: {settings.is_kimi_configured()}')"
```

Should output: `Kimi configured: True`

---

## Usage Examples

### Example 1: Code Generation (Kimi Execution)

```python
from src.core.hybrid_brain import hybrid_brain, TaskType

# Generate code using Kimi
response = await hybrid_brain.think(
    query="Generate Python code to analyze fashion trends from CSV data",
    task_type=TaskType.EXECUTION
)

print(response.content)  # Generated code
print(f"Cost: ${response.cost:.4f}")  # Very low cost with Kimi
print(f"Models used: {response.models_used}")  # ['kimi']
```

### Example 2: Reasoning (Grok Only)

```python
# Pure reasoning using Grok
response = await hybrid_brain.think(
    query="What are the key fashion trends for Spring 2026?",
    task_type=TaskType.REASONING
)

print(response.content)  # Trend analysis
print(f"Models used: {response.models_used}")  # ['grok']
```

### Example 3: Hybrid Workflow (Both Models)

```python
# Complex task using both models
response = await hybrid_brain.think(
    query="Analyze SS26 trends and generate an Excel report with data visualizations",
    task_type=TaskType.HYBRID  # Default
)

# Flow:
# 1. Grok: Understand query and plan approach
# 2. Kimi: Execute searches, generate Excel code
# 3. Grok: Synthesize final response

print(f"Models used: {response.models_used}")  # ['grok', 'kimi']
print(f"Total cost: ${response.cost:.4f}")  # Optimized cost
```

---

## Cost Comparison

### Before (Grok Only)

```
Query: "Generate fashion trend report with Excel export"
- Tokens: 1M input + 500K output
- Cost: $82.50
- Model: Grok
```

### After (Hybrid)

```
Query: "Generate fashion trend report with Excel export"
- Reasoning (Grok): 200K tokens = $16.50
- Execution (Kimi): 800K tokens = $2.08
- Total Cost: $18.58 (77% savings!)
- Models: Grok + Kimi
```

---

## Model Selection Logic

The hybrid brain automatically routes tasks:

| Query Type           | Model  | Reason                             |
| -------------------- | ------ | ---------------------------------- |
| "What is...?"        | Grok   | Pure reasoning                     |
| "Generate code..."   | Kimi   | Code generation (97% cheaper)      |
| "Create Excel..."    | Kimi   | Execution task                     |
| "Analyze trends..."  | Hybrid | Planning (Grok) + Execution (Kimi) |
| "Debug this code..." | Kimi   | Code analysis                      |
| "Explain why..."     | Grok   | Reasoning                          |

---

## API Reference

### KimiClient

```python
from src.core.kimi_client import kimi_client

# Execute a task
response = await kimi_client.execute(
    query="Generate Python code for data analysis",
    context="Additional context here",
    temperature=0.7
)

# With tool calling
response = await kimi_client.execute_with_tools(
    query="Search for sustainable suppliers",
    tools=[...],  # Tool definitions
    max_iterations=5
)

# Streaming
async for chunk in kimi_client._execute_stream(payload):
    print(chunk, end='')
```

### HybridBrain

```python
from src.core.hybrid_brain import hybrid_brain, TaskType

# Auto-routing (default)
response = await hybrid_brain.think(query="Your query")

# Force reasoning only
response = await hybrid_brain.think(
    query="Your query",
    task_type=TaskType.REASONING
)

# Force execution only
response = await hybrid_brain.think(
    query="Your query",
    task_type=TaskType.EXECUTION
)

# Streaming
async for chunk in hybrid_brain.think_stream(query="Your query"):
    print(chunk, end='')
```

---

## Testing

### Run Tests

```bash
cd apps/backend
pytest tests/test_kimi_integration.py -v
```

### Manual Testing

```python
# Test Kimi connectivity
from src.core.kimi_client import kimi_client

response = await kimi_client.execute("Say hello")
assert response.success
print(f"✅ Kimi working! Cost: ${response.cost:.6f}")

# Test hybrid brain
from src.core.hybrid_brain import hybrid_brain

response = await hybrid_brain.think("Generate a simple Python function")
assert response.success
print(f"✅ Hybrid brain working! Models: {response.models_used}")
```

---

## Troubleshooting

### "MOONSHOT_API_KEY not configured"

**Solution**: Add your Kimi API key to `.env`:

```bash
MOONSHOT_API_KEY=sk-your-key-here
```

### "Kimi not configured - execution will use Grok fallback"

**Solution**: This is a warning, not an error. The system will use Grok for execution if Kimi is not configured. Add Kimi API key to enable dual-model mode.

### High costs

**Solution**: Check that `ENABLE_MULTI_MODEL=true` in `.env`. This ensures Kimi is used for execution tasks (97% cheaper than Grok).

### Slow responses

**Solution**:

1. Check `KIMI_MAX_TOKENS` (default: 32768)
2. Reduce if needed for faster responses
3. Use `TaskType.EXECUTION` to skip Grok planning for simple tasks

---

## Best Practices

### 1. Use Appropriate Task Types

```python
# ✅ Good: Use EXECUTION for code tasks
response = await hybrid_brain.think(
    "Generate Python code",
    task_type=TaskType.EXECUTION  # Skip Grok, use Kimi directly
)

# ❌ Bad: Using REASONING for code tasks
response = await hybrid_brain.think(
    "Generate Python code",
    task_type=TaskType.REASONING  # Wastes Grok tokens
)
```

### 2. Provide Context

```python
# ✅ Good: Provide context for better results
response = await hybrid_brain.think(
    query="Optimize this code",
    context="Code: def slow_function()..."
)

# ❌ Bad: No context
response = await hybrid_brain.think("Optimize this code")
```

### 3. Monitor Costs

```python
# Track costs per request
response = await hybrid_brain.think(query)
print(f"Cost: ${response.cost:.4f}")
print(f"Models: {response.models_used}")

# Log for analysis
logger.info(f"Query cost: ${response.cost}, models: {response.models_used}")
```

---

## Deployment

### Environment Variables

Required for production:

```bash
# Core Models
XAI_API_KEY=xai-...              # Grok (reasoning)
MOONSHOT_API_KEY=sk-...          # Kimi (execution)

# Model Configuration
DEFAULT_LLM_PROVIDER=grok
ENABLE_MULTI_MODEL=true
KIMI_MODEL=kimi-k2.5
KIMI_MAX_TOKENS=32768
```

### Railway Deployment

1. Add environment variables in Railway dashboard
2. Redeploy backend
3. Verify with health check:

```bash
curl https://your-backend.railway.app/api/status
```

Should show:

```json
{
  "services": {
    "grok": true,
    "kimi": true
  }
}
```

---

## Monitoring

### Cost Tracking

```python
# Add to your logging
logger.info(f"""
Request completed:
- Query: {query[:50]}...
- Models: {response.models_used}
- Tokens: {response.tokens_used}
- Cost: ${response.cost:.4f}
- Success: {response.success}
""")
```

### Performance Metrics

```python
import time

start = time.time()
response = await hybrid_brain.think(query)
duration = time.time() - start

logger.info(f"Response time: {duration:.2f}s, Cost: ${response.cost:.4f}")
```

---

## FAQ

**Q: When should I use Kimi vs Grok?**
A: Use Kimi for execution (code, tools, actions). Use Grok for reasoning (planning, understanding). Use HYBRID for complex tasks.

**Q: How much can I save?**
A: Up to 77% on execution-heavy workloads. Pure reasoning tasks still use Grok.

**Q: Is Kimi as good as Grok?**
A: Kimi excels at coding and tool calling (SWE-Bench leader). Grok is better for reasoning and natural language.

**Q: Can I use only Kimi?**
A: Yes, set `DEFAULT_LLM_PROVIDER=kimi` and use `TaskType.EXECUTION`. But hybrid mode is recommended.

**Q: What if Kimi is down?**
A: The system automatically falls back to Grok for execution tasks.

---

## Next Steps

1. ✅ Get Kimi API key
2. ✅ Add to `.env`
3. ✅ Test integration
4. ✅ Monitor costs
5. ✅ Optimize task routing

For support, check the [implementation plan](kimi_implementation_plan.md).
