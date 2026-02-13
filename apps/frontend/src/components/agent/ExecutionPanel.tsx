"use client";

/**
 * ExecutionPanel Component (FIXED)
 * ================================
 * 
 * CRITICAL FIXES:
 * 1. Added proper WebSocket URL construction for live screenshots
 * 2. Added file download handling for generated files
 * 3. Added execution state management with proper cleanup
 * 4. Fixed event type handling for different message types
 * 5. Added support for file metadata in completion events
 */

import React, { useState, useEffect, useRef, useCallback } from "react";
import LiveScreen from "./LiveScreen";

// ============================================================================
// TYPES
// ============================================================================

export interface ExecutionStep {
  id: string;
  step_number: number;
  tool: string;
  status: "pending" | "running" | "completed" | "failed";
  title: string;
  instruction: string;
  result_summary?: string;
  execution_time_ms?: number;
  timestamp: string;
}

export interface GeneratedFile {
  id: string;
  filename: string;
  url: string;
  file_type: string;
  size_bytes: number;
  description?: string;
}

export interface ExecutionState {
  execution_id: string;
  status: "idle" | "running" | "completed" | "failed";
  current_step?: ExecutionStep;
  steps: ExecutionStep[];
  screenshot?: {
    image: string;
    url: string;
    title: string;
  };
  result?: any;
  error?: string;
  generated_files: GeneratedFile[];
}

interface ExecutionPanelProps {
  /** Execution ID for WebSocket connection */
  executionId?: string;
  /** Backend API base URL */
  apiBaseUrl?: string;
  /** Whether an execution is active */
  isActive?: boolean;
  /** Callback when execution completes */
  onComplete?: (result: any, files: GeneratedFile[]) => void;
  /** Callback when execution fails */
  onError?: (error: string) => void;
  /** Optional initial state */
  initialState?: Partial<ExecutionState>;
}

// ============================================================================
// COMPONENT
// ============================================================================

export default function ExecutionPanel({
  executionId,
  apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || "https://web-production-29f3c.up.railway.app",
  isActive = false,
  onComplete,
  onError,
  initialState,
}: ExecutionPanelProps) {
  // State
  const [state, setState] = useState<ExecutionState>({
    execution_id: executionId || "",
    status: initialState?.status || "idle",
    steps: initialState?.steps || [],
    generated_files: initialState?.generated_files || [],
    ...initialState,
  });

  const [reasoning, setReasoning] = useState<string>("");
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // ============================================================================
  // FIXED: WebSocket Connection with Correct URL
  // ============================================================================

  useEffect(() => {
    // Only connect if we have an execution ID and are active
    if (!executionId || !isActive) {
      return;
    }

    // FIXED: Construct WebSocket URL correctly
    // Convert HTTP(S) to WS(WSS)
    const wsProtocol = apiBaseUrl.startsWith("https") ? "wss" : "ws";
    const baseUrl = apiBaseUrl.replace(/^https?:\/\//, "");
    
    // FIXED: Use the correct endpoint path that matches the backend
    // Backend expects: /api/v2/ws/execute/{execution_id}
    const wsUrl = `${wsProtocol}://${baseUrl}/api/v2/ws/execute/${executionId}`;

    console.log("[ExecutionPanel] Connecting to WebSocket:", wsUrl);

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("[ExecutionPanel] WebSocket connected");
      setState((prev) => ({ ...prev, status: "running" }));
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        handleWebSocketMessage(message);
      } catch (e) {
        console.error("[ExecutionPanel] Failed to parse WebSocket message:", e);
      }
    };

    ws.onerror = (error) => {
      console.error("[ExecutionPanel] WebSocket error:", error);
      setState((prev) => ({
        ...prev,
        status: "failed",
        error: "WebSocket connection failed",
      }));
      if (onError) {
        onError("WebSocket connection failed");
      }
    };

    ws.onclose = () => {
      console.log("[ExecutionPanel] WebSocket closed");
      wsRef.current = null;
    };

    // Cleanup
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [executionId, isActive, apiBaseUrl]);

  // ============================================================================
  // FIXED: WebSocket Message Handler
  // ============================================================================

  const handleWebSocketMessage = useCallback((message: any) => {
    const { type, data } = message;

    switch (type) {
      // Browser screenshot update
      case "browser_screenshot":
        setState((prev) => ({
          ...prev,
          screenshot: {
            image: data.image,
            url: data.url,
            title: data.title,
          },
        }));
        break;

      // Step update
      case "step_update":
        setState((prev) => {
          const existingStepIndex = prev.steps.findIndex(
            (s) => s.step_number === data.step_id
          );
          
          const newStep: ExecutionStep = {
            id: `step-${data.step_id}`,
            step_number: data.step_id,
            tool: data.tool,
            status: data.status,
            title: data.title,
            instruction: data.instruction,
            result_summary: data.result_summary,
            execution_time_ms: data.execution_time_ms,
            timestamp: data.timestamp,
          };

          let newSteps;
          if (existingStepIndex >= 0) {
            newSteps = [...prev.steps];
            newSteps[existingStepIndex] = newStep;
          } else {
            newSteps = [...prev.steps, newStep];
          }

          return {
            ...prev,
            steps: newSteps,
            current_step: newStep,
          };
        });
        break;

      // Reasoning/thinking updates
      case "reasoning":
        setReasoning((prev) => prev + (data.content || ""));
        break;

      // Execution complete
      case "execution_complete":
        setState((prev) => ({
          ...prev,
          status: data.success ? "completed" : "failed",
          result: data.result,
          // FIXED: Extract generated files from completion event
          generated_files: data.result?.generated_files || prev.generated_files,
        }));

        if (data.success && onComplete) {
          onComplete(data.result, data.result?.generated_files || []);
        } else if (!data.success && onError) {
          onError(data.result?.error || "Execution failed");
        }
        break;

      // Error
      case "error":
        setState((prev) => ({
          ...prev,
          status: "failed",
          error: data.error,
        }));
        if (onError) {
          onError(data.error);
        }
        break;

      // Pong (keepalive response)
      case "pong":
        // No action needed
        break;

      default:
        console.log("[ExecutionPanel] Unknown message type:", type, data);
    }
  }, [onComplete, onError]);

  // ============================================================================
  // Helper: Send ping to keep connection alive
  // ============================================================================

  useEffect(() => {
    if (!wsRef.current || state.status !== "running") return;

    const pingInterval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: "ping" }));
      }
    }, 30000); // Ping every 30 seconds

    return () => clearInterval(pingInterval);
  }, [state.status]);

  // ============================================================================
  // Render
  // ============================================================================

  const isRunning = state.status === "running";
  const isCompleted = state.status === "completed";
  const isFailed = state.status === "failed";

  return (
    <div className="flex flex-col h-full bg-[#0d0d1a] rounded-xl overflow-hidden border border-white/5">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-[#1a1a2e] border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className={`
            w-2.5 h-2.5 rounded-full
            ${isRunning ? "bg-yellow-400 animate-pulse" : ""}
            ${isCompleted ? "bg-green-400" : ""}
            ${isFailed ? "bg-red-400" : ""}
            ${state.status === "idle" ? "bg-white/20" : ""}
          `} />
          <h3 className="text-sm font-medium text-white/90">
            {isRunning && "Executing..."}
            {isCompleted && "Completed"}
            {isFailed && "Failed"}
            {state.status === "idle" && "Ready"}
          </h3>
          {executionId && (
            <span className="text-[10px] text-white/30 font-mono">
              ID: {executionId.slice(0, 8)}
            </span>
          )}
        </div>

        {/* Status badge */}
        {isRunning && (
          <div className="flex items-center gap-1.5 px-2 py-0.5 bg-blue-500/10 rounded text-[10px] text-blue-400">
            <div className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" />
            Live
          </div>
        )}
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-h-0">
        {/* Live Screen (Browser View) */}
        <div className="flex-1 min-h-0 p-3">
          <LiveScreen
            screenshot={state.screenshot?.image || null}
            url={state.screenshot?.url || ""}
            title={state.screenshot?.title || ""}
            isActive={isRunning}
            currentAction={state.current_step?.instruction}
            wsUrl={undefined} // We're handling WebSocket in this component
          />
        </div>

        {/* Steps panel */}
        {state.steps.length > 0 && (
          <div className="max-h-48 overflow-y-auto border-t border-white/5">
            <div className="px-3 py-2 text-[10px] text-white/40 uppercase tracking-wider">
              Execution Steps
            </div>
            <div className="px-3 pb-3 space-y-1">
              {state.steps.map((step) => (
                <div
                  key={step.id}
                  className={`
                    flex items-center gap-2 px-2 py-1.5 rounded text-xs
                    ${step.status === "running" ? "bg-blue-500/10" : "bg-white/5"}
                  `}
                >
                  {/* Status icon */}
                  <div className={`
                    w-4 h-4 rounded-full flex items-center justify-center text-[10px]
                    ${step.status === "completed" ? "bg-green-500/20 text-green-400" : ""}
                    ${step.status === "failed" ? "bg-red-500/20 text-red-400" : ""}
                    ${step.status === "running" ? "bg-blue-500/20 text-blue-400" : ""}
                    ${step.status === "pending" ? "bg-white/10 text-white/40" : ""}
                  `}>
                    {step.status === "completed" && "✓"}
                    {step.status === "failed" && "✕"}
                    {step.status === "running" && "◌"}
                    {step.status === "pending" && "○"}
                  </div>

                  {/* Step info */}
                  <div className="flex-1 min-w-0">
                    <div className="text-white/80 truncate">{step.title}</div>
                    {step.instruction && (
                      <div className="text-[10px] text-white/40 truncate">
                        {step.instruction}
                      </div>
                    )}
                  </div>

                  {/* Execution time */}
                  {step.execution_time_ms && (
                    <div className="text-[10px] text-white/30">
                      {(step.execution_time_ms / 1000).toFixed(1)}s
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Reasoning panel */}
        {reasoning && (
          <div className="max-h-32 overflow-y-auto border-t border-white/5">
            <div className="px-3 py-2 text-[10px] text-white/40 uppercase tracking-wider">
              Reasoning
            </div>
            <div className="px-3 pb-3">
              <pre className="text-[10px] text-white/50 whitespace-pre-wrap font-mono">
                {reasoning}
              </pre>
            </div>
          </div>
        )}

        {/* FIXED: Generated Files Panel */}
        {state.generated_files.length > 0 && (
          <div className="border-t border-white/5 bg-[#1a1a2e]/50">
            <div className="px-3 py-2 text-[10px] text-white/40 uppercase tracking-wider">
              Generated Files
            </div>
            <div className="px-3 pb-3 space-y-1">
              {state.generated_files.map((file) => (
                <a
                  key={file.id}
                  href={file.url}
                  download={file.filename}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 px-2 py-2 bg-white/5 hover:bg-white/10 
                             rounded transition-colors group"
                >
                  {/* File icon */}
                  <span className="text-lg">
                    {file.file_type.includes("excel") || file.file_type.includes("sheet")
                      ? "📊"
                      : file.file_type.includes("pdf")
                      ? "📄"
                      : file.file_type.includes("word")
                      ? "📝"
                      : file.file_type.includes("ppt")
                      ? "📽️"
                      : "📎"}
                  </span>

                  {/* File info */}
                  <div className="flex-1 min-w-0">
                    <div className="text-xs text-white/80 truncate group-hover:text-blue-400 transition-colors">
                      {file.filename}
                    </div>
                    {file.description && (
                      <div className="text-[10px] text-white/40 truncate">
                        {file.description}
                      </div>
                    )}
                  </div>

                  {/* Download icon */}
                  <svg
                    className="w-4 h-4 text-white/30 group-hover:text-blue-400 transition-colors"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                    />
                  </svg>
                </a>
              ))}
            </div>
          </div>
        )}

        {/* Error display */}
        {isFailed && state.error && (
          <div className="p-3 bg-red-500/10 border-t border-red-500/20">
            <div className="flex items-center gap-2 text-xs text-red-400">
              <svg
                className="w-4 h-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              {state.error}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ============================================================================
// Hook for using execution panel
// ============================================================================

export interface UseExecutionPanelReturn {
  executionId: string | null;
  startExecution: () => string;
  stopExecution: () => void;
  isActive: boolean;
  state: ExecutionState;
}

export function useExecutionPanel(): UseExecutionPanelReturn {
  const [executionId, setExecutionId] = useState<string | null>(null);
  const [isActive, setIsActive] = useState(false);
  const [state, setState] = useState<ExecutionState>({
    execution_id: "",
    status: "idle",
    steps: [],
    generated_files: [],
  });

  const startExecution = useCallback((): string => {
    const newId = Math.random().toString(36).substring(2, 15);
    setExecutionId(newId);
    setIsActive(true);
    setState({
      execution_id: newId,
      status: "running",
      steps: [],
      generated_files: [],
    });
    return newId;
  }, []);

  const stopExecution = useCallback(() => {
    setIsActive(false);
    setState((prev) => ({ ...prev, status: "idle" }));
  }, []);

  return {
    executionId,
    startExecution,
    stopExecution,
    isActive,
    state,
  };
}
