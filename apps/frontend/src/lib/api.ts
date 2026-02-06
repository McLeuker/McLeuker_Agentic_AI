import axios from 'axios';
import { V51Response, ChatRequest, ChatResponse } from '@/types';

// Backend API URL - Railway deployment
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://web-production-29f3c.up.railway.app';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000, // 120 second timeout for AI responses
});

// Parse V5.1 Response Contract
export function parseV51Response(data: any): V51Response | null {
  try {
    // Handle string responses (legacy)
    if (typeof data === 'string') {
      try {
        data = JSON.parse(data);
      } catch {
        // If it's plain text, wrap it in a V51-like structure
        return {
          session_id: crypto.randomUUID(),
          message_id: crypto.randomUUID(),
          timestamp: new Date().toISOString(),
          intent: 'general',
          domain: 'general',
          confidence: 1.0,
          summary: data.substring(0, 200),
          main_content: data,
          key_insights: [],
          sections: [],
          sources: [],
          follow_up_questions: [],
          action_items: [],
          credits_used: 1,
        };
      }
    }

    // Check if response is wrapped in a "response" object (V5.1 format)
    const responseData = data.response || data;

    // Check if it's a V5.1 response
    if (responseData.main_content || responseData.summary) {
      return {
        session_id: responseData.session_id || data.session_id || crypto.randomUUID(),
        message_id: responseData.message_id || crypto.randomUUID(),
        timestamp: responseData.timestamp || new Date().toISOString(),
        intent: responseData.intent || 'general',
        domain: responseData.domain || 'general',
        confidence: responseData.confidence || 1.0,
        summary: responseData.summary || '',
        main_content: responseData.main_content || responseData.content || '',
        key_insights: responseData.key_insights || [],
        sections: responseData.sections || [],
        sources: responseData.sources || [],
        follow_up_questions: responseData.follow_up_questions || [],
        action_items: responseData.action_items || [],
        credits_used: responseData.credits_used || data.credits_used || 1,
      };
    }

    // Fallback for unexpected formats
    return {
      session_id: crypto.randomUUID(),
      message_id: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
      intent: 'general',
      domain: 'general',
      confidence: 1.0,
      summary: 'Response received',
      main_content: JSON.stringify(data, null, 2),
      key_insights: [],
      sections: [],
      sources: [],
      follow_up_questions: [],
      action_items: [],
      credits_used: 1,
    };
  } catch (error) {
    console.error('Error parsing V5.1 response:', error);
    return null;
  }
}

// Send chat message to backend (legacy V5.1 endpoint)
export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  try {
    const response = await api.post('/api/chat', {
      message: request.message,
      session_id: request.session_id,
      user_id: request.user_id,
    });

    const parsedResponse = parseV51Response(response.data);
    
    if (parsedResponse) {
      return {
        success: true,
        data: parsedResponse,
      };
    }

    return {
      success: false,
      error: 'Failed to parse response',
    };
  } catch (error: any) {
    console.error('API Error:', error);
    return {
      success: false,
      error: error.response?.data?.detail || error.message || 'An error occurred',
    };
  }
}

// Health check (legacy)
export async function checkHealth(): Promise<boolean> {
  try {
    const response = await api.get('/health');
    return response.status === 200;
  } catch {
    return false;
  }
}

// =============================================================================
// Kimi 2.5 Complete API Client
// =============================================================================

export interface KimiChatMessage {
  role: 'system' | 'user' | 'assistant' | 'tool';
  content: string | any[];
}

export interface KimiChatOptions {
  mode?: 'instant' | 'thinking' | 'agent' | 'swarm' | 'research';
  stream?: boolean;
  enable_tools?: boolean;
}

export interface DownloadableFile {
  filename: string;
  download_url: string;
  file_id: string;
}

export interface SearchResult {
  type: 'search' | 'file';
  filename?: string;
  download_url?: string;
  file_id?: string;
  results?: any;
}

export const kimiApi = {
  // Main chat with tool execution
  async chat(messages: KimiChatMessage[], options: KimiChatOptions = {}) {
    const response = await api.post('/api/v1/chat', {
      messages,
      mode: options.mode || 'thinking',
      stream: options.stream || false,
      enable_tools: options.enable_tools !== false
    });
    return response.data;
  },

  // Streaming chat
  async *chatStream(messages: KimiChatMessage[], options: KimiChatOptions = {}) {
    const response = await fetch(`${API_BASE_URL}/api/v1/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        messages,
        mode: options.mode || 'thinking',
        enable_tools: options.enable_tools !== false
      })
    });

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) return;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            yield data;
          } catch (e) {
            // Ignore parse errors
          }
        }
      }
    }
  },

  // Agent swarm for complex tasks
  async swarm(masterTask: string, numAgents: number = 5, enableSearch: boolean = true) {
    const response = await api.post('/api/v1/swarm', {
      master_task: masterTask,
      context: {},
      num_agents: numAgents,
      enable_search: enableSearch
    });
    return response.data;
  },

  // Direct search across multiple sources
  async search(query: string, sources: string[] = ['web'], numResults: number = 10) {
    const response = await api.post('/api/v1/search', {
      query,
      sources,
      num_results: numResults
    });
    return response.data;
  },

  // Deep research with optional report generation
  async research(query: string, depth: 'quick' | 'deep' | 'exhaustive' = 'deep', generateReport: boolean = false) {
    const response = await api.post('/api/v1/research', {
      query,
      depth,
      generate_report: generateReport
    });
    return response.data;
  },

  // Generate downloadable file
  async generateFile(content: string | object, fileType: 'excel' | 'word' | 'pdf' | 'pptx', title?: string, filename?: string) {
    const response = await api.post('/api/v1/generate-file', {
      content: typeof content === 'string' ? content : JSON.stringify(content),
      file_type: fileType,
      title,
      filename
    });
    return response.data;
  },

  // Multimodal (text + image)
  async multimodal(text: string, imageFile?: File, mode: string = 'thinking') {
    const formData = new FormData();
    formData.append('text', text);
    formData.append('mode', mode);
    if (imageFile) formData.append('image', imageFile);

    const response = await fetch(`${API_BASE_URL}/api/v1/multimodal`, {
      method: 'POST',
      body: formData
    });
    return response.json();
  },

  // Download generated file
  downloadFile(fileId: string, filename: string) {
    const link = document.createElement('a');
    link.href = `${API_BASE_URL}/api/v1/download/${fileId}`;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  },

  // Health check
  async health() {
    const response = await api.get('/api/v1/health');
    return response.data;
  }
};

// Helper function to handle chat response with downloads
export function handleChatResponse(response: any) {
  if (!response.success) {
    return { error: response.error, answer: null, downloads: [], searchResults: [] };
  }

  const { answer, reasoning, downloads = [], search_results = [], metadata } = response.response;

  return {
    answer,
    reasoning,
    downloads,
    searchResults: search_results,
    metadata
  };
}

// Helper to create Excel data from array
export function createExcelData(items: any[], sheetName: string = 'Data') {
  return {
    [sheetName]: items
  };
}

export default api;
