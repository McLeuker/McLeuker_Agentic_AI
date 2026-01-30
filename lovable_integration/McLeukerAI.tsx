/**
 * McLeuker Agentic AI Platform - Complete Lovable Integration
 * 
 * This file contains everything you need to integrate the McLeuker AI backend
 * with your Lovable frontend. Simply copy this file to your Lovable project.
 * 
 * Usage:
 * 1. Copy this file to your Lovable project's src/components folder
 * 2. Update the API_BASE_URL to your deployed backend URL
 * 3. Import and use the components in your pages
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';

// ============================================================================
// CONFIGURATION - UPDATE THIS URL TO YOUR DEPLOYED BACKEND
// ============================================================================

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://your-backend-url.railway.app';

// ============================================================================
// TYPES
// ============================================================================

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  files?: GeneratedFile[];
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
  summary?: string;
  follow_up_questions?: string[];
}

export interface ConfigStatus {
  status: string;
  services: {
    llm: Record<string, boolean>;
    search: Record<string, boolean>;
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

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
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

  // Health & Status
  async getHealth(): Promise<{ status: string; version: string; timestamp: string }> {
    return this.request('/health');
  }

  async getStatus(): Promise<any> {
    return this.request('/api/status');
  }

  async getConfigStatus(): Promise<ConfigStatus> {
    return this.request('/api/config/status');
  }

  // Task Processing
  async createTask(prompt: string, userId?: string): Promise<TaskResult> {
    return this.request('/api/tasks/sync', {
      method: 'POST',
      body: JSON.stringify({ prompt, user_id: userId }),
    });
  }

  async createTaskAsync(prompt: string, userId?: string): Promise<{ task_id: string; status: string }> {
    return this.request('/api/tasks', {
      method: 'POST',
      body: JSON.stringify({ prompt, user_id: userId }),
    });
  }

  async getTaskStatus(taskId: string): Promise<TaskResult> {
    return this.request(`/api/tasks/${taskId}`);
  }

  // Chat
  async chat(message: string, conversationId?: string): Promise<any> {
    return this.request('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ message, conversation_id: conversationId }),
    });
  }

  // Search
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

  // Interpret (for debugging)
  async interpret(prompt: string): Promise<{ interpretation: TaskInterpretation }> {
    return this.request('/api/interpret', {
      method: 'POST',
      body: JSON.stringify({ prompt }),
    });
  }

  // File download
  getFileDownloadUrl(filename: string): string {
    return `${this.baseUrl}/api/files/${filename}`;
  }
}

// Create singleton instance
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

    // Add user message
    const userMessage: Message = {
      id: `msg_${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);

    try {
      const response = await mcLeukerAPI.chat(content, conversationId);

      // Add assistant message
      const assistantMessage: Message = {
        id: `msg_${Date.now() + 1}`,
        role: 'assistant',
        content: response.message || response.response,
        timestamp: new Date(),
        files: response.files,
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
      const answer = await mcLeukerAPI.quickAnswer(question);
      return answer;
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
  const [status, setStatus] = useState<any>(null);
  const [configStatus, setConfigStatus] = useState<ConfigStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const [statusData, configData] = await Promise.all([
          mcLeukerAPI.getStatus(),
          mcLeukerAPI.getConfigStatus(),
        ]);
        setStatus(statusData);
        setConfigStatus(configData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch status');
      } finally {
        setIsLoading(false);
      }
    };

    fetchStatus();
  }, []);

  return { status, configStatus, isLoading, error };
}

// ============================================================================
// COMPONENTS
// ============================================================================

interface ChatInterfaceProps {
  className?: string;
  placeholder?: string;
  welcomeMessage?: string;
}

export function McLeukerChatInterface({
  className = '',
  placeholder = 'Ask me anything or describe a task...',
  welcomeMessage = 'Hello! I\'m McLeuker AI. I can help you with research, create reports, analyze data, and much more. What would you like me to do?',
}: ChatInterfaceProps) {
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
    <div className={`flex flex-col h-full ${className}`}>
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 py-8">
            <p className="text-lg">{welcomeMessage}</p>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-4 ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              <p className="whitespace-pre-wrap">{message.content}</p>
              
              {message.files && message.files.length > 0 && (
                <div className="mt-3 space-y-2">
                  <p className="text-sm font-medium">Generated Files:</p>
                  {message.files.map((file, idx) => (
                    <a
                      key={idx}
                      href={mcLeukerAPI.getFileDownloadUrl(file.filename)}
                      download
                      className="block text-sm underline hover:opacity-80"
                    >
                      📎 {file.filename}
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
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Error */}
      {error && (
        <div className="px-4 py-2 bg-red-100 text-red-700 text-sm">
          {error}
        </div>
      )}

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t">
        <div className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={placeholder}
            disabled={isLoading}
            className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}

interface SearchInterfaceProps {
  className?: string;
  placeholder?: string;
}

export function McLeukerSearchInterface({
  className = '',
  placeholder = 'Search for anything...',
}: SearchInterfaceProps) {
  const { isSearching, results, error, search } = useMcLeukerSearch();
  const [query, setQuery] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isSearching) return;
    await search(query);
  };

  return (
    <div className={`${className}`}>
      {/* Search Form */}
      <form onSubmit={handleSubmit} className="mb-6">
        <div className="flex space-x-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={placeholder}
            disabled={isSearching}
            className="flex-1 px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-lg"
          />
          <button
            type="submit"
            disabled={isSearching || !query.trim()}
            className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {isSearching ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>

      {/* Error */}
      {error && (
        <div className="mb-4 p-4 bg-red-100 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      {/* Results */}
      {results && (
        <div className="space-y-6">
          {/* Summary */}
          {results.summary && (
            <div className="p-4 bg-blue-50 rounded-lg">
              <h3 className="font-semibold text-blue-900 mb-2">AI Summary</h3>
              <p className="text-blue-800">{results.summary}</p>
            </div>
          )}

          {/* Search Results */}
          <div className="space-y-4">
            {results.results.map((result, idx) => (
              <div key={idx} className="p-4 border rounded-lg hover:shadow-md transition-shadow">
                <a
                  href={result.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-lg font-medium text-blue-600 hover:underline"
                >
                  {result.title}
                </a>
                <p className="text-sm text-green-700 mt-1">{result.url}</p>
                <p className="text-gray-600 mt-2">{result.snippet}</p>
              </div>
            ))}
          </div>

          {/* Follow-up Questions */}
          {results.follow_up_questions && results.follow_up_questions.length > 0 && (
            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="font-semibold text-gray-900 mb-2">Related Questions</h3>
              <div className="space-y-2">
                {results.follow_up_questions.map((question, idx) => (
                  <button
                    key={idx}
                    onClick={() => {
                      setQuery(question);
                      search(question);
                    }}
                    className="block text-left text-blue-600 hover:underline"
                  >
                    → {question}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

interface TaskSubmitterProps {
  className?: string;
  onComplete?: (result: TaskResult) => void;
}

export function McLeukerTaskSubmitter({
  className = '',
  onComplete,
}: TaskSubmitterProps) {
  const { isProcessing, result, error, submitTask } = useMcLeukerTask();
  const [prompt, setPrompt] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || isProcessing) return;

    const taskResult = await submitTask(prompt);
    if (onComplete) {
      onComplete(taskResult);
    }
  };

  return (
    <div className={`${className}`}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Describe your task in detail. For example: 'Create a market analysis report for the fashion industry with trends, competitors, and recommendations.'"
          rows={4}
          disabled={isProcessing}
          className="w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
        />
        <button
          type="submit"
          disabled={isProcessing || !prompt.trim()}
          className="w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {isProcessing ? 'Processing...' : 'Submit Task'}
        </button>
      </form>

      {/* Processing Status */}
      {isProcessing && (
        <div className="mt-4 p-4 bg-blue-50 rounded-lg">
          <div className="flex items-center space-x-3">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600" />
            <span className="text-blue-800">Processing your request...</span>
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="mt-4 p-4 bg-red-100 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      {/* Result */}
      {result && !isProcessing && (
        <div className="mt-4 p-4 bg-green-50 rounded-lg">
          <h3 className="font-semibold text-green-900 mb-2">Task Complete!</h3>
          
          {result.interpretation && (
            <div className="text-sm text-green-800 mb-3">
              <p>Intent: {result.interpretation.intent}</p>
              <p>Domain: {result.interpretation.domain}</p>
            </div>
          )}

          {result.files && result.files.length > 0 && (
            <div className="space-y-2">
              <p className="font-medium text-green-900">Generated Files:</p>
              {result.files.map((file, idx) => (
                <a
                  key={idx}
                  href={mcLeukerAPI.getFileDownloadUrl(file.filename)}
                  download
                  className="block p-2 bg-white rounded border hover:bg-gray-50"
                >
                  📎 {file.filename} ({file.format})
                </a>
              ))}
            </div>
          )}

          {result.message && (
            <p className="mt-3 text-green-800">{result.message}</p>
          )}
        </div>
      )}
    </div>
  );
}

// Status indicator component
export function McLeukerStatusIndicator() {
  const { status, configStatus, isLoading, error } = useMcLeukerStatus();

  if (isLoading) {
    return (
      <div className="flex items-center space-x-2 text-gray-500">
        <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse" />
        <span className="text-sm">Connecting...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center space-x-2 text-red-500">
        <div className="w-2 h-2 bg-red-500 rounded-full" />
        <span className="text-sm">Disconnected</span>
      </div>
    );
  }

  return (
    <div className="flex items-center space-x-2 text-green-500">
      <div className="w-2 h-2 bg-green-500 rounded-full" />
      <span className="text-sm">Connected</span>
    </div>
  );
}

// Export all components and utilities
export default {
  McLeukerChatInterface,
  McLeukerSearchInterface,
  McLeukerTaskSubmitter,
  McLeukerStatusIndicator,
  mcLeukerAPI,
  useMcLeukerChat,
  useMcLeukerTask,
  useMcLeukerSearch,
  useMcLeukerStatus,
};
