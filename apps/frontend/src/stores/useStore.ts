import { create } from 'zustand';
import { Message, Conversation, V51Response } from '@/types';
import { sendChatMessage } from '@/lib/api';

interface ChatState {
  // State
  conversations: Conversation[];
  currentConversationId: string | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  createConversation: () => string;
  setCurrentConversation: (id: string) => void;
  sendMessage: (content: string) => Promise<void>;
  clearError: () => void;
  
  // Getters
  getCurrentConversation: () => Conversation | null;
  getCurrentMessages: () => Message[];
}

export const useChatStore = create<ChatState>((set, get) => ({
  // Initial state
  conversations: [],
  currentConversationId: null,
  isLoading: false,
  error: null,

  // Create a new conversation
  createConversation: () => {
    const newConversation: Conversation = {
      id: crypto.randomUUID(),
      title: 'New Chat',
      messages: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    set((state) => ({
      conversations: [newConversation, ...state.conversations],
      currentConversationId: newConversation.id,
    }));

    return newConversation.id;
  },

  // Set current conversation
  setCurrentConversation: (id: string) => {
    set({ currentConversationId: id });
  },

  // Send a message
  sendMessage: async (content: string) => {
    const state = get();
    let conversationId = state.currentConversationId;

    // Create a new conversation if none exists
    if (!conversationId) {
      conversationId = get().createConversation();
    }

    // Create user message
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    };

    // Add user message to conversation
    set((state) => ({
      conversations: state.conversations.map((conv) =>
        conv.id === conversationId
          ? {
              ...conv,
              messages: [...conv.messages, userMessage],
              updatedAt: new Date().toISOString(),
              title: conv.messages.length === 0 ? content.substring(0, 50) : conv.title,
            }
          : conv
      ),
      isLoading: true,
      error: null,
    }));

    try {
      // Send to backend
      const response = await sendChatMessage({
        message: content,
        session_id: conversationId,
      });

      if (response.success && response.data) {
        // Create assistant message
        const assistantMessage: Message = {
          id: response.data.message_id,
          role: 'assistant',
          content: response.data.main_content,
          timestamp: response.data.timestamp,
          response: response.data,
        };

        // Add assistant message to conversation
        set((state) => ({
          conversations: state.conversations.map((conv) =>
            conv.id === conversationId
              ? {
                  ...conv,
                  messages: [...conv.messages, assistantMessage],
                  updatedAt: new Date().toISOString(),
                }
              : conv
          ),
          isLoading: false,
        }));
      } else {
        set({
          isLoading: false,
          error: response.error || 'Failed to get response',
        });
      }
    } catch (error: any) {
      set({
        isLoading: false,
        error: error.message || 'An error occurred',
      });
    }
  },

  // Clear error
  clearError: () => {
    set({ error: null });
  },

  // Get current conversation
  getCurrentConversation: () => {
    const state = get();
    return state.conversations.find((c) => c.id === state.currentConversationId) || null;
  },

  // Get current messages
  getCurrentMessages: () => {
    const conversation = get().getCurrentConversation();
    return conversation?.messages || [];
  },
}));
