'use client';

import { createContext, useContext, useState, useEffect, useCallback, useRef, ReactNode } from 'react';

// =============================================================================
// Types
// =============================================================================

export interface ReasoningLayer {
  id: string;
  layer_num: number;
  type: 'understanding' | 'planning' | 'research' | 'analysis' | 'synthesis' | 'writing';
  title: string;
  content: string;
  sub_steps: { step: string; result?: string; status?: string }[];
  status: 'active' | 'complete';
  expanded: boolean;
}

export interface Source {
  title: string;
  url: string;
  snippet?: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  reasoning_layers: ReasoningLayer[];
  sources: Source[];
  follow_up_questions: string[];
  timestamp: Date;
  isStreaming: boolean;
  is_favorite?: boolean;
}

export interface ActiveChat {
  conversationId: string | null;
  messages: Message[];
  isStreaming: boolean;
  pendingMessage: string | null;
  searchMode: 'quick' | 'deep';
  sector: string;
}

interface ChatContextType {
  activeChat: ActiveChat;
  setActiveChat: (chat: ActiveChat) => void;
  updateMessages: (messages: Message[]) => void;
  setIsStreaming: (streaming: boolean) => void;
  setPendingMessage: (message: string | null) => void;
  setSearchMode: (mode: 'quick' | 'deep') => void;
  setSector: (sector: string) => void;
  clearChat: () => void;
  abortController: AbortController | null;
  setAbortController: (controller: AbortController | null) => void;
}

// =============================================================================
// Context
// =============================================================================

const ChatContext = createContext<ChatContextType | undefined>(undefined);

const STORAGE_KEY = 'mcleuker-active-chat';

const defaultChat: ActiveChat = {
  conversationId: null,
  messages: [],
  isStreaming: false,
  pendingMessage: null,
  searchMode: 'quick',
  sector: 'all',
};

// =============================================================================
// Provider
// =============================================================================

export function ChatProvider({ children }: { children: ReactNode }) {
  const [activeChat, setActiveChatState] = useState<ActiveChat>(defaultChat);
  const [abortController, setAbortController] = useState<AbortController | null>(null);
  const isInitialized = useRef(false);

  // Load from localStorage on mount
  useEffect(() => {
    if (isInitialized.current) return;
    isInitialized.current = true;

    if (typeof window === 'undefined') return;

    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        // Restore messages with proper Date objects
        const messages = (parsed.messages || []).map((m: any) => ({
          ...m,
          timestamp: new Date(m.timestamp),
          isStreaming: false, // Reset streaming state on reload
        }));
        
        setActiveChatState({
          ...parsed,
          messages,
          isStreaming: false,
          pendingMessage: null,
        });
      }
    } catch (err) {
      console.error('Error loading chat state:', err);
    }
  }, []);

  // Save to localStorage when chat changes (debounced)
  useEffect(() => {
    if (typeof window === 'undefined') return;
    if (!isInitialized.current) return;

    const timeoutId = setTimeout(() => {
      try {
        // Don't save if streaming - wait for completion
        if (activeChat.isStreaming) return;
        
        localStorage.setItem(STORAGE_KEY, JSON.stringify({
          ...activeChat,
          // Don't persist streaming state
          isStreaming: false,
          pendingMessage: null,
        }));
      } catch (err) {
        console.error('Error saving chat state:', err);
      }
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [activeChat]);

  const setActiveChat = useCallback((chat: ActiveChat) => {
    setActiveChatState(chat);
  }, []);

  const updateMessages = useCallback((messages: Message[]) => {
    setActiveChatState(prev => ({
      ...prev,
      messages,
    }));
  }, []);

  const setIsStreaming = useCallback((streaming: boolean) => {
    setActiveChatState(prev => ({
      ...prev,
      isStreaming: streaming,
    }));
  }, []);

  const setPendingMessage = useCallback((message: string | null) => {
    setActiveChatState(prev => ({
      ...prev,
      pendingMessage: message,
    }));
  }, []);

  const setSearchMode = useCallback((mode: 'quick' | 'deep') => {
    setActiveChatState(prev => ({
      ...prev,
      searchMode: mode,
    }));
  }, []);

  const setSector = useCallback((sector: string) => {
    setActiveChatState(prev => ({
      ...prev,
      sector,
    }));
  }, []);

  const clearChat = useCallback(() => {
    // Abort any ongoing request
    if (abortController) {
      abortController.abort();
      setAbortController(null);
    }
    
    setActiveChatState(defaultChat);
    
    if (typeof window !== 'undefined') {
      localStorage.removeItem(STORAGE_KEY);
    }
  }, [abortController]);

  return (
    <ChatContext.Provider value={{
      activeChat,
      setActiveChat,
      updateMessages,
      setIsStreaming,
      setPendingMessage,
      setSearchMode,
      setSector,
      clearChat,
      abortController,
      setAbortController,
    }}>
      {children}
    </ChatContext.Provider>
  );
}

// =============================================================================
// Hook
// =============================================================================

export function useChat() {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
}
