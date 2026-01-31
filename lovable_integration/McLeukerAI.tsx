/**
 * McLeuker Agentic AI Platform - Complete Lovable Integration
 * 
 * LIVE BACKEND URL: https://web-production-29f3c.up.railway.app
 * 
 * Usage:
 * 1. Copy this file to your Lovable project's src/components folder
 * 2. The API_BASE_URL is already configured to your live backend
 * 3. Import and use the components in your pages
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';

// ============================================================================
// CONFIGURATION - YOUR LIVE BACKEND URL
// ============================================================================

const API_BASE_URL = import.meta.env.VITE_RAILWAY_API_URL || 'https://web-production-29f3c.up.railway.app';

// ============================================================================
// TYPES
// ============================================================================

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  files?: GeneratedFile[];
  sources?: SearchResult[];
}

export interface GeneratedFile {
  filename: string;
  filepath: string;
  format: string;
  size_bytes?: number;
  download_url?: string;
}

export interface TaskInterpretation {
  intent: string;
  domain: string;
  complexity: string;
  required_outputs: string[];
  requires_research: boolean;
  confidence: number;
}

export interface TaskResult {
  task_id: string;
  status: string;
  interpretation?: TaskInterpretation;
  files?: GeneratedFile[];
  message?: string;
  error?: string;
}

export interface SearchResult {
  title: string;
  url: string;
  snippet: string;
  source?: string;
}

export interface AISearchResponse {
  query: string;
  expanded_queries: string[];
  results: SearchResult[];
  total_results: number;
  summary?: string;
  follow_up_questions?: string[];
}

export interface ConfigStatus {
  status: string;
  services: {
    has_llm: boolean;
    has_search: boolean;
  };
  default_llm: string;
}

// ============================================================================
// API CLIENT
// ============================================================================

class McLeukerAPIClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  async getHealth(): Promise<{ status: string; version: string; timestamp: string }> {
    return this.request('/health');
  }

  async getStatus(): Promise<any> {
    return this.request('/api/status');
  }

  async getConfigStatus(): Promise<ConfigStatus> {
    return this.request('/api/config/status');
  }

  async createTask(prompt: string, userId?: string): Promise<TaskResult> {
    return this.request('/api/tasks/sync', {
      method: 'POST',
      body: JSON.stringify({ prompt, user_id: userId }),
    });
  }

  async chat(message: string, conversationId?: string): Promise<any> {
    return this.request('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ message, conversation_id: conversationId }),
    });
  }

  async search(query: string, options?: { numResults?: number; summarize?: boolean }): Promise<AISearchResponse> {
    return this.request('/api/search', {
      method: 'POST',
      body: JSON.stringify({
        query,
        num_results: options?.numResults || 10,
        summarize: options?.summarize ?? true,
      }),
    });
  }

  async quickAnswer(question: string): Promise<{ answer: string; sources: string[] }> {
    return this.request('/api/search/quick', {
      method: 'POST',
      body: JSON.stringify({ question }),
    });
  }

  async research(topic: string, depth?: string): Promise<any> {
    return this.request('/api/research', {
      method: 'POST',
      body: JSON.stringify({ topic, depth: depth || 'medium' }),
    });
  }

  getFileDownloadUrl(filename: string): string {
    return `${this.baseUrl}/api/files/${filename}`;
  }
}

export const mcLeukerAPI = new McLeukerAPIClient();

// ============================================================================
// HOOKS
// ============================================================================

export function useMcLeukerChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId] = useState(() => `conv_${Date.now()}`);

  const sendMessage = useCallback(async (content: string) => {
    setIsLoading(true);
    setError(null);

    const userMessage: Message = {
      id: `msg_${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);

    try {
      const response = await mcLeukerAPI.chat(content, conversationId);

      const assistantMessage: Message = {
        id: `msg_${Date.now() + 1}`,
        role: 'assistant',
        content: response.message || response.response,
        timestamp: new Date(),
        files: response.files,
        sources: response.sources,
      };
      setMessages(prev => [...prev, assistantMessage]);

      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [conversationId]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return { messages, isLoading, error, sendMessage, clearMessages };
}

export function useMcLeukerTask() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<TaskResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const submitTask = useCallback(async (prompt: string) => {
    setIsProcessing(true);
    setError(null);
    setResult(null);

    try {
      const taskResult = await mcLeukerAPI.createTask(prompt);
      if (taskResult.files) {
        taskResult.files = taskResult.files.map(file => ({
          ...file,
          download_url: mcLeukerAPI.getFileDownloadUrl(file.filename),
        }));
      }
      setResult(taskResult);
      return taskResult;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Task failed';
      setError(errorMessage);
      throw err;
    } finally {
      setIsProcessing(false);
    }
  }, []);

  return { isProcessing, result, error, submitTask };
}

export function useMcLeukerSearch() {
  const [isSearching, setIsSearching] = useState(false);
  const [results, setResults] = useState<AISearchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const search = useCallback(async (query: string, options?: { numResults?: number; summarize?: boolean }) => {
    setIsSearching(true);
    setError(null);

    try {
      const searchResults = await mcLeukerAPI.search(query, options);
      setResults(searchResults);
      return searchResults;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Search failed';
      setError(errorMessage);
      throw err;
    } finally {
      setIsSearching(false);
    }
  }, []);

  const quickAnswer = useCallback(async (question: string) => {
    setIsSearching(true);
    setError(null);

    try {
      return await mcLeukerAPI.quickAnswer(question);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Quick answer failed';
      setError(errorMessage);
      throw err;
    } finally {
      setIsSearching(false);
    }
  }, []);

  return { isSearching, results, error, search, quickAnswer };
}

export function useMcLeukerStatus() {
  const [isConnected, setIsConnected] = useState(false);
  const [configStatus, setConfigStatus] = useState<ConfigStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const config = await mcLeukerAPI.getConfigStatus();
        setConfigStatus(config);
        setIsConnected(true);
      } catch {
        setIsConnected(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  return { isConnected, configStatus, isLoading };
}

// ============================================================================
// COMPONENTS
// ============================================================================

export function McLeukerStatusIndicator() {
  const { isConnected, isLoading, configStatus } = useMcLeukerStatus();

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 text-sm text-gray-500">
        <div className="w-2 h-2 rounded-full bg-yellow-400 animate-pulse" />
        <span>Connecting...</span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2 text-sm">
      <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
      <span className={isConnected ? 'text-green-600' : 'text-red-600'}>
        {isConnected ? `AI Ready (${configStatus?.default_llm || 'OpenAI'})` : 'Disconnected'}
      </span>
    </div>
  );
}

export function McLeukerChatInterface({ className = '' }: { className?: string }) {
  const { messages, isLoading, error, sendMessage, clearMessages } = useMcLeukerChat();
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    const message = input;
    setInput('');
    await sendMessage(message);
  };

  return (
    <div className={`flex flex-col h-full bg-white rounded-lg shadow ${className}`}>
      <div className="flex items-center justify-between p-4 border-b">
        <h2 className="font-semibold">McLeuker AI</h2>
        <McLeukerStatusIndicator />
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 py-8">
            <p>Ask me anything or describe a task...</p>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] rounded-lg p-4 ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-100'}`}>
              <p className="whitespace-pre-wrap">{msg.content}</p>
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-2 pt-2 border-t border-gray-200 text-xs">
                  {msg.sources.slice(0, 3).map((s, i) => (
                    <a key={i} href={s.url} target="_blank" rel="noopener noreferrer" className="block text-blue-500 hover:underline truncate">
                      {s.title}
                    </a>
                  ))}
                </div>
              )}
              {msg.files && msg.files.length > 0 && (
                <div className="mt-2 pt-2 border-t border-gray-200">
                  {msg.files.map((f, i) => (
                    <a key={i} href={f.download_url || mcLeukerAPI.getFileDownloadUrl(f.filename)} className="block text-sm text-blue-500 hover:underline" download>
                      📄 {f.filename}
                    </a>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg p-4">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
              </div>
            </div>
          </div>
        )}

        {error && <div className="bg-red-50 text-red-600 p-3 rounded text-sm">{error}</div>}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="p-4 border-t">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}

export function McLeukerSearchInterface({ className = '' }: { className?: string }) {
  const { isSearching, results, error, search } = useMcLeukerSearch();
  const [query, setQuery] = useState('');

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isSearching) return;
    await search(query);
  };

  return (
    <div className={`bg-white rounded-lg shadow p-6 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-semibold">AI Search</h2>
        <McLeukerStatusIndicator />
      </div>

      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search with AI..."
            className="flex-1 px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isSearching}
          />
          <button
            type="submit"
            disabled={isSearching || !query.trim()}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {isSearching ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>

      {error && <div className="bg-red-50 text-red-600 p-4 rounded mb-4">{error}</div>}

      {results && (
        <div className="space-y-6">
          {results.summary && (
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="font-semibold text-blue-800 mb-2">AI Summary</h3>
              <p className="text-sm text-gray-700">{results.summary}</p>
            </div>
          )}

          {results.follow_up_questions && results.follow_up_questions.length > 0 && (
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold mb-2">Related Questions</h3>
              {results.follow_up_questions.map((q, i) => (
                <button
                  key={i}
                  onClick={() => { setQuery(q); search(q); }}
                  className="block text-sm text-blue-600 hover:underline mb-1"
                >
                  → {q}
                </button>
              ))}
            </div>
          )}

          <div>
            <h3 className="font-semibold mb-3">Results ({results.total_results})</h3>
            {results.results.map((r, i) => (
              <div key={i} className="border-b pb-4 mb-4">
                <a href={r.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline font-medium">
                  {r.title}
                </a>
                <p className="text-sm text-gray-600 mt-1">{r.snippet}</p>
                <p className="text-xs text-gray-400 mt-1">{r.url}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default { mcLeukerAPI, useMcLeukerChat, useMcLeukerTask, useMcLeukerSearch, useMcLeukerStatus, McLeukerStatusIndicator, McLeukerChatInterface, McLeukerSearchInterface };
