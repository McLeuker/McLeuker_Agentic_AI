/**
 * McLeuker AI - Complete API Client
 * All Kimi 2.5 capabilities with TypeScript support
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://web-production-29f3c.up.railway.app';

// Types
export interface ChatMessage {
  role: 'system' | 'user' | 'assistant' | 'tool';
  content: string | any[];
  tool_calls?: any[];
  tool_call_id?: string;
}

export type ChatMode = 'instant' | 'thinking' | 'agent' | 'swarm' | 'research' | 'code';

export interface ChatOptions {
  mode?: ChatMode;
  stream?: boolean;
  enable_tools?: boolean;
  context_id?: string;
}

export interface DownloadableFile {
  filename: string;
  download_url: string;
  file_id: string;
  file_type: string;
}

export interface SearchSource {
  type: 'search' | 'file';
  filename?: string;
  download_url?: string;
  file_id?: string;
  sources?: string[];
}

export interface ChatResponse {
  success: boolean;
  response?: {
    answer: string;
    reasoning?: string;
    mode: ChatMode;
    downloads: DownloadableFile[];
    search_sources: SearchSource[];
    metadata: {
      tokens: {
        prompt_tokens: number;
        completion_tokens: number;
        total_tokens: number;
      };
      latency_ms: number;
      tool_calls: number;
    };
  };
  error?: string;
}

// Main API client
export const api = {
  // ==================== CHAT ====================
  
  async chat(messages: ChatMessage[], options: ChatOptions = {}): Promise<ChatResponse> {
    const response = await fetch(`${API_URL}/api/v1/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        messages,
        mode: options.mode || 'thinking',
        stream: options.stream || false,
        enable_tools: options.enable_tools !== false,
        context_id: options.context_id
      })
    });
    return response.json();
  },

  async *chatStream(messages: ChatMessage[], options: ChatOptions = {}) {
    const response = await fetch(`${API_URL}/api/v1/chat/stream`, {
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

  // ==================== AGENT SWARM ====================
  
  async swarm(
    masterTask: string, 
    numAgents: number = 5, 
    enableSearch: boolean = true,
    generateDeliverable: boolean = false,
    deliverableType?: 'report' | 'presentation' | 'spreadsheet'
  ) {
    const response = await fetch(`${API_URL}/api/v1/swarm`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        master_task: masterTask,
        context: {},
        num_agents: numAgents,
        enable_search: enableSearch,
        generate_deliverable: generateDeliverable,
        deliverable_type: deliverableType
      })
    });
    return response.json();
  },

  // ==================== SEARCH ====================
  
  async search(
    query: string, 
    sources: string[] = ['web', 'news'], 
    numResults: number = 10,
    recencyDays?: number
  ) {
    const response = await fetch(`${API_URL}/api/v1/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query,
        sources,
        num_results: numResults,
        recency_days: recencyDays
      })
    });
    return response.json();
  },

  // ==================== RESEARCH ====================
  
  async research(
    query: string, 
    depth: 'quick' | 'deep' | 'exhaustive' = 'deep',
    generateDeliverable: boolean = false,
    deliverableType: 'report' | 'presentation' | 'spreadsheet' = 'report'
  ) {
    const response = await fetch(`${API_URL}/api/v1/research`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query,
        depth,
        generate_deliverable: generateDeliverable,
        deliverable_type: deliverableType
      })
    });
    return response.json();
  },

  // ==================== VISION TO CODE ====================
  
  async visionToCode(
    imageBase64: string, 
    requirements: string = '', 
    framework: 'html' | 'react' | 'vue' | 'svelte' | 'angular' = 'html',
    stylingPreference: 'tailwind' | 'bootstrap' | 'css' | 'styled-components' = 'tailwind'
  ) {
    const response = await fetch(`${API_URL}/api/v1/vision-to-code`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        image_base64: imageBase64,
        requirements,
        framework,
        styling_preference: stylingPreference
      })
    });
    return response.json();
  },

  // ==================== CODE EXECUTION ====================
  
  async executeCode(
    code: string,
    language: 'python' | 'javascript' | 'typescript' | 'bash' | 'sql' = 'python',
    timeout: number = 30,
    dependencies?: string[],
    inputs?: Record<string, any>
  ) {
    const response = await fetch(`${API_URL}/api/v1/execute-code`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        code,
        language,
        timeout,
        dependencies,
        inputs
      })
    });
    return response.json();
  },

  // ==================== FILE GENERATION ====================
  
  async generateFile(
    content: string | object,
    fileType: 'excel' | 'word' | 'pdf' | 'pptx' | 'csv' | 'json',
    options: {
      title?: string;
      subtitle?: string;
      filename?: string;
      includeCharts?: boolean;
    } = {}
  ) {
    const response = await fetch(`${API_URL}/api/v1/generate-file`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        content: typeof content === 'string' ? content : JSON.stringify(content),
        file_type: fileType,
        title: options.title,
        subtitle: options.subtitle,
        filename: options.filename,
        include_charts: options.includeCharts
      })
    });
    return response.json();
  },

  async generateExcel(
    data: Record<string, any[]> | any[],
    options: {
      title?: string;
      filename?: string;
      includeCharts?: boolean;
    } = {}
  ) {
    return this.generateFile(data, 'excel', options);
  },

  async generateWord(
    content: string,
    options: {
      title?: string;
      subtitle?: string;
      filename?: string;
    } = {}
  ) {
    return this.generateFile(content, 'word', options);
  },

  async generatePDF(
    content: string,
    options: {
      title?: string;
      filename?: string;
      includeToc?: boolean;
    } = {}
  ) {
    return this.generateFile(content, 'pdf', {
      ...options,
      includeCharts: options.includeToc
    });
  },

  async generatePresentation(
    content: string,
    options: {
      title?: string;
      filename?: string;
      theme?: 'professional' | 'modern' | 'dark';
    } = {}
  ) {
    return this.generateFile(content, 'pptx', options);
  },

  // ==================== MULTIMODAL ====================
  
  async multimodal(text: string, imageFile?: File, mode: ChatMode = 'thinking') {
    const formData = new FormData();
    formData.append('text', text);
    formData.append('mode', mode);
    if (imageFile) formData.append('image', imageFile);

    const response = await fetch(`${API_URL}/api/v1/multimodal`, {
      method: 'POST',
      body: formData
    });
    return response.json();
  },

  // ==================== DOWNLOAD ====================
  
  downloadFile(fileId: string, filename: string) {
    const link = document.createElement('a');
    link.href = `${API_URL}/api/v1/download/${fileId}`;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  },

  getDownloadUrl(fileId: string) {
    return `${API_URL}/api/v1/download/${fileId}`;
  },

  // ==================== HEALTH & STATUS ====================
  
  async health() {
    const response = await fetch(`${API_URL}/api/v1/health`);
    return response.json();
  }
};

// ==================== HELPERS ====================

export function handleChatResponse(response: ChatResponse) {
  if (!response.success) {
    return {
      error: response.error,
      answer: null,
      reasoning: null,
      downloads: [] as DownloadableFile[],
      searchSources: [] as SearchSource[],
      metadata: null
    };
  }

  const { answer, reasoning, downloads = [], search_sources = [], metadata } = response.response!;

  return {
    answer,
    reasoning,
    downloads,
    searchSources: search_sources,
    metadata
  };
}

export function createExcelData(items: any[], sheetName: string = 'Data'): Record<string, any[]> {
  return { [sheetName]: items };
}

export function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const base64 = (reader.result as string).split(',')[1];
      resolve(base64);
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

export function detectFileRequest(text: string): { type: 'excel' | 'word' | 'pdf' | 'pptx' | null; confidence: number } {
  const lower = text.toLowerCase();
  
  const patterns = [
    { type: 'excel' as const, keywords: ['excel', 'spreadsheet', '.xlsx', 'csv', 'sheet', 'table data'] },
    { type: 'word' as const, keywords: ['word', 'document', '.docx', 'report', 'write up'] },
    { type: 'pdf' as const, keywords: ['pdf', 'whitepaper', 'download as pdf'] },
    { type: 'pptx' as const, keywords: ['presentation', 'powerpoint', 'pptx', 'slides', 'deck'] }
  ];
  
  for (const pattern of patterns) {
    const matches = pattern.keywords.filter(kw => lower.includes(kw)).length;
    if (matches > 0) {
      return { type: pattern.type, confidence: matches / pattern.keywords.length };
    }
  }
  
  return { type: null, confidence: 0 };
}

export function formatTokenCount(count: number): string {
  if (count >= 1000000) return `${(count / 1000000).toFixed(1)}M`;
  if (count >= 1000) return `${(count / 1000).toFixed(1)}K`;
  return count.toString();
}

export function formatLatency(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
}
