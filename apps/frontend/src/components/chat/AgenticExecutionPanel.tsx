'use client';

import React, { useState, useMemo } from 'react';
import { cn } from '@/lib/utils';
import {
  CheckCircle2,
  Circle,
  Loader2,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  Globe,
  Brain,
  Search,
  FileText,
  Code2,
  Sparkles,
  Pause,
  Play,
  X,
  Download,
  ExternalLink,
} from 'lucide-react';
import type { ExecutionStep, ExecutionArtifact } from '@/lib/agenticAPI';

// ============================================================================
// TYPES
// ============================================================================

interface AgenticExecutionPanelProps {
  steps: ExecutionStep[];
  status: 'idle' | 'planning' | 'executing' | 'paused' | 'completed' | 'error';
  progress: number;
  content: string;
  reasoning: string;
  artifacts: ExecutionArtifact[];
  error: string | null;
  onPause?: () => void;
  onResume?: () => void;
  onCancel?: () => void;
  className?: string;
}

// ============================================================================
// HELPER COMPONENTS
// ============================================================================

function PhaseIcon({ phase, className }: { phase: string; className?: string }) {
  switch (phase) {
    case 'planning':
      return <Brain className={cn('h-4 w-4', className)} />;
    case 'research':
      return <Search className={cn('h-4 w-4', className)} />;
    case 'execution':
      return <Code2 className={cn('h-4 w-4', className)} />;
    case 'verification':
      return <Globe className={cn('h-4 w-4', className)} />;
    case 'delivery':
      return <Sparkles className={cn('h-4 w-4', className)} />;
    default:
      return <FileText className={cn('h-4 w-4', className)} />;
  }
}

function StatusIcon({ status }: { status: string }) {
  switch (status) {
    case 'complete':
      return <CheckCircle2 className="h-4 w-4 text-emerald-400" />;
    case 'active':
      return <Loader2 className="h-4 w-4 text-blue-400 animate-spin" />;
    case 'error':
      return <AlertCircle className="h-4 w-4 text-red-400" />;
    case 'skipped':
      return <Circle className="h-4 w-4 text-white/20" />;
    default:
      return <Circle className="h-4 w-4 text-white/30" />;
  }
}

function phaseColor(phase: string): string {
  switch (phase) {
    case 'planning': return 'text-violet-400';
    case 'research': return 'text-blue-400';
    case 'execution': return 'text-amber-400';
    case 'verification': return 'text-emerald-400';
    case 'delivery': return 'text-[#7a8a6e]';
    default: return 'text-white/60';
  }
}

function phaseBg(phase: string): string {
  switch (phase) {
    case 'planning': return 'bg-violet-500/10 border-violet-500/20';
    case 'research': return 'bg-blue-500/10 border-blue-500/20';
    case 'execution': return 'bg-amber-500/10 border-amber-500/20';
    case 'verification': return 'bg-emerald-500/10 border-emerald-500/20';
    case 'delivery': return 'bg-[#2E3524]/30 border-[#5c6652]/30';
    default: return 'bg-white/5 border-white/10';
  }
}

// ============================================================================
// STEP ITEM COMPONENT
// ============================================================================

function StepItem({ step }: { step: ExecutionStep }) {
  const [expanded, setExpanded] = useState(step.status === 'active');
  const hasDetails = !!(step.detail || (step.subSteps && step.subSteps.length > 0) || (step.artifacts && step.artifacts.length > 0));

  return (
    <div className={cn(
      'border rounded-lg transition-all duration-200',
      step.status === 'active' ? phaseBg(step.phase) : 'border-white/[0.06] bg-white/[0.02]',
      step.status === 'complete' && 'opacity-80'
    )}>
      <button
        onClick={() => hasDetails && setExpanded(!expanded)}
        className="w-full flex items-center gap-3 px-3 py-2.5 text-left"
      >
        <StatusIcon status={step.status} />
        <PhaseIcon phase={step.phase} className={phaseColor(step.phase)} />
        <div className="flex-1 min-w-0">
          <div className={cn(
            'text-sm font-medium',
            step.status === 'active' ? 'text-white/90' : 'text-white/60'
          )}>
            {step.title}
          </div>
          {step.status === 'active' && step.detail && (
            <div className="text-xs text-white/40 mt-0.5 truncate">
              {step.detail}
            </div>
          )}
        </div>
        {step.progress !== undefined && step.status === 'active' && (
          <span className="text-[10px] text-white/30 font-mono flex-shrink-0">
            {Math.round(step.progress)}%
          </span>
        )}
        {hasDetails && (
          <div className="flex-shrink-0">
            {expanded ? (
              <ChevronUp className="h-3.5 w-3.5 text-white/30" />
            ) : (
              <ChevronDown className="h-3.5 w-3.5 text-white/30" />
            )}
          </div>
        )}
      </button>

      {/* Expanded details */}
      {expanded && hasDetails && (
        <div className="px-3 pb-3 space-y-2">
          {step.detail && step.status !== 'active' && (
            <p className="text-xs text-white/40 pl-11">{step.detail}</p>
          )}

          {/* Sub-steps */}
          {step.subSteps && step.subSteps.length > 0 && (
            <div className="pl-11 space-y-1">
              {step.subSteps.map((sub, i) => (
                <div key={i} className="flex items-center gap-2">
                  <div className={cn(
                    'w-1.5 h-1.5 rounded-full flex-shrink-0',
                    sub.status === 'complete' ? 'bg-emerald-400' :
                    sub.status === 'active' ? 'bg-blue-400 animate-pulse' :
                    'bg-white/20'
                  )} />
                  <span className="text-[11px] text-white/40">{sub.label}</span>
                </div>
              ))}
            </div>
          )}

          {/* Artifacts */}
          {step.artifacts && step.artifacts.length > 0 && (
            <div className="pl-11 flex flex-wrap gap-1.5">
              {step.artifacts.map((artifact, i) => (
                <div
                  key={i}
                  className="flex items-center gap-1.5 px-2 py-1 bg-white/[0.04] border border-white/[0.08] rounded-md"
                >
                  {artifact.type === 'file' && <FileText className="h-3 w-3 text-white/40" />}
                  {artifact.type === 'code' && <Code2 className="h-3 w-3 text-white/40" />}
                  {artifact.type === 'url' && <ExternalLink className="h-3 w-3 text-white/40" />}
                  <span className="text-[10px] text-white/50">{artifact.name}</span>
                  {artifact.url && (
                    <a
                      href={artifact.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-400 hover:text-blue-300"
                    >
                      <Download className="h-3 w-3" />
                    </a>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ============================================================================
// MAIN PANEL COMPONENT
// ============================================================================

export function AgenticExecutionPanel({
  steps,
  status,
  progress,
  content,
  reasoning,
  artifacts,
  error,
  onPause,
  onResume,
  onCancel,
  className,
}: AgenticExecutionPanelProps) {
  const [showReasoning, setShowReasoning] = useState(false);

  // Group steps by phase
  const groupedSteps = useMemo(() => {
    const groups: Record<string, ExecutionStep[]> = {};
    for (const step of steps) {
      if (!groups[step.phase]) groups[step.phase] = [];
      groups[step.phase].push(step);
    }
    return groups;
  }, [steps]);

  const phaseOrder = ['planning', 'research', 'execution', 'verification', 'delivery'];
  const isRunning = status === 'planning' || status === 'executing';
  const isPaused = status === 'paused';

  if (status === 'idle' && steps.length === 0) return null;

  return (
    <div className={cn(
      'flex flex-col h-full bg-[#0f0f0f] border-l border-white/[0.06]',
      className
    )}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/[0.06]">
        <div className="flex items-center gap-2.5">
          <div className={cn(
            'w-2 h-2 rounded-full',
            isRunning ? 'bg-blue-400 animate-pulse' :
            isPaused ? 'bg-amber-400' :
            status === 'completed' ? 'bg-emerald-400' :
            status === 'error' ? 'bg-red-400' :
            'bg-white/30'
          )} />
          <span className="text-sm font-medium text-white/80">
            {status === 'planning' ? 'Planning...' :
             status === 'executing' ? 'Executing...' :
             status === 'paused' ? 'Paused' :
             status === 'completed' ? 'Completed' :
             status === 'error' ? 'Error' :
             'Agent Execution'}
          </span>
        </div>

        <div className="flex items-center gap-1.5">
          {isRunning && onPause && (
            <button
              onClick={onPause}
              className="p-1.5 rounded-lg hover:bg-white/[0.06] text-white/40 hover:text-white/70 transition"
              title="Pause"
            >
              <Pause className="h-3.5 w-3.5" />
            </button>
          )}
          {isPaused && onResume && (
            <button
              onClick={onResume}
              className="p-1.5 rounded-lg hover:bg-white/[0.06] text-white/40 hover:text-white/70 transition"
              title="Resume"
            >
              <Play className="h-3.5 w-3.5" />
            </button>
          )}
          {(isRunning || isPaused) && onCancel && (
            <button
              onClick={onCancel}
              className="p-1.5 rounded-lg hover:bg-red-500/10 text-white/40 hover:text-red-400 transition"
              title="Cancel"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Progress bar */}
      {(isRunning || isPaused) && (
        <div className="h-1 bg-white/[0.04]">
          <div
            className={cn(
              'h-full transition-all duration-700 ease-out rounded-r',
              isPaused ? 'bg-amber-500/60' : 'bg-gradient-to-r from-blue-500 to-[#5c6652]'
            )}
            style={{ width: `${Math.max(progress, 2)}%` }}
          />
        </div>
      )}

      {/* Steps list */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {phaseOrder.map((phase) => {
          const phaseSteps = groupedSteps[phase];
          if (!phaseSteps || phaseSteps.length === 0) return null;

          return (
            <div key={phase} className="space-y-1.5">
              <div className="flex items-center gap-2 px-1 pt-1">
                <PhaseIcon phase={phase} className={cn('h-3 w-3', phaseColor(phase))} />
                <span className={cn('text-[10px] font-semibold uppercase tracking-wider', phaseColor(phase))}>
                  {phase}
                </span>
              </div>
              {phaseSteps.map((step) => (
                <StepItem key={step.id} step={step} />
              ))}
            </div>
          );
        })}

        {/* Error display */}
        {error && (
          <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20">
            <div className="flex items-center gap-2 mb-1">
              <AlertCircle className="h-4 w-4 text-red-400" />
              <span className="text-sm font-medium text-red-400">Error</span>
            </div>
            <p className="text-xs text-red-300/70 pl-6">{error}</p>
          </div>
        )}
      </div>

      {/* Reasoning toggle */}
      {reasoning && (
        <div className="border-t border-white/[0.06]">
          <button
            onClick={() => setShowReasoning(!showReasoning)}
            className="w-full flex items-center justify-between px-4 py-2 text-xs text-white/40 hover:text-white/60 transition"
          >
            <span className="flex items-center gap-1.5">
              <Brain className="h-3 w-3" />
              Reasoning
            </span>
            {showReasoning ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
          </button>
          {showReasoning && (
            <div className="px-4 pb-3 max-h-40 overflow-y-auto">
              <p className="text-[11px] text-white/30 leading-relaxed whitespace-pre-wrap">
                {reasoning}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Artifacts footer */}
      {artifacts.length > 0 && (
        <div className="border-t border-white/[0.06] px-4 py-2.5">
          <p className="text-[10px] text-white/30 uppercase tracking-wider mb-2">
            Artifacts ({artifacts.length})
          </p>
          <div className="flex flex-wrap gap-1.5">
            {artifacts.map((artifact, i) => (
              <a
                key={i}
                href={artifact.url || '#'}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1.5 px-2.5 py-1.5 bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] hover:border-white/[0.14] rounded-lg transition text-[11px] text-white/50 hover:text-white/80"
              >
                {artifact.type === 'file' && <FileText className="h-3 w-3" />}
                {artifact.type === 'code' && <Code2 className="h-3 w-3" />}
                {artifact.type === 'url' && <ExternalLink className="h-3 w-3" />}
                <span className="truncate max-w-[120px]">{artifact.name}</span>
                <Download className="h-3 w-3 flex-shrink-0" />
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default AgenticExecutionPanel;
