/**
 * McLeuker Agentic AI Platform - Lovable API Client
 * 
 * This file provides a complete API client for integrating the McLeuker AI
 * backend with a Lovable frontend. Copy this file into your Lovable project's
 * `src/lib/` directory.
 */

// --- Configuration ---
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// --- Type Definitions ---

export interface TaskRequest {
  prompt: string;
  user_id?: string;
  preferred_outputs?: string[];
  domain_hint?: string;
}

export interface TaskResponse {
  task_id: string;
  status: string;
  interpretation?: TaskInterpretation;
  files?: GeneratedFile[];
  message?: string;
  error?: string;
}

export interface TaskInterpretation {
  intent: string;
  domain: string;
  requires_real_time_research: boolean;
  research_depth: string;
  outputs: string[];
  execution_plan: string[];
}

export interface GeneratedFile {
  filename: string;
  format: string;
  path: string;
  size_bytes: number;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface ChatResponse {
  message: string;
  action_taken?: 'task_execution' | 'search' | 'answer' | 'conversation';
  task_id?: string;
  files?: GeneratedFile[];
  sources?: SearchSource[];
}

export interface SearchRequest {
  query: string;
  num_results?: number;
  summarize?: boolean;
  scrape_top?: number;
}

export interface SearchResponse {
  query: string;
  query_analysis?: Record<string, any>;
  expanded_queries?: string[];
  results: SearchResult[];
  total_results: number;
  summary?: string;
  follow_up_questions?: string[];
  timestamp: string;
}

export interface SearchResult {
  title: string;
  url: string;
  snippet: string;
  source?: string;
  date?: string;
}

export interface SearchSource {
  title: string;
  url: string;
}

export interface ResearchRequest {
  topic: string;
  depth?: 'light' | 'medium' | 'deep';
}

export interface ResearchResponse {
  topic: string;
  depth: string;
  research_questions: string[];
  findings: ResearchFinding[];
  synthesis: string;
  timestamp: string;
}

export interface ResearchFinding {
  question: string;
  summary: string;
  sources: SearchResult[];
}

export interface QuickAnswerRequest {
  question: string;
}

export interface QuickAnswerResponse {
  query: string;
  answer: string;
  sources: SearchSource[];
  confidence: 'low' | 'medium' | 'high';
}

export interface HealthResponse {
  status: string;
  version: string;
  timestamp: string;
}

export interface PlatformStatus {
  status: string;
  agent_state: {
    state: string;
    has_active_task: boolean;
    task_id?: string;
    task_status?: string;
  };
  active_tasks: number;
  supported_outputs: string[];
  timestamp: string;
}

// --- API Error Class ---

export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public details?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

// --- Helper Functions ---

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let details;
    try {
      details = await response.json();
    } catch {
      details = await response.text();
    }
    throw new APIError(
      `API request failed: ${response.statusText}`,
      response.status,
      details
    );
  }
  return response.json();
}

// --- API Client Functions ---

/**
 * Check the health of the backend server.
 */
export async function checkHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`);
  return handleResponse<HealthResponse>(response);
}

/**
 * Get the current status of the platform.
 */
export async function getPlatformStatus(): Promise<PlatformStatus> {
  const response = await fetch(`${API_BASE_URL}/api/status`);
  return handleResponse<PlatformStatus>(response);
}

/**
 * Process a task synchronously.
 * This will wait for the task to complete before returning.
 */
export async function processTask(request: TaskRequest): Promise<TaskResponse> {
  const response = await fetch(`${API_BASE_URL}/api/tasks/sync`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  return handleResponse<TaskResponse>(response);
}

/**
 * Process a task asynchronously.
 * Returns immediately with a task ID that can be used to check status.
 */
export async function processTaskAsync(request: TaskRequest): Promise<{ task_id: string; status: string; message: string }> {
  const response = await fetch(`${API_BASE_URL}/api/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  return handleResponse(response);
}

/**
 * Get the status of a task by ID.
 */
export async function getTaskStatus(taskId: string): Promise<TaskResponse> {
  const response = await fetch(`${API_BASE_URL}/api/tasks/${taskId}`);
  return handleResponse<TaskResponse>(response);
}

/**
 * Get the files generated by a task.
 */
export async function getTaskFiles(taskId: string): Promise<{ files: GeneratedFile[] }> {
  const response = await fetch(`${API_BASE_URL}/api/tasks/${taskId}/files`);
  return handleResponse(response);
}

/**
 * Get the download URL for a generated file.
 */
export function getFileDownloadUrl(filename: string): string {
  return `${API_BASE_URL}/api/files/${filename}`;
}

/**
 * Chat with the AI agent.
 */
export async function chat(request: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  return handleResponse<ChatResponse>(response);
}

/**
 * Perform an AI-powered search.
 */
export async function search(request: SearchRequest): Promise<SearchResponse> {
  const response = await fetch(`${API_BASE_URL}/api/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  return handleResponse<SearchResponse>(response);
}

/**
 * Get a quick answer to a question.
 */
export async function quickAnswer(request: QuickAnswerRequest): Promise<QuickAnswerResponse> {
  const response = await fetch(`${API_BASE_URL}/api/search/quick`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  return handleResponse<QuickAnswerResponse>(response);
}

/**
 * Perform in-depth research on a topic.
 */
export async function researchTopic(request: ResearchRequest): Promise<ResearchResponse> {
  const response = await fetch(`${API_BASE_URL}/api/research`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  return handleResponse<ResearchResponse>(response);
}

/**
 * Interpret a prompt without executing the task.
 * Useful for previewing what the AI will do.
 */
export async function interpretPrompt(prompt: string): Promise<{ interpretation: TaskInterpretation; message: string }> {
  const response = await fetch(`${API_BASE_URL}/api/interpret`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt }),
  });
  return handleResponse(response);
}
