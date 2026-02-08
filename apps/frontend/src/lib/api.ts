/**
 * McLeuker AI V5.2 - Frontend API Service
 * Handles all API communication with standardized event parsing
 * Includes persistent file download and background search support
 */

import { ChatMode } from '@/components/chat/ModeSelector';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ============================================================================
// TYPES
// ============================================================================

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system' | 'tool';
  content: string;
}

export interface ChatRequest {
  messages: ChatMessage[];
  mode: ChatMode;
  stream?: boolean;
  conversation_id?: string;
  user_id?: string;
}

export interface StreamEvent {
  type: string;
  data: any;
  timestamp: string;
}

export interface SourceInfo {
  title: string;
  url: string;
  snippet?: string;
  source: string;
}

export interface DownloadInfo {
  file_id: string;
  filename: string;
  file_type: string;
  download_url: string;
}

export interface TaskProgress {
  step: string;
  title: string;
  status: 'pending' | 'active' | 'complete' | 'error';
  detail?: string;
  progress?: number;
}

// ============================================================================
// EVENT HANDLERS
// ============================================================================

export interface ChatEventHandlers {
  onTaskProgress?: (progress: TaskProgress) => void;
  onReasoning?: (chunk: string) => void;
  onContent?: (chunk: string) => void;
  onToolCall?: (tool: string, status: string, output?: any) => void;
  onSearchSources?: (sources: SourceInfo[]) => void;
  onDownload?: (download: DownloadInfo) => void;
  onFollowUp?: (questions: string[]) => void;
  onComplete?: (data: {
    content: string;
    conversation_id?: string;
    downloads: DownloadInfo[];
    sources: SourceInfo[];
    follow_up_questions: string[];
  }) => void;
  onError?: (message: string) => void;
  onConversationCreated?: (id: string, mode: string) => void;
}

// ============================================================================
// API SERVICE
// ============================================================================

export class APIService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Stream chat with event handlers
   */
  async streamChat(
    request: ChatRequest,
    handlers: ChatEventHandlers
  ): Promise<void> {
    const response = await fetch(`${this.baseUrl}/api/v1/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream'
      },
      body: JSON.stringify(request)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    if (!response.body) {
      throw new Error('No response body');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const event: StreamEvent = JSON.parse(line.slice(6));
              this.handleEvent(event, handlers);
            } catch (e) {
              console.error('Failed to parse event:', line, e);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  /**
   * Non-streaming chat
   */
  async chat(request: ChatRequest): Promise<{
    content: string;
    downloads: DownloadInfo[];
    sources: SourceInfo[];
    follow_up_questions: string[];
  }> {
    const response = await fetch(`${this.baseUrl}/api/v1/chat/non-stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(request)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Search
   */
  async search(query: string, sources: string[] = ['web', 'news']): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/v1/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ query, sources })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Generate file
   */
  async generateFile(
    prompt: string,
    fileType: 'excel' | 'word' | 'pdf' | 'pptx',
    userId?: string,
    conversationId?: string
  ): Promise<{
    success: boolean;
    file_id?: string;
    filename?: string;
    download_url?: string;
    error?: string;
  }> {
    const response = await fetch(`${this.baseUrl}/api/v1/files/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        prompt,
        file_type: fileType,
        user_id: userId,
        conversation_id: conversationId
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Download file
   */
  downloadFile(fileId: string): string {
    return `${this.baseUrl}/api/v1/files/${fileId}/download`;
  }

  /**
   * Get conversations
   */
  async getConversations(userId: string): Promise<any[]> {
    const response = await fetch(`${this.baseUrl}/api/v1/conversations?user_id=${userId}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data.conversations || [];
  }

  /**
   * Create conversation
   */
  async createConversation(
    userId: string,
    title?: string,
    mode: ChatMode = 'thinking'
  ): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/v1/conversations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ user_id: userId, title, mode })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Get conversation with messages
   */
  async getConversation(conversationId: string, userId: string): Promise<{
    conversation: any;
    messages: any[];
  }> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/conversations/${conversationId}?user_id=${userId}`
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Delete conversation
   */
  async deleteConversation(conversationId: string, userId: string): Promise<void> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/conversations/${conversationId}?user_id=${userId}`,
      { method: 'DELETE' }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
  }

  /**
   * List generated files (persistent - survives server restarts)
   */
  async listGeneratedFiles(userId?: string, conversationId?: string): Promise<{
    success: boolean;
    files: Array<{
      file_id: string;
      filename: string;
      file_type: string;
      download_url: string;
      public_url: string;
      size_bytes: number;
      created_at: string;
      conversation_id?: string;
    }>;
    count: number;
  }> {
    const params = new URLSearchParams();
    if (userId) params.set('user_id', userId);
    if (conversationId) params.set('conversation_id', conversationId);
    
    const response = await fetch(`${this.baseUrl}/api/v1/files/generated?${params}`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return response.json();
  }

  /**
   * Get file download URL (works even after server restart)
   */
  getFileDownloadUrl(fileId: string): string {
    return `${this.baseUrl}/api/v1/download/${fileId}`;
  }

  /**
   * Start background search (survives page refresh)
   */
  async startBackgroundSearch(query: string, userId?: string): Promise<{
    task_id: string;
    status: string;
  }> {
    const response = await fetch(`${this.baseUrl}/api/v1/search/background`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, user_id: userId })
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return response.json();
  }

  /**
   * Check background search status
   */
  async getBackgroundSearchStatus(taskId: string): Promise<{
    task_id: string;
    status: string;
    progress: number;
    result?: any;
    error?: string;
  }> {
    const response = await fetch(`${this.baseUrl}/api/v1/search/background/${taskId}`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return response.json();
  }

  /**
   * Streaming chat generator - yields SSE events
   */
  async *chatStream(
    messages: Array<{ role: string; content: string }>,
    options: { mode?: ChatMode; enable_tools?: boolean } = {}
  ): AsyncGenerator<{ type: string; data: any }> {
    const response = await fetch(`${this.baseUrl}/api/v1/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream'
      },
      body: JSON.stringify({
        messages,
        mode: options.mode || 'research',
        stream: true,
        enable_tools: options.enable_tools ?? true
      })
    });

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    if (!response.body) throw new Error('No response body');

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const event = JSON.parse(line.slice(6));
              yield event;
            } catch (e) {
              console.error('Failed to parse SSE event:', e);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  /**
   * Swarm endpoint - multi-agent execution
   */
  async swarm(
    masterTask: string,
    numAgents: number = 5,
    autoSynthesize: boolean = true,
    generateFile: boolean = false,
    fileType?: string
  ): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/v1/swarm`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        master_task: masterTask,
        context: {},
        num_agents: numAgents,
        auto_synthesize: autoSynthesize,
        generate_file: generateFile,
        file_type: fileType
      })
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return response.json();
  }

  /**
   * Research endpoint - deep research with file generation
   */
  async research(
    query: string,
    depth: string = 'deep',
    generateFile: boolean = false
  ): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/v1/research`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query,
        depth,
        generate_file: generateFile
      })
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return response.json();
  }

  /**
   * Multimodal endpoint - image/video analysis
   */
  async multimodal(
    text: string,
    file?: File,
    mode: string = 'research'
  ): Promise<any> {
    const formData = new FormData();
    formData.append('text', text);
    formData.append('mode', mode);
    if (file) formData.append('image', file);

    const response = await fetch(`${this.baseUrl}/api/v1/multimodal`, {
      method: 'POST',
      body: formData
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return response.json();
  }

  /**
   * Vision-to-code endpoint
   */
  async visionToCode(
    imageBase64: string,
    requirements: string = '',
    framework: 'html' | 'react' | 'vue' = 'react'
  ): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/v1/vision-to-code`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        image_base64: imageBase64,
        requirements,
        framework
      })
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return response.json();
  }

  /**
   * Upload file for analysis
   */
  async uploadFile(file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseUrl}/api/v1/upload`, {
      method: 'POST',
      body: formData
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return response.json();
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{
    status: string;
    version: string;
    services: Record<string, boolean>;
  }> {
    const response = await fetch(`${this.baseUrl}/health`);
    return response.json();
  }

  // ============================================================================
  // PRIVATE METHODS
  // ============================================================================

  private handleEvent(event: StreamEvent, handlers: ChatEventHandlers): void {
    const { type, data } = event;

    switch (type) {
      case 'task_progress':
        handlers.onTaskProgress?.(data as TaskProgress);
        break;

      case 'reasoning':
        handlers.onReasoning?.(data.chunk);
        break;

      case 'content':
        handlers.onContent?.(data.chunk);
        break;

      case 'tool_call':
        handlers.onToolCall?.(data.tool, data.status, data.output);
        break;

      case 'search_sources':
        handlers.onSearchSources?.(data.sources as SourceInfo[]);
        break;

      case 'download':
        handlers.onDownload?.(data as DownloadInfo);
        break;

      case 'follow_up':
        handlers.onFollowUp?.(data.questions);
        break;

      case 'complete':
        handlers.onComplete?.({
          content: data.content,
          conversation_id: data.conversation_id,
          downloads: data.downloads || [],
          sources: data.sources || [],
          follow_up_questions: data.follow_up_questions || []
        });
        break;

      case 'error':
        handlers.onError?.(data.message);
        break;

      case 'conversation_created':
        handlers.onConversationCreated?.(data.id, data.mode);
        break;

      default:
        console.log('Unknown event type:', type, data);
    }
  }
}

// ============================================================================
// HOOK
// ============================================================================

import { useState, useCallback } from 'react';

export interface UseChatOptions {
  userId?: string;
  conversationId?: string;
  mode?: ChatMode;
}

export interface UseChatReturn {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  currentContent: string;
  downloads: DownloadInfo[];
  sources: SourceInfo[];
  followUpQuestions: string[];
  taskProgress: TaskProgress | null;
  sendMessage: (content: string) => Promise<void>;
  clearMessages: () => void;
}

export function useChat(options: UseChatOptions = {}): UseChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentContent, setCurrentContent] = useState('');
  const [downloads, setDownloads] = useState<DownloadInfo[]>([]);
  const [sources, setSources] = useState<SourceInfo[]>([]);
  const [followUpQuestions, setFollowUpQuestions] = useState<string[]>([]);
  const [taskProgress, setTaskProgress] = useState<TaskProgress | null>(null);

  const api = new APIService();

  const sendMessage = useCallback(async (content: string) => {
    setIsLoading(true);
    setError(null);
    setCurrentContent('');
    setDownloads([]);
    setSources([]);
    setFollowUpQuestions([]);

    // Add user message
    const userMessage: ChatMessage = { role: 'user', content };
    setMessages(prev => [...prev, userMessage]);

    try {
      await api.streamChat(
        {
          messages: [...messages, userMessage],
          mode: options.mode || 'thinking',
          stream: true,
          conversation_id: options.conversationId,
          user_id: options.userId
        },
        {
          onTaskProgress: setTaskProgress,
          onContent: (chunk) => {
            setCurrentContent(prev => prev + chunk);
          },
          onSearchSources: setSources,
          onDownload: (download) => {
            setDownloads(prev => [...prev, download]);
          },
          onFollowUp: setFollowUpQuestions,
          onComplete: (data) => {
            setMessages(prev => [...prev, { role: 'assistant', content: data.content }]);
            setCurrentContent('');
            setDownloads(data.downloads);
            setSources(data.sources);
            setFollowUpQuestions(data.follow_up_questions);
          },
          onError: (message) => {
            setError(message);
          },
          onConversationCreated: (id) => {
            // Handle conversation creation if needed
            console.log('Conversation created:', id);
          }
        }
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsLoading(false);
      setTaskProgress(null);
    }
  }, [messages, options.mode, options.conversationId, options.userId]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setCurrentContent('');
    setDownloads([]);
    setSources([]);
    setFollowUpQuestions([]);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    currentContent,
    downloads,
    sources,
    followUpQuestions,
    taskProgress,
    sendMessage,
    clearMessages
  };
}

// Export singleton instance
export const api = new APIService();
export default api;

// Re-export ChatMode for backward compatibility
export type { ChatMode } from '@/components/chat/ModeSelector';

// Legacy type aliases for backward compatibility
export type DownloadableFile = DownloadInfo;
export type SearchSource = SourceInfo;

// Legacy function aliases
export const handleChatResponse = () => {};
export const sendChatMessage = async (request: any) => {
  const apiInstance = new APIService();
  return apiInstance.chat(request);
};
export const detectFileRequest = (msg: string): { type: string | null } => {
  const lower = msg.toLowerCase();
  if (lower.includes('excel') || lower.includes('spreadsheet')) return { type: 'excel' };
  if (lower.includes('word') || lower.includes('document') || lower.includes('docx')) return { type: 'word' };
  if (lower.includes('pdf') || lower.includes('report')) return { type: 'pdf' };
  if (lower.includes('ppt') || lower.includes('presentation') || lower.includes('slide')) return { type: 'pptx' };
  return { type: null };
};
export const formatTokenCount = (count: number): string => {
  if (count >= 1000000) return `${(count / 1000000).toFixed(1)}M`;
  if (count >= 1000) return `${(count / 1000).toFixed(1)}K`;
  return count.toString();
};
export const formatLatency = (ms: number): string => {
  if (ms >= 1000) return `${(ms / 1000).toFixed(1)}s`;
  return `${ms}ms`;
};
