'use client';

import { useState, useCallback, useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "@/contexts/AuthContext";

// Types
export interface Source {
  title: string;
  url: string;
  snippet?: string;
}

export interface ReasoningLayer {
  id: number;
  title: string;
  description: string;
  status: 'pending' | 'active' | 'complete';
  details?: string[];
}

export interface KeyInsight {
  title: string;
  description: string;
  importance: string;
  icon?: string;
}

export interface MessageMetadata {
  sources?: Source[];
  reasoning_layers?: ReasoningLayer[];
  follow_up_questions?: string[];
  search_mode?: 'auto' | 'instant' | 'agent';
}

export interface ChatMessage {
  id: string;
  conversation_id: string;
  user_id: string;
  role: "user" | "assistant";
  content: string;
  model_used: string | null;
  credits_used: number;
  is_favorite: boolean;
  created_at: string;
  // Metadata fields (parsed from JSON)
  sources?: Source[];
  reasoning_layers?: ReasoningLayer[];
  follow_up_questions?: string[];
  search_mode?: 'auto' | 'instant' | 'agent';
}

export interface Conversation {
  id: string;
  title: string;
  createdAt: Date;
  updatedAt: Date;
}

export function useConversations() {
  const { user } = useAuth();
  
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);

  // Load conversations
  const loadConversations = useCallback(async () => {
    if (!user) return;

    try {
      const { data, error } = await supabase
        .from("conversations")
        .select("*")
        .eq("user_id", user.id)
        .order("updated_at", { ascending: false });

      if (error) throw error;

      const formattedConversations: Conversation[] = (data || []).map((conv) => ({
        id: conv.id,
        title: conv.title || "New Chat",
        createdAt: new Date(conv.created_at),
        updatedAt: new Date(conv.updated_at),
      }));

      setConversations(formattedConversations);
    } catch (error) {
      console.error("Error loading conversations:", error);
    }
  }, [user]);

  // Load messages for a conversation - now includes metadata parsing
  const loadMessages = useCallback(async (conversationId: string) => {
    if (!user) return;

    try {
      const { data, error } = await supabase
        .from("chat_messages")
        .select("*")
        .eq("conversation_id", conversationId)
        .order("created_at", { ascending: true });

      if (error) throw error;

      const formattedMessages: ChatMessage[] = (data || []).map((msg) => {
        // Parse metadata if it exists
        let metadata: MessageMetadata = {};
        if (msg.metadata) {
          try {
            metadata = typeof msg.metadata === 'string' 
              ? JSON.parse(msg.metadata) 
              : msg.metadata as MessageMetadata;
          } catch (e) {
            console.error('Error parsing message metadata:', e);
          }
        }

        return {
          id: msg.id,
          conversation_id: msg.conversation_id,
          user_id: msg.user_id,
          role: msg.role as "user" | "assistant",
          content: msg.content,
          model_used: msg.model_used,
          credits_used: msg.credits_used || 0,
          is_favorite: msg.is_favorite,
          created_at: msg.created_at,
          // Include parsed metadata fields
          sources: metadata.sources,
          reasoning_layers: metadata.reasoning_layers,
          follow_up_questions: metadata.follow_up_questions,
          search_mode: metadata.search_mode,
        };
      });

      setMessages(formattedMessages);
    } catch (error) {
      console.error("Error loading messages:", error);
    }
  }, [user]);

  // Create a new conversation
  const createConversation = useCallback(async (title: string = "New Chat"): Promise<Conversation | null> => {
    if (!user) return null;

    try {
      // Generate a unique session_id for this conversation
      const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      
      const { data, error } = await supabase
        .from("conversations")
        .insert({
          user_id: user.id,
          title,
          session_id: sessionId,
        })
        .select()
        .single();

      if (error) throw error;

      const newConversation: Conversation = {
        id: data.id,
        title: data.title || "New Chat",
        createdAt: new Date(data.created_at),
        updatedAt: new Date(data.updated_at),
      };

      setConversations((prev) => [newConversation, ...prev]);
      setCurrentConversation(newConversation);
      setMessages([]);

      return newConversation;
    } catch (error) {
      console.error("Error creating conversation:", error);
      return null;
    }
  }, [user]);

  // Save a message with optional metadata
  const saveMessage = useCallback(async (
    conversationId: string,
    role: "user" | "assistant",
    content: string,
    modelUsed?: string,
    creditsUsed?: number,
    metadata?: MessageMetadata
  ): Promise<ChatMessage | null> => {
    if (!user) return null;

    try {
      // Convert metadata to JSON-compatible format
      const jsonMetadata = metadata ? JSON.parse(JSON.stringify(metadata)) : null;
      
      const { data, error } = await supabase
        .from("chat_messages")
        .insert({
          conversation_id: conversationId,
          user_id: user.id,
          role,
          content,
          model_used: modelUsed || null,
          credits_used: creditsUsed || 0,
          metadata: jsonMetadata,
        })
        .select()
        .single();

      if (error) throw error;

      // Parse metadata from response
      let parsedMetadata: MessageMetadata = {};
      if (data.metadata) {
        try {
          parsedMetadata = typeof data.metadata === 'string' 
            ? JSON.parse(data.metadata) 
            : data.metadata as MessageMetadata;
        } catch (e) {
          console.error('Error parsing saved message metadata:', e);
        }
      }

      const newMessage: ChatMessage = {
        id: data.id,
        conversation_id: data.conversation_id,
        user_id: data.user_id,
        role: data.role as "user" | "assistant",
        content: data.content,
        model_used: data.model_used,
        credits_used: data.credits_used || 0,
        is_favorite: data.is_favorite,
        created_at: data.created_at,
        sources: parsedMetadata.sources,
        reasoning_layers: parsedMetadata.reasoning_layers,
        follow_up_questions: parsedMetadata.follow_up_questions,
        search_mode: parsedMetadata.search_mode,
      };

      setMessages((prev) => [...prev, newMessage]);

      // Update conversation timestamp
      await supabase
        .from("conversations")
        .update({ updated_at: new Date().toISOString() })
        .eq("id", conversationId);

      return newMessage;
    } catch (error) {
      console.error("Error saving message:", error);
      return null;
    }
  }, [user]);

  // Update conversation title
  const updateConversationTitle = useCallback(async (conversationId: string, title: string) => {
    try {
      const { error } = await supabase
        .from("conversations")
        .update({ title })
        .eq("id", conversationId);

      if (error) throw error;

      setConversations((prev) =>
        prev.map((conv) =>
          conv.id === conversationId ? { ...conv, title } : conv
        )
      );

      if (currentConversation?.id === conversationId) {
        setCurrentConversation((prev) => prev ? { ...prev, title } : null);
      }
    } catch (error) {
      console.error("Error updating conversation title:", error);
    }
  }, [currentConversation]);

  // Delete a conversation
  const deleteConversation = useCallback(async (conversationId: string) => {
    try {
      // Delete messages first
      await supabase
        .from("chat_messages")
        .delete()
        .eq("conversation_id", conversationId);

      // Delete conversation
      const { error } = await supabase
        .from("conversations")
        .delete()
        .eq("id", conversationId);

      if (error) throw error;

      setConversations((prev) => prev.filter((conv) => conv.id !== conversationId));

      if (currentConversation?.id === conversationId) {
        setCurrentConversation(null);
        setMessages([]);
      }
    } catch (error) {
      console.error("Error deleting conversation:", error);
    }
  }, [currentConversation]);

  // Select a conversation
  const selectConversation = useCallback(async (conversation: Conversation) => {
    setCurrentConversation(conversation);
    await loadMessages(conversation.id);
  }, [loadMessages]);

  // Start a new chat
  const startNewChat = useCallback(() => {
    setCurrentConversation(null);
    setMessages([]);
  }, []);

  // Load conversations on mount
  useEffect(() => {
    if (user) {
      loadConversations();
    }
  }, [user, loadConversations]);

  return {
    conversations,
    currentConversation,
    messages,
    loading,
    setLoading,
    setMessages,
    loadConversations,
    loadMessages,
    createConversation,
    saveMessage,
    updateConversationTitle,
    deleteConversation,
    selectConversation,
    startNewChat,
    setCurrentConversation,
  };
}
