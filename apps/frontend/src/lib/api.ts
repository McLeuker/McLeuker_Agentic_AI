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

// Send chat message to backend
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

// Health check
export async function checkHealth(): Promise<boolean> {
  try {
    const response = await api.get('/health');
    return response.status === 200;
  } catch {
    return false;
  }
}

// =============================================================================
// Kimi 2.5 API Client (New Endpoints)
// =============================================================================

export interface KimiChatMessage {
  role: 'system' | 'user' | 'assistant' | 'tool';
  content: string | any[];
}

export interface KimiChatOptions {
  mode?: 'instant' | 'thinking' | 'agent' | 'swarm' | 'vision_code';
  stream?: boolean;
}

export const kimiApi = {
  async chat(messages: KimiChatMessage[], options: KimiChatOptions = {}) {
    const response = await api.post('/api/v1/chat', {
      messages,
      mode: options.mode || 'thinking',
      stream: options.stream || false
    });
    return response.data;
  },

  async swarm(masterTask: string, numAgents: number = 5) {
    const response = await api.post('/api/v1/swarm', {
      master_task: masterTask,
      context: {},
      num_agents: numAgents,
      auto_synthesize: true
    });
    return response.data;
  },

  async visionToCode(imageBase64: string, requirements: string = '', framework: 'html' | 'react' | 'vue' = 'html') {
    const response = await api.post('/api/v1/vision-to-code', {
      image_base64: imageBase64,
      requirements,
      framework
    });
    return response.data;
  },

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

  async health() {
    const response = await api.get('/api/v1/health');
    return response.data;
  }
};

export default api;
