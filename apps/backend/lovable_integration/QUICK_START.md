# McLeuker AI - Lovable Quick Start Guide

This guide will help you integrate the McLeuker AI backend with your Lovable frontend in just a few minutes.

## Step 1: Deploy the Backend

### Option A: Deploy to Railway (Recommended)

1. Go to [Railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select the `McLeuker/McLeuker_Agentic_AI` repository
4. Railway will automatically detect the Dockerfile
5. Add your environment variables in the Railway dashboard:
   - `OPENAI_API_KEY`
   - `GROK_API_KEY`
   - `GOOGLE_SEARCH_API_KEY`
   - `PERPLEXITY_API_KEY`
   - (and any other API keys you want to use)
6. Click "Deploy"
7. Copy your deployment URL (e.g., `https://mcleuker-ai.railway.app`)

### Option B: Deploy to Render

1. Go to [Render.com](https://render.com)
2. Click "New" → "Web Service"
3. Connect your GitHub account and select the repository
4. Render will use the `render.yaml` configuration
5. Add environment variables in the dashboard
6. Deploy and copy your URL

## Step 2: Add to Lovable

### Copy the Integration File

Copy the `McLeukerAI.tsx` file from this folder to your Lovable project:

```
lovable_integration/McLeukerAI.tsx → your-lovable-project/src/components/McLeukerAI.tsx
```

### Update the API URL

Open `McLeukerAI.tsx` and update the `API_BASE_URL`:

```typescript
const API_BASE_URL = 'https://your-backend-url.railway.app';  // Your deployed URL
```

Or set it as an environment variable in Lovable:
```
REACT_APP_API_URL=https://your-backend-url.railway.app
```

## Step 3: Use the Components

### Chat Interface

```tsx
import { McLeukerChatInterface } from './components/McLeukerAI';

function ChatPage() {
  return (
    <div className="h-screen">
      <McLeukerChatInterface 
        welcomeMessage="Hello! How can I help you today?"
        placeholder="Type your message..."
      />
    </div>
  );
}
```

### AI Search

```tsx
import { McLeukerSearchInterface } from './components/McLeukerAI';

function SearchPage() {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">AI Search</h1>
      <McLeukerSearchInterface 
        placeholder="Search for anything..."
      />
    </div>
  );
}
```

### Task Submitter

```tsx
import { McLeukerTaskSubmitter } from './components/McLeukerAI';

function TaskPage() {
  const handleComplete = (result) => {
    console.log('Task completed:', result);
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Create a Task</h1>
      <McLeukerTaskSubmitter onComplete={handleComplete} />
    </div>
  );
}
```

### Status Indicator

```tsx
import { McLeukerStatusIndicator } from './components/McLeukerAI';

function Header() {
  return (
    <header className="flex justify-between items-center p-4">
      <h1>McLeuker AI</h1>
      <McLeukerStatusIndicator />
    </header>
  );
}
```

## Step 4: Use the Hooks (Advanced)

For more control, use the hooks directly:

```tsx
import { useMcLeukerChat, useMcLeukerSearch, useMcLeukerTask } from './components/McLeukerAI';

function CustomComponent() {
  const { messages, sendMessage, isLoading } = useMcLeukerChat();
  const { search, results, isSearching } = useMcLeukerSearch();
  const { submitTask, result, isProcessing } = useMcLeukerTask();

  // Your custom implementation
}
```

## Step 5: Use the API Client Directly

For maximum flexibility:

```tsx
import { mcLeukerAPI } from './components/McLeukerAI';

// Health check
const health = await mcLeukerAPI.getHealth();

// Create a task
const result = await mcLeukerAPI.createTask('Create a market analysis report');

// Search
const searchResults = await mcLeukerAPI.search('AI trends 2025');

// Quick answer
const answer = await mcLeukerAPI.quickAnswer('What is the capital of France?');

// Research a topic
const research = await mcLeukerAPI.research('Sustainable fashion', 'deep');
```

## Environment Variables

For production, set these in your Lovable project:

```env
REACT_APP_API_URL=https://your-backend-url.railway.app
```

## Troubleshooting

### CORS Errors

The backend is configured to allow all origins by default. If you still get CORS errors:

1. Check that your backend is running
2. Verify the `CORS_ORIGINS` environment variable includes your Lovable URL

### Connection Errors

1. Verify your backend URL is correct
2. Check that the backend is deployed and running
3. Use the `McLeukerStatusIndicator` component to check connection status

### API Key Errors

If you get authentication errors:

1. Verify your API keys are set correctly in the backend environment
2. Check the `/api/config/status` endpoint to see which services are configured

## Support

For issues or questions:
- Check the main README.md in the repository
- Open an issue on GitHub
- Contact the McLeuker team
