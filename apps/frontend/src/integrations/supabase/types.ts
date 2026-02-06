export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  public: {
    Tables: {
      chat_messages: {
        Row: {
          id: string
          conversation_id: string
          user_id: string
          role: string
          content: string
          model_used: string | null
          credits_used: number | null
          is_favorite: boolean
          metadata: Json | null
          attachments: Json | null
          created_at: string
        }
        Insert: {
          id?: string
          conversation_id: string
          user_id: string
          role: string
          content: string
          model_used?: string | null
          credits_used?: number | null
          is_favorite?: boolean
          metadata?: Json | null
          attachments?: Json | null
          created_at?: string
        }
        Update: {
          id?: string
          conversation_id?: string
          user_id?: string
          role?: string
          content?: string
          model_used?: string | null
          credits_used?: number | null
          is_favorite?: boolean
          metadata?: Json | null
          attachments?: Json | null
          created_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "chat_messages_conversation_id_fkey"
            columns: ["conversation_id"]
            isOneToOne: false
            referencedRelation: "conversations"
            referencedColumns: ["id"]
          },
        ]
      }
      conversations: {
        Row: {
          id: string
          user_id: string
          session_id: string
          title: string | null
          sector: string | null
          is_archived: boolean
          is_pinned: boolean
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          session_id: string
          title?: string | null
          sector?: string | null
          is_archived?: boolean
          is_pinned?: boolean
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          session_id?: string
          title?: string | null
          sector?: string | null
          is_archived?: boolean
          is_pinned?: boolean
          created_at?: string
          updated_at?: string
        }
        Relationships: []
      }
      profiles: {
        Row: {
          id: string
          user_id: string
          full_name: string | null
          email: string | null
          avatar_url: string | null
          bio: string | null
          website: string | null
          company: string | null
          job_title: string | null
          location: string | null
          timezone: string
          language: string
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          full_name?: string | null
          email?: string | null
          avatar_url?: string | null
          bio?: string | null
          website?: string | null
          company?: string | null
          job_title?: string | null
          location?: string | null
          timezone?: string
          language?: string
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          full_name?: string | null
          email?: string | null
          avatar_url?: string | null
          bio?: string | null
          website?: string | null
          company?: string | null
          job_title?: string | null
          location?: string | null
          timezone?: string
          language?: string
          created_at?: string
          updated_at?: string
        }
        Relationships: []
      }
      credit_transactions: {
        Row: {
          id: string
          user_id: string
          amount: number
          type: string
          description: string | null
          balance_after: number
          conversation_id: string | null
          message_id: string | null
          created_at: string
        }
        Insert: {
          id?: string
          user_id: string
          amount: number
          type: string
          description?: string | null
          balance_after: number
          conversation_id?: string | null
          message_id?: string | null
          created_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          amount?: number
          type?: string
          description?: string | null
          balance_after?: number
          conversation_id?: string | null
          message_id?: string | null
          created_at?: string
        }
        Relationships: []
      }
      support_requests: {
        Row: {
          id: string
          user_id: string
          type: string
          subject: string
          message: string
          status: string
          priority: string
          assigned_to: string | null
          resolution: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          type: string
          subject: string
          message: string
          status?: string
          priority?: string
          assigned_to?: string | null
          resolution?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          type?: string
          subject?: string
          message?: string
          status?: string
          priority?: string
          assigned_to?: string | null
          resolution?: string | null
          created_at?: string
          updated_at?: string
        }
        Relationships: []
      }
      users: {
        Row: {
          id: string
          name: string | null
          email: string
          avatar_url: string | null
          profile_image: string | null
          company: string | null
          role: string | null
          subscription_tier: string
          credits_balance: number
          created_at: string
          updated_at: string
          last_active_at: string | null
          metadata: Json | null
          auth_provider: string
          preferences: Json | null
          onboarding_completed: boolean
        }
        Insert: {
          id?: string
          name?: string | null
          email: string
          avatar_url?: string | null
          profile_image?: string | null
          company?: string | null
          role?: string | null
          subscription_tier?: string
          credits_balance?: number
          created_at?: string
          updated_at?: string
          last_active_at?: string | null
          metadata?: Json | null
          auth_provider?: string
          preferences?: Json | null
          onboarding_completed?: boolean
        }
        Update: {
          id?: string
          name?: string | null
          email?: string
          avatar_url?: string | null
          profile_image?: string | null
          company?: string | null
          role?: string | null
          subscription_tier?: string
          credits_balance?: number
          created_at?: string
          updated_at?: string
          last_active_at?: string | null
          metadata?: Json | null
          auth_provider?: string
          preferences?: Json | null
          onboarding_completed?: boolean
        }
        Relationships: []
      }
      subscriptions: {
        Row: {
          id: string
          user_id: string
          plan: string
          status: string
          credits_remaining: number
          credits_monthly: number
          stripe_customer_id: string | null
          stripe_subscription_id: string | null
          current_period_start: string | null
          current_period_end: string | null
          cancel_at_period_end: boolean
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          plan?: string
          status?: string
          credits_remaining?: number
          credits_monthly?: number
          stripe_customer_id?: string | null
          stripe_subscription_id?: string | null
          current_period_start?: string | null
          current_period_end?: string | null
          cancel_at_period_end?: boolean
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          plan?: string
          status?: string
          credits_remaining?: number
          credits_monthly?: number
          stripe_customer_id?: string | null
          stripe_subscription_id?: string | null
          current_period_start?: string | null
          current_period_end?: string | null
          cancel_at_period_end?: boolean
          created_at?: string
          updated_at?: string
        }
        Relationships: []
      }
      workspaces: {
        Row: {
          id: string
          name: string
          slug: string
          description: string | null
          owner_id: string
          logo_url: string | null
          settings: Json | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          name: string
          slug: string
          description?: string | null
          owner_id: string
          logo_url?: string | null
          settings?: Json | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          name?: string
          slug?: string
          description?: string | null
          owner_id?: string
          logo_url?: string | null
          settings?: Json | null
          created_at?: string
          updated_at?: string
        }
        Relationships: []
      }
      workspace_members: {
        Row: {
          id: string
          workspace_id: string
          user_id: string
          role: string
          invited_by: string | null
          joined_at: string
        }
        Insert: {
          id?: string
          workspace_id: string
          user_id: string
          role?: string
          invited_by?: string | null
          joined_at?: string
        }
        Update: {
          id?: string
          workspace_id?: string
          user_id?: string
          role?: string
          invited_by?: string | null
          joined_at?: string
        }
        Relationships: []
      }
      user_memory: {
        Row: {
          id: string
          user_id: string
          memory_type: string
          key: string
          value: string
          confidence: number
          source: string | null
          expires_at: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          memory_type: string
          key: string
          value: string
          confidence?: number
          source?: string | null
          expires_at?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          memory_type?: string
          key?: string
          value?: string
          confidence?: number
          source?: string | null
          expires_at?: string | null
          created_at?: string
          updated_at?: string
        }
        Relationships: []
      }
      saved_outputs: {
        Row: {
          id: string
          user_id: string
          conversation_id: string | null
          message_id: string | null
          title: string
          content: string
          content_type: string
          tags: string[] | null
          is_public: boolean
          metadata: Json | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          conversation_id?: string | null
          message_id?: string | null
          title: string
          content: string
          content_type?: string
          tags?: string[] | null
          is_public?: boolean
          metadata?: Json | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          conversation_id?: string | null
          message_id?: string | null
          title?: string
          content?: string
          content_type?: string
          tags?: string[] | null
          is_public?: boolean
          metadata?: Json | null
          created_at?: string
          updated_at?: string
        }
        Relationships: []
      }
      file_uploads: {
        Row: {
          id: string
          user_id: string
          conversation_id: string | null
          file_name: string
          file_type: string
          file_size: number
          storage_path: string
          public_url: string | null
          mime_type: string | null
          metadata: Json | null
          created_at: string
        }
        Insert: {
          id?: string
          user_id: string
          conversation_id?: string | null
          file_name: string
          file_type: string
          file_size: number
          storage_path: string
          public_url?: string | null
          mime_type?: string | null
          metadata?: Json | null
          created_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          conversation_id?: string | null
          file_name?: string
          file_type?: string
          file_size?: number
          storage_path?: string
          public_url?: string | null
          mime_type?: string | null
          metadata?: Json | null
          created_at?: string
        }
        Relationships: []
      }
      api_usage: {
        Row: {
          id: string
          user_id: string
          api_name: string
          endpoint: string | null
          tokens_used: number
          cost_cents: number
          request_metadata: Json | null
          created_at: string
        }
        Insert: {
          id?: string
          user_id: string
          api_name: string
          endpoint?: string | null
          tokens_used?: number
          cost_cents?: number
          request_metadata?: Json | null
          created_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          api_name?: string
          endpoint?: string | null
          tokens_used?: number
          cost_cents?: number
          request_metadata?: Json | null
          created_at?: string
        }
        Relationships: []
      }
      user_sessions: {
        Row: {
          id: string
          user_id: string
          session_token: string
          device_info: Json | null
          ip_address: string | null
          user_agent: string | null
          is_active: boolean
          last_activity_at: string
          expires_at: string
          created_at: string
        }
        Insert: {
          id?: string
          user_id: string
          session_token: string
          device_info?: Json | null
          ip_address?: string | null
          user_agent?: string | null
          is_active?: boolean
          last_activity_at?: string
          expires_at: string
          created_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          session_token?: string
          device_info?: Json | null
          ip_address?: string | null
          user_agent?: string | null
          is_active?: boolean
          last_activity_at?: string
          expires_at?: string
          created_at?: string
        }
        Relationships: []
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
  }
}
