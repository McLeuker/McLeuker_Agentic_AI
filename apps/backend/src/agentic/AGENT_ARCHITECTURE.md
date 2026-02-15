# McLeuker Agent Mode Architecture

## Overview

Agent mode is the **smartest mode** — it combines Q&A intelligence with real-world execution capabilities.

## Smart Routing

Every request goes through intent classification:

```
User Request → Intent Classifier → Route Decision
                                    ├── Simple Q&A → ChatHandler (reasoning-first response)
                                    ├── File Generation → ChatHandler + FileEngine
                                    ├── Execution Task → ExecutionOrchestrator
                                    │   ├── Browser Automation (Playwright + screenshots)
                                    │   ├── Code Execution (E2B sandbox)
                                    │   ├── GitHub Operations (API)
                                    │   └── Research (Search APIs)
                                    └── Ambiguous → ChatHandler (ask clarification)
```

## Browser Automation Capabilities

### Supported Platforms
- **Any website** — navigate, read, extract content
- **GitHub** — read repos, create issues, PRs (via API + browser)
- **Gmail** — compose, read (requires user OAuth)
- **Canva** — design interaction (requires user login)
- **Any web app** — form filling, clicking, scrolling

### How It Works
1. **Playwright** (primary): Headless Chromium with live screenshot streaming
2. **Browserless** (fallback): Content extraction when Playwright fails
3. **LLM Vision** (CUA loop): screenshot → vision model → next action → repeat

### Screenshot Streaming
- Every browser action captures a screenshot
- Screenshots are base64-encoded and streamed via SSE
- Frontend displays them in real-time in the execution panel

## Credential System (Future)

### User Credentials Flow
```
User → Settings → Add Credential (encrypted) → Supabase vault
Agent → Needs credential → Fetch from vault → Inject into browser session
```

### Supported Credential Types
- **OAuth tokens** (GitHub, Google, etc.)
- **API keys** (user's own keys)
- **Session cookies** (for platforms without API)

### Security
- All credentials encrypted at rest (Supabase vault)
- Credentials never logged or stored in plain text
- User can revoke any credential at any time
- Agent requests credential permission before first use

## File Generation Pipeline

### Supported Formats
- **Excel** (.xlsx) — multi-tab, charts, formatting
- **PDF** — markdown → HTML → PDF
- **Word** (.docx) — structured document
- **PowerPoint** (.pptx) — slide deck with content
- **CSV** — data export

### Quality System
- Model chain: Kimi → Grok (primary → fallback)
- Self-correction: if JSON parse fails, re-prompt with error
- Retry: up to 3 attempts per generation
- No timeouts — quality over speed
- Search data feeding for real, verified content

## Task Progress Events

### Event Types
- `execution_start` — task begins
- `step_update` — individual step progress
- `execution_progress` — overall % complete
- `execution_reasoning` — AI thinking process
- `browser_screenshot` — live browser view
- `execution_artifact` — generated file/output
- `execution_complete` — task finished

### Frontend Display
- Inline collapsible progress in message field
- Live browser preview in execution panel
- Source pills with favicons
- Download buttons for generated files
