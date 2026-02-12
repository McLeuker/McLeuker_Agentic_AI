"use client";

import React, { useState, useRef, useEffect } from "react";
import LiveScreen from "./LiveScreen";

// ============================================================================
// TYPES
// ============================================================================

export interface ExecutionStep {
  id: number;
  tool: string;
  title: string;
  status: "pending" | "running" | "completed" | "failed";
  instruction?: string;
  resultSummary?: string;
  executionTimeMs?: number;
}

export interface BrowserScreenshot {
  image: string;
  url: string;
  title: string;
  action?: string;
}

export interface ExecutionPanelProps {
  /** List of execution steps */
  steps: ExecutionStep[];
  /** Current browser screenshot */
  browserScreenshot: BrowserScreenshot | null;
  /** Whether the agent is actively executing */
  isExecuting: boolean;
  /** Reasoning/analysis content */
  reasoning: string;
  /** Live content preview (streaming text) */
  liveContent: string;
  /** Current action being performed */
  currentAction?: string;
  /** WebSocket URL for live screenshots */
  wsUrl?: string;
}

// ============================================================================
// TOOL ICONS
// ============================================================================

const TOOL_ICONS: Record<string, string> = {
  browser: "🌐",
  search: "🔍",
  code: "⚡",
  github: "📦",
  think: "🧠",
  file: "📄",
};

const TOOL_COLORS: Record<string, string> = {
  browser: "text-blue-400",
  search: "text-purple-400",
  code: "text-green-400",
  github: "text-orange-400",
  think: "text-cyan-400",
  file: "text-yellow-400",
};

// ============================================================================
// STEP ITEM COMPONENT
// ============================================================================

function StepItem({ step }: { step: ExecutionStep }) {
  const icon = TOOL_ICONS[step.tool] || "⚙️";
  const color = TOOL_COLORS[step.tool] || "text-white/60";

  return (
    <div className="flex items-start gap-3 py-2.5 px-3 group">
      {/* Status indicator */}
      <div className="mt-0.5 flex-shrink-0">
        {step.status === "running" ? (
          <div className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
        ) : step.status === "completed" ? (
          <div className="w-4 h-4 rounded-full bg-green-500/20 flex items-center justify-center">
            <svg className="w-2.5 h-2.5 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
            </svg>
          </div>
        ) : step.status === "failed" ? (
          <div className="w-4 h-4 rounded-full bg-red-500/20 flex items-center justify-center">
            <svg className="w-2.5 h-2.5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
        ) : (
          <div className="w-4 h-4 rounded-full border border-white/10" />
        )}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-sm">{icon}</span>
          <span className={`text-sm font-medium ${step.status === "running" ? "text-white" : step.status === "completed" ? "text-white/70" : "text-white/40"}`}>
            {step.title}
          </span>
          {step.executionTimeMs && (
            <span className="text-[10px] text-white/20 ml-auto">
              {step.executionTimeMs}ms
            </span>
          )}
        </div>

        {step.status === "running" && step.instruction && (
          <p className="text-xs text-white/30 mt-1 line-clamp-2">
            {step.instruction}
          </p>
        )}

        {step.status === "completed" && step.resultSummary && (
          <p className="text-xs text-white/25 mt-1 line-clamp-1">
            {step.resultSummary}
          </p>
        )}

        {step.status === "failed" && step.resultSummary && (
          <p className="text-xs text-red-400/60 mt-1 line-clamp-1">
            {step.resultSummary}
          </p>
        )}
      </div>
    </div>
  );
}

// ============================================================================
// REASONING RENDERER
// ============================================================================

function ReasoningView({ content }: { content: string }) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [content]);

  if (!content) {
    return (
      <div className="flex items-center justify-center h-full text-white/20 text-sm">
        Reasoning will appear here during execution...
      </div>
    );
  }

  // Simple markdown-like rendering
  const lines = content.split("\n");

  return (
    <div
      ref={containerRef}
      className="h-full overflow-y-auto p-4 space-y-1 text-sm font-mono"
    >
      {lines.map((line, i) => {
        if (line.startsWith("## ")) {
          return (
            <h3 key={i} className="text-white font-bold text-base mt-3 mb-1">
              {line.replace("## ", "")}
            </h3>
          );
        }
        if (line.startsWith("**") && line.endsWith("**")) {
          return (
            <p key={i} className="text-white/80 font-semibold mt-2">
              {line.replace(/\*\*/g, "")}
            </p>
          );
        }
        if (line.match(/^\d+\.\s/)) {
          return (
            <p key={i} className="text-white/50 pl-4">
              {line}
            </p>
          );
        }
        if (line.startsWith("- ")) {
          return (
            <p key={i} className="text-white/40 pl-4">
              {line}
            </p>
          );
        }
        if (line.trim() === "") {
          return <div key={i} className="h-2" />;
        }
        return (
          <p key={i} className="text-white/40">
            {line}
          </p>
        );
      })}
    </div>
  );
}

// ============================================================================
// LIVE CONTENT PREVIEW
// ============================================================================

function LiveContentView({ content }: { content: string }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [content]);

  if (!content) return null;

  return (
    <div className="border-t border-white/5 bg-white/[0.02]">
      <div className="flex items-center justify-between px-3 py-1.5">
        <div className="flex items-center gap-2">
          <div className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
          <span className="text-[10px] text-white/30 uppercase tracking-wider font-medium">
            Live Preview
          </span>
          <span className="text-[10px] text-white/15">
            {content.length.toLocaleString()} chars
          </span>
        </div>
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-[10px] text-white/20 hover:text-white/40 transition-colors"
        >
          {expanded ? "Collapse" : "Expand"}
        </button>
      </div>
      <div
        ref={containerRef}
        className="px-3 pb-2 overflow-y-auto transition-all duration-300"
        style={{ maxHeight: expanded ? "600px" : "192px" }}
      >
        <pre className="text-xs text-white/30 whitespace-pre-wrap break-words font-mono leading-relaxed">
          {content}
        </pre>
      </div>
    </div>
  );
}

// ============================================================================
// MAIN EXECUTION PANEL
// ============================================================================

export default function ExecutionPanel({
  steps,
  browserScreenshot,
  isExecuting,
  reasoning,
  liveContent,
  currentAction,
  wsUrl,
}: ExecutionPanelProps) {
  const [activeTab, setActiveTab] = useState<"steps" | "browser" | "reasoning">("steps");
  const stepsRef = useRef<HTMLDivElement>(null);

  // Auto-scroll steps
  useEffect(() => {
    if (stepsRef.current) {
      stepsRef.current.scrollTop = stepsRef.current.scrollHeight;
    }
  }, [steps]);

  // Auto-switch to browser tab when screenshot arrives
  useEffect(() => {
    if (browserScreenshot && isExecuting) {
      setActiveTab("browser");
    }
  }, [browserScreenshot, isExecuting]);

  const completedSteps = steps.filter((s) => s.status === "completed").length;
  const failedSteps = steps.filter((s) => s.status === "failed").length;

  return (
    <div className="flex flex-col h-full bg-[#0d0d1a] rounded-lg border border-white/5 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2.5 border-b border-white/5">
        <div className="flex items-center gap-2">
          {isExecuting ? (
            <div className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
          ) : completedSteps > 0 ? (
            <div className="w-2 h-2 rounded-full bg-green-400" />
          ) : (
            <div className="w-2 h-2 rounded-full bg-white/20" />
          )}
          <span className="text-xs font-medium text-white/60 uppercase tracking-wider">
            {isExecuting ? "Executing" : completedSteps > 0 ? "Complete" : "Execution Panel"}
          </span>
          {steps.length > 0 && (
            <span className="text-[10px] text-white/30 ml-1">
              {completedSteps}/{steps.length} steps
              {failedSteps > 0 && ` (${failedSteps} failed)`}
            </span>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-white/5">
        {(["steps", "browser", "reasoning"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`flex-1 py-2 text-xs font-medium transition-colors relative ${
              activeTab === tab
                ? "text-white/80"
                : "text-white/30 hover:text-white/50"
            }`}
          >
            {tab === "steps" && `Steps (${steps.length})`}
            {tab === "browser" && "Browser"}
            {tab === "reasoning" && "Reasoning"}
            {activeTab === tab && (
              <div className="absolute bottom-0 left-0 right-0 h-px bg-blue-400" />
            )}
            {tab === "browser" && browserScreenshot && (
              <span className="ml-1 w-1.5 h-1.5 rounded-full bg-green-400 inline-block" />
            )}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === "steps" && (
          <div className="h-full flex flex-col">
            <div ref={stepsRef} className="flex-1 overflow-y-auto divide-y divide-white/[0.03]">
              {steps.length === 0 ? (
                <div className="flex items-center justify-center h-full text-white/20 text-sm">
                  {isExecuting ? "Planning execution steps..." : "No steps yet"}
                </div>
              ) : (
                steps.map((step) => <StepItem key={step.id} step={step} />)
              )}
            </div>
            {liveContent && <LiveContentView content={liveContent} />}
          </div>
        )}

        {activeTab === "browser" && (
          <LiveScreen
            screenshot={browserScreenshot?.image || null}
            url={browserScreenshot?.url || ""}
            title={browserScreenshot?.title || ""}
            isActive={isExecuting}
            currentAction={currentAction}
            wsUrl={wsUrl}
          />
        )}

        {activeTab === "reasoning" && (
          <ReasoningView content={reasoning} />
        )}
      </div>
    </div>
  );
}
