"use client";

/**
 * ExecutionPanelV4 — Manus AI-style Agent Execution Visualization
 * ================================================================
 * Real-time step-by-step execution with:
 * - Thought / reasoning display
 * - Tool call visualization
 * - Live browser screenshots
 * - File generation with download links
 * - Progress tracking
 * - Error handling with retry indicators
 *
 * Connects to V4 WebSocket: /api/v4/ws/execute/{execution_id}
 * Falls back to V2 WebSocket: /api/v2/ws/execute/{execution_id}
 */

import React, { useEffect, useRef, useState, useCallback } from "react";
import { useExecutionWebSocket } from "@/hooks/useExecutionWebSocket";
import LiveScreen from "./LiveScreen";

// ============================================================================
// TYPES
// ============================================================================

export interface ExecutionStepV4 {
  id: string;
  type:
    | "thought"
    | "action"
    | "observation"
    | "tool_call"
    | "tool_result"
    | "error"
    | "completion"
    | "plan";
  content: string;
  tool_name?: string;
  tool_input?: Record<string, any>;
  tool_output?: any;
  status:
    | "pending"
    | "running"
    | "completed"
    | "failed"
    | "retrying"
    | "paused";
  timestamp: string;
  duration_ms?: number;
  error?: string;
  retry_count?: number;
  screenshot?: string;
  metadata?: Record<string, any>;
}

export interface GeneratedFileV4 {
  id: string;
  filename: string;
  url: string;
  file_type: string;
  size_bytes?: number;
  description?: string;
}

export interface ExecutionStateV4 {
  id: string;
  status: "idle" | "running" | "paused" | "completed" | "failed";
  steps: ExecutionStepV4[];
  currentStepIndex: number;
  startTime?: string;
  endTime?: string;
  progress: number;
  screenshot?: { image: string; url: string; title: string };
  generated_files: GeneratedFileV4[];
  result?: any;
  error?: string;
}

interface ExecutionPanelV4Props {
  executionId?: string;
  apiBaseUrl?: string;
  isActive?: boolean;
  onComplete?: (result: any, files: GeneratedFileV4[]) => void;
  onError?: (error: string) => void;
  className?: string;
  showScreenshots?: boolean;
}

// ============================================================================
// HELPERS
// ============================================================================

const formatDuration = (ms?: number): string => {
  if (!ms) return "";
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
};

const formatTime = (timestamp: string): string => {
  try {
    const date = new Date(timestamp);
    return date.toLocaleTimeString("en-US", {
      hour12: false,
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  } catch {
    return "--:--:--";
  }
};

const STEP_ICONS: Record<string, string> = {
  thought: "🧠",
  action: "▶️",
  observation: "👁️",
  tool_call: "🔧",
  tool_result: "✅",
  error: "❌",
  completion: "🎯",
  plan: "📋",
};

const STEP_COLORS: Record<string, string> = {
  thought: "border-purple-500/30 bg-purple-500/5",
  action: "border-blue-500/30 bg-blue-500/5",
  observation: "border-cyan-500/30 bg-cyan-500/5",
  tool_call: "border-amber-500/30 bg-amber-500/5",
  tool_result: "border-green-500/30 bg-green-500/5",
  error: "border-red-500/30 bg-red-500/5",
  completion: "border-emerald-500/30 bg-emerald-500/5",
  plan: "border-indigo-500/30 bg-indigo-500/5",
};

const FILE_ICONS: Record<string, string> = {
  pdf: "📄",
  xlsx: "📊",
  xls: "📊",
  csv: "📊",
  docx: "📝",
  doc: "📝",
  pptx: "📽️",
  ppt: "📽️",
  txt: "📃",
  md: "📃",
  json: "📋",
  html: "🌐",
  py: "🐍",
  js: "📜",
  ts: "📜",
};

function getFileIcon(filename: string): string {
  const ext = filename.split(".").pop()?.toLowerCase() || "";
  return FILE_ICONS[ext] || "📎";
}

// ============================================================================
// STEP ITEM COMPONENT
// ============================================================================

const StepItem: React.FC<{
  step: ExecutionStepV4;
  isActive: boolean;
  isExpanded: boolean;
  onToggle: () => void;
}> = ({ step, isActive, isExpanded, onToggle }) => {
  const icon = STEP_ICONS[step.type] || "▶️";
  const colorClass = STEP_COLORS[step.type] || STEP_COLORS.action;
  const isRunning = step.status === "running" || step.status === "retrying";

  return (
    <div
      className={`border rounded-lg overflow-hidden transition-all duration-200 ${colorClass} ${
        isActive ? "ring-1 ring-blue-500/40" : ""
      }`}
    >
      {/* Header */}
      <button
        onClick={onToggle}
        className="w-full flex items-center gap-2.5 px-3 py-2 text-left hover:bg-white/5 transition-colors"
      >
        {/* Status dot */}
        <div
          className={`w-2 h-2 rounded-full flex-shrink-0 ${
            isRunning ? "bg-blue-400 animate-pulse" : ""
          } ${step.status === "completed" ? "bg-green-400" : ""} ${
            step.status === "failed" ? "bg-red-400" : ""
          } ${step.status === "pending" ? "bg-white/20" : ""}`}
        />

        {/* Icon */}
        <span className="text-sm flex-shrink-0">{icon}</span>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-medium text-white/40 uppercase tracking-wider">
              {step.type.replace("_", " ")}
            </span>
            {step.tool_name && (
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/10 text-white/60">
                {step.tool_name}
              </span>
            )}
            {step.retry_count ? (
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400">
                Retry {step.retry_count}
              </span>
            ) : null}
          </div>
          <p className="text-xs text-white/80 truncate mt-0.5">
            {step.content}
          </p>
        </div>

        {/* Duration */}
        {step.duration_ms ? (
          <span className="text-[10px] text-white/30 flex-shrink-0">
            {formatDuration(step.duration_ms)}
          </span>
        ) : null}

        {/* Time */}
        <span className="text-[10px] text-white/20 flex-shrink-0">
          {formatTime(step.timestamp)}
        </span>

        {/* Expand arrow */}
        <span className="text-white/30 text-xs flex-shrink-0">
          {isExpanded ? "▼" : "▶"}
        </span>
      </button>

      {/* Expanded content */}
      {isExpanded && (
        <div className="border-t border-white/5 bg-black/20 px-3 py-2.5 space-y-2">
          {/* Full content */}
          <div className="text-xs text-white/70 whitespace-pre-wrap">
            {step.content}
          </div>

          {/* Tool input */}
          {step.tool_input && (
            <div>
              <span className="text-[10px] text-white/40">Input:</span>
              <pre className="text-[10px] bg-black/30 rounded p-2 mt-1 overflow-x-auto text-white/50">
                {JSON.stringify(step.tool_input, null, 2)}
              </pre>
            </div>
          )}

          {/* Tool output */}
          {step.tool_output && (
            <div>
              <span className="text-[10px] text-white/40">Output:</span>
              <pre className="text-[10px] bg-black/30 rounded p-2 mt-1 overflow-x-auto text-green-400/70">
                {typeof step.tool_output === "string"
                  ? step.tool_output
                  : JSON.stringify(step.tool_output, null, 2)}
              </pre>
            </div>
          )}

          {/* Error */}
          {step.error && (
            <div>
              <span className="text-[10px] text-red-400">Error:</span>
              <pre className="text-[10px] bg-red-500/10 border border-red-500/20 rounded p-2 mt-1 overflow-x-auto text-red-400/80">
                {step.error}
              </pre>
            </div>
          )}

          {/* Screenshot */}
          {step.screenshot && (
            <div>
              <span className="text-[10px] text-white/40">Screenshot:</span>
              <div className="rounded-lg overflow-hidden border border-white/10 mt-1">
                <img
                  src={`data:image/jpeg;base64,${step.screenshot}`}
                  alt="Step screenshot"
                  className="w-full h-auto"
                />
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function ExecutionPanelV4({
  executionId,
  apiBaseUrl = process.env.NEXT_PUBLIC_API_URL ||
    "https://web-production-29f3c.up.railway.app",
  isActive = false,
  onComplete,
  onError,
  className = "",
  showScreenshots = true,
}: ExecutionPanelV4Props) {
  const [state, setState] = useState<ExecutionStateV4>({
    id: executionId || "",
    status: "idle",
    steps: [],
    currentStepIndex: -1,
    progress: 0,
    generated_files: [],
  });

  const [expandedSteps, setExpandedSteps] = useState<Set<string>>(new Set());
  const [isMinimized, setIsMinimized] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const stepCounterRef = useRef(0);

  // Build WebSocket URL
  const wsProtocol = apiBaseUrl.startsWith("https") ? "wss" : "ws";
  const baseHost = apiBaseUrl.replace(/^https?:\/\//, "");
  const wsUrl = executionId
    ? `${wsProtocol}://${baseHost}/api/v4/ws/execute/${executionId}`
    : "";

  // Handle incoming WebSocket messages
  const handleMessage = useCallback(
    (message: any) => {
      const { type, data } = message;

      switch (type) {
        case "step": {
          const stepData = data;
          const newStep: ExecutionStepV4 = {
            id: stepData.id || `step-${stepCounterRef.current++}`,
            type: stepData.type || "action",
            content: stepData.content || "",
            tool_name: stepData.tool_name,
            tool_input: stepData.tool_input,
            tool_output: stepData.tool_output,
            status: stepData.status || "completed",
            timestamp: stepData.timestamp || new Date().toISOString(),
            duration_ms: stepData.duration_ms,
            error: stepData.error,
            retry_count: stepData.retry_count,
            screenshot: stepData.screenshot,
            metadata: stepData.metadata,
          };

          setState((prev) => {
            const existingIdx = prev.steps.findIndex(
              (s) => s.id === newStep.id
            );
            let newSteps: ExecutionStepV4[];
            if (existingIdx >= 0) {
              newSteps = [...prev.steps];
              newSteps[existingIdx] = newStep;
            } else {
              newSteps = [...prev.steps, newStep];
            }
            return {
              ...prev,
              steps: newSteps,
              currentStepIndex: newSteps.length - 1,
              progress: Math.min(
                95,
                Math.round((newSteps.length / 20) * 100)
              ),
            };
          });

          // Auto-expand current step
          setExpandedSteps((prev) => new Set([...prev, newStep.id]));
          break;
        }

        case "thought": {
          const step: ExecutionStepV4 = {
            id: `thought-${stepCounterRef.current++}`,
            type: "thought",
            content: data.content || "",
            status: "completed",
            timestamp: new Date().toISOString(),
          };
          setState((prev) => ({
            ...prev,
            steps: [...prev.steps, step],
            currentStepIndex: prev.steps.length,
          }));
          setExpandedSteps((prev) => new Set([...prev, step.id]));
          break;
        }

        case "tool_call": {
          const step: ExecutionStepV4 = {
            id: `tool-${stepCounterRef.current++}`,
            type: "tool_call",
            content: `Calling ${data.tool}`,
            tool_name: data.tool,
            tool_input: data.input,
            status: "running",
            timestamp: new Date().toISOString(),
          };
          setState((prev) => ({
            ...prev,
            steps: [...prev.steps, step],
            currentStepIndex: prev.steps.length,
          }));
          setExpandedSteps((prev) => new Set([...prev, step.id]));
          break;
        }

        case "observation": {
          const step: ExecutionStepV4 = {
            id: `obs-${stepCounterRef.current++}`,
            type: "observation",
            content: `Result from ${data.tool}`,
            tool_name: data.tool,
            tool_output: data.output,
            status: "completed",
            timestamp: new Date().toISOString(),
          };
          setState((prev) => ({
            ...prev,
            steps: [...prev.steps, step],
            currentStepIndex: prev.steps.length,
          }));
          break;
        }

        case "browser_screenshot": {
          setState((prev) => ({
            ...prev,
            screenshot: {
              image: data.image || data.screenshot || "",
              url: data.url || "",
              title: data.title || "",
            },
          }));
          break;
        }

        case "step_update": {
          // V2 compatibility
          const newStep: ExecutionStepV4 = {
            id: `step-${data.step_id || stepCounterRef.current++}`,
            type: "action",
            content: data.title || data.instruction || "",
            tool_name: data.tool,
            status: data.status || "running",
            timestamp: data.timestamp || new Date().toISOString(),
            duration_ms: data.execution_time_ms,
          };
          setState((prev) => {
            const existingIdx = prev.steps.findIndex(
              (s) => s.id === newStep.id
            );
            let newSteps: ExecutionStepV4[];
            if (existingIdx >= 0) {
              newSteps = [...prev.steps];
              newSteps[existingIdx] = newStep;
            } else {
              newSteps = [...prev.steps, newStep];
            }
            return {
              ...prev,
              steps: newSteps,
              currentStepIndex: newSteps.length - 1,
            };
          });
          break;
        }

        case "reasoning": {
          const step: ExecutionStepV4 = {
            id: `reason-${stepCounterRef.current++}`,
            type: "thought",
            content: data.content || "",
            status: "completed",
            timestamp: new Date().toISOString(),
          };
          setState((prev) => ({
            ...prev,
            steps: [...prev.steps, step],
          }));
          break;
        }

        case "completion":
        case "execution_complete": {
          setState((prev) => ({
            ...prev,
            status: data.success !== false ? "completed" : "failed",
            progress: 100,
            endTime: new Date().toISOString(),
            result: data.result || data.content,
            generated_files:
              data.result?.generated_files || prev.generated_files,
          }));
          if (data.success !== false) {
            onComplete?.(
              data.result || data.content,
              data.result?.generated_files || []
            );
          } else {
            onError?.(data.result?.error || "Execution failed");
          }
          break;
        }

        case "download": {
          const file: GeneratedFileV4 = {
            id: data.file_id || `file-${Date.now()}`,
            filename: data.filename || "download",
            url: data.download_url
              ? data.download_url.startsWith("http")
                ? data.download_url
                : `${apiBaseUrl}${data.download_url}`
              : "",
            file_type: data.file_type || "unknown",
            size_bytes: data.size_bytes,
            description: data.description,
          };
          setState((prev) => ({
            ...prev,
            generated_files: [...prev.generated_files, file],
          }));
          break;
        }

        case "error": {
          setState((prev) => ({
            ...prev,
            status: "failed",
            error: data.error || "Unknown error",
          }));
          onError?.(data.error || "Unknown error");
          break;
        }

        case "execution_start": {
          setState((prev) => ({
            ...prev,
            status: "running",
            startTime: new Date().toISOString(),
          }));
          break;
        }
      }
    },
    [apiBaseUrl, onComplete, onError]
  );

  // WebSocket connection
  const { connected, connecting } = useExecutionWebSocket({
    url: wsUrl,
    enabled: !!executionId && isActive && !!wsUrl,
    onMessage: handleMessage,
    onConnect: () => {
      setState((prev) => ({
        ...prev,
        status: "running",
        startTime: new Date().toISOString(),
      }));
    },
    onError: () => {
      // Silently handle — will auto-reconnect
    },
  });

  // Auto-scroll
  useEffect(() => {
    if (scrollRef.current && state.status === "running") {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [state.steps, state.status]);

  const toggleStep = (stepId: string) => {
    setExpandedSteps((prev) => {
      const next = new Set(prev);
      if (next.has(stepId)) next.delete(stepId);
      else next.add(stepId);
      return next;
    });
  };

  // ============================================================================
  // RENDER
  // ============================================================================

  const isRunning = state.status === "running";
  const isCompleted = state.status === "completed";
  const isFailed = state.status === "failed";

  if (isMinimized) {
    return (
      <div
        className="fixed bottom-4 right-4 z-50 bg-[#0d0d1a] border border-white/10 rounded-lg shadow-xl p-3 flex items-center gap-3 cursor-pointer hover:border-white/20 transition-colors"
        onClick={() => setIsMinimized(false)}
      >
        <div
          className={`w-2.5 h-2.5 rounded-full ${
            isRunning ? "bg-blue-400 animate-pulse" : ""
          } ${isCompleted ? "bg-green-400" : ""} ${
            isFailed ? "bg-red-400" : ""
          }`}
        />
        <span className="text-xs font-medium text-white/80">
          {isRunning
            ? "Executing..."
            : isCompleted
            ? "Completed"
            : isFailed
            ? "Failed"
            : "Idle"}
        </span>
        <span className="text-[10px] text-white/40">{state.progress}%</span>
      </div>
    );
  }

  return (
    <div
      className={`flex flex-col h-full bg-[#0d0d1a] rounded-xl overflow-hidden border border-white/5 ${className}`}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-[#1a1a2e] border-b border-white/5">
        <div className="flex items-center gap-3">
          <div
            className={`w-2.5 h-2.5 rounded-full ${
              isRunning ? "bg-blue-400 animate-pulse" : ""
            } ${isCompleted ? "bg-green-400" : ""} ${
              isFailed ? "bg-red-400" : ""
            } ${state.status === "idle" ? "bg-white/20" : ""}`}
          />
          <div>
            <h3 className="text-sm font-medium text-white/90">
              {isRunning
                ? "Executing..."
                : isCompleted
                ? "Completed"
                : isFailed
                ? "Failed"
                : "Ready"}
            </h3>
            {executionId && (
              <span className="text-[10px] text-white/30 font-mono">
                {executionId.slice(0, 8)}
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Progress bar */}
          <div className="flex items-center gap-2 mr-2">
            <div className="w-20 h-1.5 bg-white/5 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-500 transition-all duration-300"
                style={{ width: `${state.progress}%` }}
              />
            </div>
            <span className="text-[10px] text-white/40">
              {state.progress}%
            </span>
          </div>

          {/* Connection status */}
          <div
            className={`flex items-center gap-1 px-2 py-0.5 rounded text-[10px] ${
              connected
                ? "bg-green-500/10 text-green-400"
                : connecting
                ? "bg-amber-500/10 text-amber-400"
                : "bg-white/5 text-white/30"
            }`}
          >
            <div
              className={`w-1.5 h-1.5 rounded-full ${
                connected
                  ? "bg-green-400"
                  : connecting
                  ? "bg-amber-400 animate-pulse"
                  : "bg-white/20"
              }`}
            />
            {connected ? "Live" : connecting ? "Connecting" : "Offline"}
          </div>

          {/* Minimize */}
          <button
            onClick={() => setIsMinimized(true)}
            className="p-1.5 rounded text-white/30 hover:text-white/60 hover:bg-white/5 transition-colors"
            title="Minimize"
          >
            <svg
              className="w-3.5 h-3.5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </button>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex min-h-0">
        {/* Steps list */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto p-3 space-y-1.5">
          {state.steps.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-white/30">
              <span className="text-3xl mb-2">🤖</span>
              <p className="text-xs">No execution steps yet</p>
              <p className="text-[10px] text-white/20 mt-1">
                Start a task to see agent reasoning
              </p>
            </div>
          ) : (
            state.steps.map((step, index) => (
              <StepItem
                key={step.id}
                step={step}
                isActive={index === state.currentStepIndex}
                isExpanded={expandedSteps.has(step.id)}
                onToggle={() => toggleStep(step.id)}
              />
            ))
          )}
        </div>

        {/* Screenshot panel */}
        {showScreenshots && state.screenshot?.image && (
          <div className="w-72 border-l border-white/5 bg-[#0a0a14] flex flex-col">
            <div className="px-3 py-2 border-b border-white/5">
              <h4 className="text-[10px] font-medium text-white/40 uppercase tracking-wider flex items-center gap-1.5">
                👁️ Live View
              </h4>
            </div>
            <div className="flex-1 p-2 overflow-y-auto">
              <LiveScreen
                screenshot={state.screenshot.image}
                url={state.screenshot.url}
                title={state.screenshot.title}
                isActive={isRunning}
              />
            </div>
          </div>
        )}
      </div>

      {/* Generated files */}
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
                className="flex items-center gap-2 px-2 py-2 bg-white/5 hover:bg-white/10 rounded transition-colors group"
              >
                <span className="text-base">{getFileIcon(file.filename)}</span>
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
                <svg
                  className="w-4 h-4 text-white/30 group-hover:text-blue-400 transition-colors flex-shrink-0"
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

      {/* Error */}
      {isFailed && state.error && (
        <div className="p-3 bg-red-500/10 border-t border-red-500/20">
          <div className="flex items-center gap-2 text-xs text-red-400">
            <span>❌</span>
            {state.error}
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="px-3 py-2 border-t border-white/5 bg-[#1a1a2e]/30 flex items-center justify-between text-[10px] text-white/30">
        <div className="flex items-center gap-3">
          <span>
            ⏱️ {state.startTime ? formatTime(state.startTime) : "--:--:--"}
          </span>
          <span>{state.steps.length} steps</span>
        </div>
        {state.endTime && <span>Done at {formatTime(state.endTime)}</span>}
      </div>
    </div>
  );
}

// ============================================================================
// HOOK
// ============================================================================

export function useExecutionPanelV4() {
  const [executionId, setExecutionId] = useState<string | null>(null);
  const [isActive, setIsActive] = useState(false);

  const startExecution = useCallback((): string => {
    const newId = Math.random().toString(36).substring(2, 15);
    setExecutionId(newId);
    setIsActive(true);
    return newId;
  }, []);

  const stopExecution = useCallback(() => {
    setIsActive(false);
  }, []);

  return { executionId, startExecution, stopExecution, isActive };
}
