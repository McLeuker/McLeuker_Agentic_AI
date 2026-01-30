# Lovable Integration Guide

This document provides a step-by-step guide for integrating the McLeuker Agentic AI Platform backend with a Lovable frontend.

## 1. Overview

The backend is built with FastAPI and provides a RESTful API that can be consumed by any frontend framework, including Lovable. The integration involves:

1.  Deploying the backend to a cloud server.
2.  Configuring CORS to allow requests from your Lovable domain.
3.  Creating API client hooks in your Lovable frontend.
4.  Connecting UI components to the API.

## 2. Backend Deployment

Before integrating with Lovable, you need to deploy the backend to a publicly accessible server. Here are some options:

*   **Railway.app:** Easy deployment for Python apps.
*   **Render.com:** Free tier available for web services.
*   **AWS / GCP / Azure:** For more control and scalability.
*   **Vercel (for serverless functions):** If you want to deploy individual API endpoints.

### Example: Deploying to Railway

1.  Push your code to a GitHub repository.
2.  Connect your GitHub account to Railway.
3.  Create a new project and select your repository.
4.  Railway will automatically detect the `requirements.txt` and deploy the app.
5.  Set the environment variables in the Railway dashboard.
6.  Your backend will be available at a URL like `https://your-app.up.railway.app`.

## 3. CORS Configuration

The backend is already configured to allow CORS from all origins (`allow_origins=["*"]`). For production, you should restrict this to your Lovable domain:

```python
# In src/api/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-lovable-app.lovable.app"],  # Replace with your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 4. Lovable Frontend Integration

### 4.1. API Client Setup

Create a new file in your Lovable project to handle API calls.

**`src/lib/api.ts`**

```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface TaskRequest {
  prompt: string;
  user_id?: string;
  preferred_outputs?: string[];
  domain_hint?: string;
}

export interface TaskResponse {
  task_id: string;
  status: string;
  interpretation?: any;
  files?: any[];
  message?: string;
  error?: string;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface ChatResponse {
  message: string;
  action_taken?: string;
  task_id?: string;
  files?: any[];
  sources?: any[];
}

export interface SearchRequest {
  query: string;
  num_results?: number;
  summarize?: boolean;
}

export interface SearchResponse {
  query: string;
  summary?: string;
  results: any[];
  follow_up_questions?: string[];
}

// --- API Functions ---

export async function processTask(request: TaskRequest): Promise<TaskResponse> {
  const response = await fetch(`${API_BASE_URL}/api/tasks/sync`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }
  return response.json();
}

export async function chat(request: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }
  return response.json();
}

export async function search(request: SearchRequest): Promise<SearchResponse> {
  const response = await fetch(`${API_BASE_URL}/api/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }
  return response.json();
}

export async function getTaskStatus(taskId: string): Promise<TaskResponse> {
  const response = await fetch(`${API_BASE_URL}/api/tasks/${taskId}`);
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }
  return response.json();
}

export function getFileDownloadUrl(filename: string): string {
  return `${API_BASE_URL}/api/files/${filename}`;
}
```

### 4.2. React Hooks

Create custom hooks for using the API in your components.

**`src/hooks/useChat.ts`**

```typescript
import { useState, useCallback } from 'react';
import { chat, ChatRequest, ChatResponse } from '@/lib/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  files?: any[];
}

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(async (content: string) => {
    setIsLoading(true);
    setError(null);

    // Add user message immediately
    setMessages((prev) => [...prev, { role: 'user', content }]);

    try {
      const response = await chat({ message: content });
      
      // Add assistant response
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: response.message,
          files: response.files,
        },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return { messages, isLoading, error, sendMessage, clearMessages };
}
```

**`src/hooks/useTask.ts`**

```typescript
import { useState, useCallback } from 'react';
import { processTask, TaskRequest, TaskResponse } from '@/lib/api';

export function useTask() {
  const [task, setTask] = useState<TaskResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submitTask = useCallback(async (prompt: string, options?: Partial<TaskRequest>) => {
    setIsLoading(true);
    setError(null);
    setTask(null);

    try {
      const response = await processTask({ prompt, ...options });
      setTask(response);
      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { task, isLoading, error, submitTask };
}
```

### 4.3. Example Component

Here's an example of a chat component that uses the `useChat` hook.

**`src/components/ChatInterface.tsx`**

```tsx
import { useState } from 'react';
import { useChat } from '@/hooks/useChat';
import { getFileDownloadUrl } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, Send, Download } from 'lucide-react';

export function ChatInterface() {
  const [input, setInput] = useState('');
  const { messages, isLoading, error, sendMessage } = useChat();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    
    const message = input;
    setInput('');
    await sendMessage(message);
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>McLeuker AI Assistant</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4 mb-4 max-h-96 overflow-y-auto">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`p-3 rounded-lg ${
                msg.role === 'user'
                  ? 'bg-blue-100 ml-8'
                  : 'bg-gray-100 mr-8'
              }`}
            >
              <p className="text-sm font-semibold mb-1">
                {msg.role === 'user' ? 'You' : 'McLeuker AI'}
              </p>
              <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
              
              {/* Display files if any */}
              {msg.files && msg.files.length > 0 && (
                <div className="mt-2 space-y-1">
                  <p className="text-xs font-semibold text-gray-600">Generated Files:</p>
                  {msg.files.map((file, fileIndex) => (
                    <a
                      key={fileIndex}
                      href={getFileDownloadUrl(file.filename)}
                      className="flex items-center gap-1 text-xs text-blue-600 hover:underline"
                      download
                    >
                      <Download className="w-3 h-3" />
                      {file.filename}
                    </a>
                  ))}
                </div>
              )}
            </div>
          ))}
          
          {isLoading && (
            <div className="flex items-center gap-2 text-gray-500">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span className="text-sm">Thinking...</span>
            </div>
          )}
        </div>

        {error && (
          <p className="text-red-500 text-sm mb-2">{error}</p>
        )}

        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask me anything or describe a task..."
            disabled={isLoading}
          />
          <Button type="submit" disabled={isLoading || !input.trim()}>
            <Send className="w-4 h-4" />
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
```

## 5. Environment Variables

In your Lovable project, create a `.env` file (or use the Lovable environment settings) to set the API base URL:

```env
VITE_API_BASE_URL=https://your-backend-url.com
```

## 6. WebSocket Integration (Optional)

For real-time updates during long-running tasks, you can use WebSockets.

**`src/hooks/useWebSocket.ts`**

```typescript
import { useEffect, useRef, useState, useCallback } from 'react';

const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000';

interface WebSocketMessage {
  type: string;
  task_id?: string;
  status?: string;
  files?: any[];
  [key: string]: any;
}

export function useWebSocket(userId: string) {
  const ws = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);

  useEffect(() => {
    ws.current = new WebSocket(`${WS_BASE_URL}/ws/${userId}`);

    ws.current.onopen = () => {
      setIsConnected(true);
    };

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setLastMessage(data);
    };

    ws.current.onclose = () => {
      setIsConnected(false);
    };

    // Ping to keep connection alive
    const pingInterval = setInterval(() => {
      if (ws.current?.readyState === WebSocket.OPEN) {
        ws.current.send('ping');
      }
    }, 30000);

    return () => {
      clearInterval(pingInterval);
      ws.current?.close();
    };
  }, [userId]);

  return { isConnected, lastMessage };
}
```

## 7. Testing the Integration

1.  Start your backend server locally: `python -m src.api.main`
2.  Start your Lovable development server.
3.  Open the chat interface and send a message like "Create a competitor analysis for sustainable fashion brands."
4.  The backend will process the request and return the generated files.

## 8. Troubleshooting

*   **CORS errors:** Make sure the backend CORS settings include your Lovable domain.
*   **Connection refused:** Ensure the backend is running and the `VITE_API_BASE_URL` is correct.
*   **API errors:** Check the backend logs for detailed error messages.
