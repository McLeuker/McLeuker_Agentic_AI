'use client';

import { useState, useCallback, useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "@/contexts/AuthContext";

// Types for user memory
export type MemoryType = 'preference' | 'fact' | 'context' | 'style' | 'project';

export interface UserMemory {
  id: string;
  user_id: string;
  memory_type: MemoryType;
  key: string;
  value: string;
  confidence: number;
  source: string | null;
  expires_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface MemoryInput {
  memory_type: MemoryType;
  key: string;
  value: string;
  confidence?: number;
  source?: string;
  expires_at?: string;
}

export function useUserMemory() {
  const { user } = useAuth();
  const [memories, setMemories] = useState<UserMemory[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load all memories for the user
  const loadMemories = useCallback(async (memoryType?: MemoryType) => {
    if (!user) return;

    setLoading(true);
    setError(null);

    try {
      let query = supabase
        .from("user_memory")
        .select("*")
        .eq("user_id", user.id)
        .order("updated_at", { ascending: false });

      if (memoryType) {
        query = query.eq("memory_type", memoryType);
      }

      const { data, error: fetchError } = await query;

      if (fetchError) throw fetchError;

      setMemories((data || []) as UserMemory[]);
    } catch (err) {
      console.error("Error loading memories:", err);
      setError("Failed to load memories");
    } finally {
      setLoading(false);
    }
  }, [user]);

  // Get a specific memory by key
  const getMemory = useCallback(async (key: string, memoryType?: MemoryType): Promise<UserMemory | null> => {
    if (!user) return null;

    try {
      let query = supabase
        .from("user_memory")
        .select("*")
        .eq("user_id", user.id)
        .eq("key", key);

      if (memoryType) {
        query = query.eq("memory_type", memoryType);
      }

      const { data, error } = await query.single();

      if (error) {
        if (error.code === 'PGRST116') return null; // Not found
        throw error;
      }

      return data as UserMemory;
    } catch (err) {
      console.error("Error getting memory:", err);
      return null;
    }
  }, [user]);

  // Save or update a memory (upsert)
  const saveMemory = useCallback(async (input: MemoryInput): Promise<UserMemory | null> => {
    if (!user) return null;

    try {
      const { data, error } = await supabase
        .from("user_memory")
        .upsert({
          user_id: user.id,
          memory_type: input.memory_type,
          key: input.key,
          value: input.value,
          confidence: input.confidence || 1.0,
          source: input.source || null,
          expires_at: input.expires_at || null,
          updated_at: new Date().toISOString(),
        }, {
          onConflict: 'user_id,memory_type,key'
        })
        .select()
        .single();

      if (error) throw error;

      // Update local state
      setMemories(prev => {
        const existingIndex = prev.findIndex(
          m => m.user_id === user.id && m.memory_type === input.memory_type && m.key === input.key
        );
        if (existingIndex >= 0) {
          const updated = [...prev];
          updated[existingIndex] = data as UserMemory;
          return updated;
        }
        return [data as UserMemory, ...prev];
      });

      return data as UserMemory;
    } catch (err) {
      console.error("Error saving memory:", err);
      setError("Failed to save memory");
      return null;
    }
  }, [user]);

  // Save multiple memories at once
  const saveMemories = useCallback(async (inputs: MemoryInput[]): Promise<boolean> => {
    if (!user || inputs.length === 0) return false;

    try {
      const records = inputs.map(input => ({
        user_id: user.id,
        memory_type: input.memory_type,
        key: input.key,
        value: input.value,
        confidence: input.confidence || 1.0,
        source: input.source || null,
        expires_at: input.expires_at || null,
        updated_at: new Date().toISOString(),
      }));

      const { error } = await supabase
        .from("user_memory")
        .upsert(records, {
          onConflict: 'user_id,memory_type,key'
        });

      if (error) throw error;

      // Reload memories
      await loadMemories();
      return true;
    } catch (err) {
      console.error("Error saving memories:", err);
      setError("Failed to save memories");
      return false;
    }
  }, [user, loadMemories]);

  // Delete a memory
  const deleteMemory = useCallback(async (id: string): Promise<boolean> => {
    if (!user) return false;

    try {
      const { error } = await supabase
        .from("user_memory")
        .delete()
        .eq("id", id)
        .eq("user_id", user.id);

      if (error) throw error;

      setMemories(prev => prev.filter(m => m.id !== id));
      return true;
    } catch (err) {
      console.error("Error deleting memory:", err);
      setError("Failed to delete memory");
      return false;
    }
  }, [user]);

  // Delete all memories of a specific type
  const deleteMemoriesByType = useCallback(async (memoryType: MemoryType): Promise<boolean> => {
    if (!user) return false;

    try {
      const { error } = await supabase
        .from("user_memory")
        .delete()
        .eq("user_id", user.id)
        .eq("memory_type", memoryType);

      if (error) throw error;

      setMemories(prev => prev.filter(m => m.memory_type !== memoryType));
      return true;
    } catch (err) {
      console.error("Error deleting memories:", err);
      setError("Failed to delete memories");
      return false;
    }
  }, [user]);

  // Get memories formatted for AI context
  const getMemoriesForAI = useCallback((): string => {
    if (memories.length === 0) return "";

    const grouped: Record<MemoryType, UserMemory[]> = {
      preference: [],
      fact: [],
      context: [],
      style: [],
      project: [],
    };

    memories.forEach(m => {
      if (grouped[m.memory_type]) {
        grouped[m.memory_type].push(m);
      }
    });

    let context = "User Context:\n";

    if (grouped.preference.length > 0) {
      context += "\nPreferences:\n";
      grouped.preference.forEach(m => {
        context += `- ${m.key}: ${m.value}\n`;
      });
    }

    if (grouped.fact.length > 0) {
      context += "\nKnown Facts:\n";
      grouped.fact.forEach(m => {
        context += `- ${m.key}: ${m.value}\n`;
      });
    }

    if (grouped.context.length > 0) {
      context += "\nContext:\n";
      grouped.context.forEach(m => {
        context += `- ${m.key}: ${m.value}\n`;
      });
    }

    if (grouped.style.length > 0) {
      context += "\nCommunication Style:\n";
      grouped.style.forEach(m => {
        context += `- ${m.key}: ${m.value}\n`;
      });
    }

    if (grouped.project.length > 0) {
      context += "\nCurrent Projects:\n";
      grouped.project.forEach(m => {
        context += `- ${m.key}: ${m.value}\n`;
      });
    }

    return context;
  }, [memories]);

  // Load memories on mount
  useEffect(() => {
    if (user) {
      loadMemories();
    }
  }, [user, loadMemories]);

  return {
    memories,
    loading,
    error,
    loadMemories,
    getMemory,
    saveMemory,
    saveMemories,
    deleteMemory,
    deleteMemoriesByType,
    getMemoriesForAI,
  };
}
