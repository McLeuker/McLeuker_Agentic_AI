/**
 * McLeuker Agentic AI Platform - Lovable React Hooks
 * 
 * This file provides custom React hooks for integrating the McLeuker AI
 * backend with a Lovable frontend. Copy this file into your Lovable project's
 * `src/hooks/` directory.
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import {
  chat,
  processTask,
  search,
  quickAnswer,
  researchTopic,
  getTaskStatus,
  ChatRequest,
  ChatResponse,
  TaskRequest,
  TaskResponse,
  SearchRequest,
  SearchResponse,
  QuickAnswerRequest,
  QuickAnswerResponse,
  ResearchRequest,
  ResearchResponse,
  GeneratedFile,
} from '@/lib/api';

// --- Types ---

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  files?: GeneratedFile[];
  sources?: { title: string; url: string }[];
  timestamp: Date;
}

interface UseChatOptions {
  onError?: (error: Error) => void;
  onTaskComplete?: (task: TaskResponse) => void;
}

interface UseTaskOptions {
  pollInterval?: number;
  onProgress?: (status: string) => void;
  onComplete?: (task: TaskResponse) => void;
  onError?: (error: Error) => void;
}

interface UseSearchOptions {
  onError?: (error: Error) => void;
}

// --- Hooks ---

/**
 * Hook for managing chat interactions with the AI agent.
 */
export function useChat(options: UseChatOptions = {}) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const messageIdCounter = useRef(0);

  const generateMessageId = () => {
    messageIdCounter.current += 1;
    return `msg-${Date.now()}-${messageIdCounter.current}`;
  };

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;

    setIsLoading(true);
    setError(null);

    // Add user message immediately
    const userMessage: Message = {
      id: generateMessageId(),
      role: 'user',
      content,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const response = await chat({ message: content });

      // Add assistant response
      const assistantMessage: Message = {
        id: generateMessageId(),
        role: 'assistant',
        content: response.message,
        files: response.files,
        sources: response.sources,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);

      // Notify if a task was completed
      if (response.action_taken === 'task_execution' && response.task_id) {
        options.onTaskComplete?.({
          task_id: response.task_id,
          status: 'completed',
          files: response.files,
        } as TaskResponse);
      }

      return response;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('An error occurred');
      setError(error);
      options.onError?.(error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [options]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  const removeMessage = useCallback((messageId: string) => {
    setMessages((prev) => prev.filter((m) => m.id !== messageId));
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearMessages,
    removeMessage,
  };
}

/**
 * Hook for processing tasks with the AI agent.
 */
export function useTask(options: UseTaskOptions = {}) {
  const [task, setTask] = useState<TaskResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [progress, setProgress] = useState<string>('');

  const submitTask = useCallback(async (prompt: string, taskOptions?: Partial<TaskRequest>) => {
    setIsLoading(true);
    setError(null);
    setTask(null);
    setProgress('Starting task...');

    try {
      options.onProgress?.('Processing your request...');
      setProgress('Processing your request...');

      const response = await processTask({ prompt, ...taskOptions });
      setTask(response);
      setProgress('Task completed!');

      options.onComplete?.(response);
      return response;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('An error occurred');
      setError(error);
      setProgress('');
      options.onError?.(error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [options]);

  const reset = useCallback(() => {
    setTask(null);
    setError(null);
    setProgress('');
  }, []);

  return {
    task,
    isLoading,
    error,
    progress,
    submitTask,
    reset,
  };
}

/**
 * Hook for performing AI-powered searches.
 */
export function useSearch(options: UseSearchOptions = {}) {
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const performSearch = useCallback(async (query: string, searchOptions?: Partial<SearchRequest>) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await search({ query, ...searchOptions });
      setResults(response);
      return response;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('An error occurred');
      setError(error);
      options.onError?.(error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [options]);

  const clearResults = useCallback(() => {
    setResults(null);
    setError(null);
  }, []);

  return {
    results,
    isLoading,
    error,
    performSearch,
    clearResults,
  };
}

/**
 * Hook for getting quick answers to questions.
 */
export function useQuickAnswer() {
  const [answer, setAnswer] = useState<QuickAnswerResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const askQuestion = useCallback(async (question: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await quickAnswer({ question });
      setAnswer(response);
      return response;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('An error occurred');
      setError(error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearAnswer = useCallback(() => {
    setAnswer(null);
    setError(null);
  }, []);

  return {
    answer,
    isLoading,
    error,
    askQuestion,
    clearAnswer,
  };
}

/**
 * Hook for performing in-depth research on a topic.
 */
export function useResearch() {
  const [research, setResearch] = useState<ResearchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const startResearch = useCallback(async (topic: string, depth: 'light' | 'medium' | 'deep' = 'medium') => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await researchTopic({ topic, depth });
      setResearch(response);
      return response;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('An error occurred');
      setError(error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearResearch = useCallback(() => {
    setResearch(null);
    setError(null);
  }, []);

  return {
    research,
    isLoading,
    error,
    startResearch,
    clearResearch,
  };
}

/**
 * Hook for WebSocket connection for real-time updates.
 */
export function useWebSocket(userId: string) {
  const ws = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);

  useEffect(() => {
    const wsUrl = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000';
    ws.current = new WebSocket(`${wsUrl}/ws/${userId}`);

    ws.current.onopen = () => {
      setIsConnected(true);
    };

    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setLastMessage(data);
      } catch {
        // Ignore non-JSON messages (like pong)
      }
    };

    ws.current.onclose = () => {
      setIsConnected(false);
    };

    ws.current.onerror = () => {
      setIsConnected(false);
    };

    // Keep connection alive with ping
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
