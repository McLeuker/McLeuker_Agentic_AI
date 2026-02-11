/**
 * McLeuker AI V6.0 - Agentic Execution API Service
 * Handles communication with v2 agentic execution endpoints
 * Provides SSE streaming for real-time execution updates
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://web-production-29f3c.up.railway.app';

// ============================================================================
// TYPES
// ============================================================================

export interface ExecutionStep {
  id: string;
  phase: 'planning' | 'research' | 'execution' | 'verification' | 'delivery';
  title: string;
  status: 'pending' | 'active' | 'complete' | 'error' | 'skipped';
  detail?: string;
  progress?: number;
  startedAt?: string;
  completedAt?: string;
  artifacts?: ExecutionArtifact[];
  subSteps?: { label: string; status: string }[];
}

export interface ExecutionArtifact {
  type: 'file' | 'code' | 'data' | 'url' | 'image';
  name: string;
  url?: string;
  content?: string;
  mimeType?: string;
}

export interface ExecutionState {
  executionId: string | null;
  status: 'idle' | 'planning' | 'executing' | 'paused' | 'completed' | 'error';
  steps: ExecutionStep[];
  content: string;
  reasoning: string;
  artifacts: ExecutionArtifact[];
  error: string | null;
  progress: number;
  startedAt: string | null;
  completedAt: string | null;
}

export interface ExecutionEvent {
  type: string;
  data: Record<string, unknown>;
  timestamp?: string;
}

// ============================================================================
// AGENTIC API SERVICE
// ============================================================================

export class AgenticAPIService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Start an agentic execution with SSE streaming
   * This is the main entry point for agent mode
   */
  async *executeStream(
    task: string,
    options: {
      userId?: string;
      conversationId?: string;
      mode?: string;
      context?: Record<string, unknown>;
      authToken?: string;
    } = {}
  ): AsyncGenerator<ExecutionEvent> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'Accept': 'text/event-stream',
    };
    if (options.authToken) {
      headers['Authorization'] = `Bearer ${options.authToken}`;
    }

    const response = await fetch(`${this.baseUrl}/api/v2/execute/stream`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        task,
        user_id: options.userId,
        conversation_id: options.conversationId,
        mode: options.mode || 'agent',
        context: options.context || {},
      }),
    });

    if (!response.ok) {
      throw new Error(`Execution failed: HTTP ${response.status}`);
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
              const event: ExecutionEvent = JSON.parse(line.slice(6));
              yield event;
            } catch (e) {
              console.error('Failed to parse agentic SSE event:', e);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  /**
   * Execute code in E2B sandbox
   */
  async executeCode(
    code: string,
    language: string = 'python',
    authToken?: string
  ): Promise<{
    success: boolean;
    output?: string;
    error?: string;
    executionTime?: number;
  }> {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (authToken) headers['Authorization'] = `Bearer ${authToken}`;

    const response = await fetch(`${this.baseUrl}/api/v2/code/execute`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ code, language }),
    });

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return response.json();
  }

  /**
   * Browse a URL using Browserless
   */
  async browseUrl(
    url: string,
    action: string = 'scrape',
    authToken?: string
  ): Promise<{
    success: boolean;
    content?: string;
    screenshot?: string;
    error?: string;
  }> {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (authToken) headers['Authorization'] = `Bearer ${authToken}`;

    const response = await fetch(`${this.baseUrl}/api/v2/browser/action`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ url, action }),
    });

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return response.json();
  }

  /**
   * Get execution status
   */
  async getExecutionStatus(
    executionId: string,
    authToken?: string
  ): Promise<{
    execution_id: string;
    status: string;
    steps: ExecutionStep[];
    progress: number;
  }> {
    const headers: Record<string, string> = {};
    if (authToken) headers['Authorization'] = `Bearer ${authToken}`;

    const response = await fetch(`${this.baseUrl}/api/v2/execute/${executionId}/status`, {
      headers,
    });

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return response.json();
  }

  /**
   * Pause an execution
   */
  async pauseExecution(executionId: string, authToken?: string): Promise<void> {
    const headers: Record<string, string> = {};
    if (authToken) headers['Authorization'] = `Bearer ${authToken}`;

    await fetch(`${this.baseUrl}/api/v2/execute/${executionId}/pause`, {
      method: 'POST',
      headers,
    });
  }

  /**
   * Resume an execution
   */
  async resumeExecution(executionId: string, authToken?: string): Promise<void> {
    const headers: Record<string, string> = {};
    if (authToken) headers['Authorization'] = `Bearer ${authToken}`;

    await fetch(`${this.baseUrl}/api/v2/execute/${executionId}/resume`, {
      method: 'POST',
      headers,
    });
  }

  /**
   * Cancel an execution
   */
  async cancelExecution(executionId: string, authToken?: string): Promise<void> {
    const headers: Record<string, string> = {};
    if (authToken) headers['Authorization'] = `Bearer ${authToken}`;

    await fetch(`${this.baseUrl}/api/v2/execute/${executionId}/cancel`, {
      method: 'POST',
      headers,
    });
  }

  /**
   * Verify a fact using Grok
   */
  async verifyFact(
    claim: string,
    authToken?: string
  ): Promise<{
    verified: boolean;
    confidence: number;
    explanation: string;
    sources: string[];
  }> {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (authToken) headers['Authorization'] = `Bearer ${authToken}`;

    const response = await fetch(`${this.baseUrl}/api/v2/verify`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ claim }),
    });

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return response.json();
  }
}

// Export singleton
export const agenticAPI = new AgenticAPIService();
export default agenticAPI;
