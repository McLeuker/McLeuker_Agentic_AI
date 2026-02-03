/**
 * McLeuker AI - Shared Types
 * V5.1 Response Contract and common types used across frontend and backend
 */

// ============================================
// V5.1 Response Contract Types
// ============================================

export interface V51Response {
  session_id: string;
  message_id: string;
  timestamp: string;
  intent: string;
  domain: string;
  confidence: number;
  summary: string;
  main_content: string;
  key_insights: KeyInsight[];
  sections: Section[];
  sources: Source[];
  follow_up_questions: string[];
  action_items: ActionItem[];
  credits_used: number;
  tables?: Table[];
  files?: GeneratedFile[];
}

export interface KeyInsight {
  icon: string;
  title: string;
  description: string;
  importance: 'high' | 'medium' | 'low';
}

export interface Section {
  id: string;
  title: string;
  content: string;
}

export interface Source {
  id?: string;
  title: string;
  url: string;
  publisher?: string;
  snippet?: string;
  date?: string;
  type?: 'article' | 'video' | 'research' | 'social' | 'other';
}

export interface ActionItem {
  action: string;
  details: string;
  link?: string | null;
  priority: 'high' | 'medium' | 'low';
}

export interface Table {
  id: string;
  title: string;
  headers: string[];
  rows: string[][];
}

export interface GeneratedFile {
  id: string;
  name: string;
  type: 'excel' | 'pdf' | 'image' | 'csv';
  url: string;
  size?: number;
}

// ============================================
// Chat Types
// ============================================

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  response?: V51Response;
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: string;
  updatedAt: string;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  user_id?: string;
  mode?: 'auto' | 'quick' | 'deep';
}

export interface ChatResponse {
  success: boolean;
  data?: V51Response;
  error?: string;
}

// ============================================
// API Response Wrapper Types
// ============================================

export interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  reasoning_steps?: string[];
  credits_used?: number;
  session_id?: string;
  response?: T;
}

// ============================================
// User Types
// ============================================

export interface User {
  id: string;
  email: string;
  name?: string;
  avatar_url?: string;
  credits_balance: number;
  tier: 'free' | 'pro' | 'enterprise';
  created_at: string;
}

// ============================================
// Health Check Types
// ============================================

export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  version: string;
  timestamp: string;
  services: {
    grok: boolean;
    search: boolean;
    supabase: boolean;
  };
  features: {
    response_contract: boolean;
    file_generation: boolean;
    intent_routing: boolean;
  };
}

// ============================================
// Intent & Domain Types
// ============================================

export type Intent = 
  | 'shopping'
  | 'research'
  | 'comparison'
  | 'recommendation'
  | 'analysis'
  | 'general';

export type Domain = 
  | 'fashion'
  | 'beauty'
  | 'skincare'
  | 'sustainability'
  | 'lifestyle'
  | 'tech'
  | 'general';

// ============================================
// Utility Types
// ============================================

export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};
