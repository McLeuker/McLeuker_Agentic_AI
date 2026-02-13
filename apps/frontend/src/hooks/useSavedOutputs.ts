'use client';

import { useState, useCallback, useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "@/contexts/AuthContext";

// Types for saved outputs
export type ContentType = 'text' | 'report' | 'analysis' | 'code' | 'image' | 'document';

export interface SavedOutput {
  id: string;
  user_id: string;
  conversation_id: string | null;
  message_id: string | null;
  title: string;
  content: string;
  content_type: ContentType;
  tags: string[];
  is_public: boolean;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface SaveOutputInput {
  conversation_id?: string;
  message_id?: string;
  title: string;
  content: string;
  content_type?: ContentType;
  tags?: string[];
  is_public?: boolean;
  metadata?: Record<string, unknown>;
}

export function useSavedOutputs() {
  const { user } = useAuth();
  const [savedOutputs, setSavedOutputs] = useState<SavedOutput[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load all saved outputs for the user
  const loadSavedOutputs = useCallback(async (contentType?: ContentType) => {
    if (!user) return;

    setLoading(true);
    setError(null);

    try {
      let query = supabase
        .from("saved_outputs")
        .select("*")
        .eq("user_id", user.id)
        .order("created_at", { ascending: false });

      if (contentType) {
        query = query.eq("content_type", contentType);
      }

      const { data, error: fetchError } = await query;

      if (fetchError) throw fetchError;

      setSavedOutputs((data || []) as SavedOutput[]);
    } catch (err) {
      console.error("Error loading saved outputs:", err);
      setError("Failed to load saved outputs");
    } finally {
      setLoading(false);
    }
  }, [user]);

  // Get a specific saved output by ID
  const getSavedOutput = useCallback(async (id: string): Promise<SavedOutput | null> => {
    if (!user) return null;

    try {
      const { data, error } = await supabase
        .from("saved_outputs")
        .select("*")
        .eq("id", id)
        .single();

      if (error) {
        if (error.code === 'PGRST116') return null; // Not found
        throw error;
      }

      return data as SavedOutput;
    } catch (err) {
      console.error("Error getting saved output:", err);
      return null;
    }
  }, [user]);

  // Save a new output
  const saveOutput = useCallback(async (input: SaveOutputInput): Promise<SavedOutput | null> => {
    if (!user) return null;

    try {
      const { data, error } = await supabase
        .from("saved_outputs")
        .insert({
          user_id: user.id,
          conversation_id: input.conversation_id || null,
          message_id: input.message_id || null,
          title: input.title,
          content: input.content,
          content_type: input.content_type || 'text',
          tags: input.tags || [],
          is_public: input.is_public || false,
          metadata: input.metadata || {},
        })
        .select()
        .single();

      if (error) throw error;

      const newOutput = data as SavedOutput;
      setSavedOutputs(prev => [newOutput, ...prev]);

      return newOutput;
    } catch (err) {
      console.error("Error saving output:", err);
      setError("Failed to save output");
      return null;
    }
  }, [user]);

  // Update a saved output
  const updateSavedOutput = useCallback(async (
    id: string, 
    updates: Partial<SaveOutputInput>
  ): Promise<SavedOutput | null> => {
    if (!user) return null;

    try {
      const { data, error } = await supabase
        .from("saved_outputs")
        .update({
          ...updates,
          updated_at: new Date().toISOString(),
        })
        .eq("id", id)
        .eq("user_id", user.id)
        .select()
        .single();

      if (error) throw error;

      const updatedOutput = data as SavedOutput;
      setSavedOutputs(prev => 
        prev.map(o => o.id === id ? updatedOutput : o)
      );

      return updatedOutput;
    } catch (err) {
      console.error("Error updating saved output:", err);
      setError("Failed to update saved output");
      return null;
    }
  }, [user]);

  // Delete a saved output
  const deleteSavedOutput = useCallback(async (id: string): Promise<boolean> => {
    if (!user) return false;

    try {
      const { error } = await supabase
        .from("saved_outputs")
        .delete()
        .eq("id", id)
        .eq("user_id", user.id);

      if (error) throw error;

      setSavedOutputs(prev => prev.filter(o => o.id !== id));
      return true;
    } catch (err) {
      console.error("Error deleting saved output:", err);
      setError("Failed to delete saved output");
      return false;
    }
  }, [user]);

  // Search saved outputs by tags
  const searchByTags = useCallback(async (tags: string[]): Promise<SavedOutput[]> => {
    if (!user || tags.length === 0) return [];

    try {
      const { data, error } = await supabase
        .from("saved_outputs")
        .select("*")
        .eq("user_id", user.id)
        .contains("tags", tags)
        .order("created_at", { ascending: false });

      if (error) throw error;

      return (data || []) as SavedOutput[];
    } catch (err) {
      console.error("Error searching saved outputs:", err);
      return [];
    }
  }, [user]);

  // Search saved outputs by title/content
  const searchByText = useCallback(async (searchText: string): Promise<SavedOutput[]> => {
    if (!user || !searchText.trim()) return [];

    try {
      const { data, error } = await supabase
        .from("saved_outputs")
        .select("*")
        .eq("user_id", user.id)
        .or(`title.ilike.%${searchText}%,content.ilike.%${searchText}%`)
        .order("created_at", { ascending: false });

      if (error) throw error;

      return (data || []) as SavedOutput[];
    } catch (err) {
      console.error("Error searching saved outputs:", err);
      return [];
    }
  }, [user]);

  // Get outputs for a specific conversation
  const getOutputsByConversation = useCallback(async (conversationId: string): Promise<SavedOutput[]> => {
    if (!user) return [];

    try {
      const { data, error } = await supabase
        .from("saved_outputs")
        .select("*")
        .eq("user_id", user.id)
        .eq("conversation_id", conversationId)
        .order("created_at", { ascending: false });

      if (error) throw error;

      return (data || []) as SavedOutput[];
    } catch (err) {
      console.error("Error getting outputs by conversation:", err);
      return [];
    }
  }, [user]);

  // Load saved outputs on mount
  useEffect(() => {
    if (user) {
      loadSavedOutputs();
    }
  }, [user, loadSavedOutputs]);

  return {
    savedOutputs,
    loading,
    error,
    loadSavedOutputs,
    getSavedOutput,
    saveOutput,
    updateSavedOutput,
    deleteSavedOutput,
    searchByTags,
    searchByText,
    getOutputsByConversation,
  };
}
