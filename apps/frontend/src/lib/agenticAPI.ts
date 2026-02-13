/**
 * McLeuker AI V9.0 - Agentic Execution API Service
 * =================================================
 * Handles communication with execution endpoints.
 * Supports both legacy /api/v2 and new /api/execute endpoints.
 * Provides SSE streaming for real-time execution updates.
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

export interface Capabilities {
  version: string;
  reasoning: {
    multi_layer: boolean;
    streaming: boolean;
    modes: string[];
  };
  execution: {
    available: boolean;
    web_automation: boolean;
    file_generation: boolean;
    code_execution: boolean;
    api_calls: boolean;
    credential_management: boolean;
    supported_services: string[];
  };
  image: {
    generation: boolean;
    editing: boolean;
    analysis: boolean;
    provider: string;
  };
  documents: {
    formats: string[];
    export: boolean;
  };
  domain_agents: {
    available: boolean;
    agents: string[];
  };
  file_analysis: {
    available: boolean;
    supported_types: string[];
  };
}

// ============================================================================
// SSE PARSER HELPER
// ============================================================================

async function* parseSSEStream(
  response: Response
): AsyncGenerator<ExecutionEvent> {
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
            console.error('Failed to parse SSE event:', e);
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
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
   * Build headers with optional auth token
   */
  private buildHeaders(authToken?: string, contentType?: string): Record<string, string> {
    const headers: Record<string, string> = {};
    if (contentType) headers['Content-Type'] = contentType;
    if (authToken) headers['Authorization'] = `Bearer ${authToken}`;
    return headers;
  }

  // ==========================================================================
  // V9 Execution Engine (new endpoints)
  // ==========================================================================

  /**
   * Execute a task with SSE streaming via the V9 execution engine.
   * This is the primary endpoint for agentic execution.
   */
  async *executeStreamV9(
    query: string,
    options: {
      userId?: string;
      sessionId?: string;
      mode?: string;
      context?: Record<string, unknown>;
      authToken?: string;
    } = {}
  ): AsyncGenerator<ExecutionEvent> {
    const headers = this.buildHeaders(options.authToken, 'application/json');
    headers['Accept'] = 'text/event-stream';

    const response = await fetch(`${this.baseUrl}/api/execute/stream`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        query,
        user_id: options.userId,
        session_id: options.sessionId,
        mode: options.mode || 'auto',
        context: options.context || {},
      }),
    });

    if (!response.ok) {
      throw new Error(`Execution failed: HTTP ${response.status}`);
    }

    yield* parseSSEStream(response);
  }

  /**
   * Execute a task non-streaming via the V9 execution engine.
   */
  async executeV9(
    query: string,
    options: {
      userId?: string;
      sessionId?: string;
      mode?: string;
      context?: Record<string, unknown>;
      authToken?: string;
    } = {}
  ): Promise<{
    success: boolean;
    result?: Record<string, unknown>;
    events?: ExecutionEvent[];
    error?: string;
  }> {
    const headers = this.buildHeaders(options.authToken, 'application/json');

    const response = await fetch(`${this.baseUrl}/api/execute`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        query,
        user_id: options.userId,
        session_id: options.sessionId,
        mode: options.mode || 'auto',
        context: options.context || {},
      }),
    });

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return response.json();
  }

  /**
   * Get execution task status
   */
  async getExecutionStatusV9(
    taskId: string,
    authToken?: string
  ): Promise<{
    success: boolean;
    task: Record<string, unknown>;
  }> {
    const headers = this.buildHeaders(authToken);

    const response = await fetch(`${this.baseUrl}/api/execute/${taskId}`, {
      headers,
    });

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return response.json();
  }

  /**
   * List active execution tasks
   */
  async listActiveExecutions(
    authToken?: string
  ): Promise<{
    success: boolean;
    tasks: Record<string, unknown>[];
  }> {
    const headers = this.buildHeaders(authToken);

    const response = await fetch(`${this.baseUrl}/api/execute/active/list`, {
      headers,
    });

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return response.json();
  }

  // ==========================================================================
  // Capabilities & Status
  // ==========================================================================

  /**
   * Get system capabilities
   */
  async getCapabilities(authToken?: string): Promise<Capabilities> {
    const headers = this.buildHeaders(authToken);

    const response = await fetch(`${this.baseUrl}/api/capabilities`, {
      headers,
    });

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const data = await response.json();
    return data.capabilities;
  }

  /**
   * Get enhancement system status
   */
  async getEnhancementStatus(authToken?: string): Promise<Record<string, unknown>> {
    const headers = this.buildHeaders(authToken);

    const response = await fetch(`${this.baseUrl}/api/enhancement/status`, {
      headers,
    });

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const data = await response.json();
    return data.status;
  }

  // ==========================================================================
  // Legacy V2 Endpoints (backward compatibility)
  // ==========================================================================

  /**
   * Start an agentic execution with SSE streaming (legacy V2)
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
    const headers = this.buildHeaders(options.authToken, 'application/json');
    headers['Accept'] = 'text/event-stream';

    // Try V9 first, fall back to V2
    try {
      const response = await fetch(`${this.baseUrl}/api/execute/stream`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          query: task,
          user_id: options.userId,
          session_id: options.conversationId,
          mode: options.mode || 'auto',
          context: options.context || {},
        }),
      });

      if (response.ok) {
        yield* parseSSEStream(response);
        return;
      }
    } catch (e) {
      console.warn('V9 execute/stream failed, trying V2 fallback:', e);
    }

    // V2 fallback
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

    yield* parseSSEStream(response);
  }

  /**
   * Execute code in sandbox
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
    const headers = this.buildHeaders(authToken, 'application/json');

    const response = await fetch(`${this.baseUrl}/api/v2/code/execute`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ code, language }),
    });

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return response.json();
  }

  /**
   * Browse a URL using browser automation
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
    const headers = this.buildHeaders(authToken, 'application/json');

    const response = await fetch(`${this.baseUrl}/api/v2/browser/action`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ url, action }),
    });

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return response.json();
  }

  /**
   * Get execution status (legacy V2)
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
    const headers = this.buildHeaders(authToken);

    // Try V9 first
    try {
      const response = await fetch(`${this.baseUrl}/api/execute/${executionId}`, {
        headers,
      });
      if (response.ok) {
        const data = await response.json();
        return {
          execution_id: executionId,
          status: data.task?.status || 'unknown',
          steps: data.task?.plan?.steps || [],
          progress: data.task?.current_step_index || 0,
        };
      }
    } catch (e) {
      // Fall through to V2
    }

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
    const headers = this.buildHeaders(authToken);

    await fetch(`${this.baseUrl}/api/v2/execute/${executionId}/pause`, {
      method: 'POST',
      headers,
    });
  }

  /**
   * Resume an execution
   */
  async resumeExecution(executionId: string, authToken?: string): Promise<void> {
    const headers = this.buildHeaders(authToken);

    await fetch(`${this.baseUrl}/api/v2/execute/${executionId}/resume`, {
      method: 'POST',
      headers,
    });
  }

  /**
   * Cancel an execution
   */
  async cancelExecution(executionId: string, authToken?: string): Promise<void> {
    const headers = this.buildHeaders(authToken);

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
    const headers = this.buildHeaders(authToken, 'application/json');

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
