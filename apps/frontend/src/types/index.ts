/**
 * McLeuker AI Frontend Types
 * Re-exports from shared-types package for convenience
 */

// Re-export all shared types
export * from '@mcleuker/shared-types';

// Frontend-specific types can be added here
export interface ChatState {
  conversations: import('@mcleuker/shared-types').Conversation[];
  currentConversationId: string | null;
  isLoading: boolean;
  error: string | null;
}
