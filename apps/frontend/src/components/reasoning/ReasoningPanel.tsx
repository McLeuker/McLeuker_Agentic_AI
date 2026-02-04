'use client';

import { useState, useEffect, useRef } from 'react';
import { cn } from '@/lib/utils';
import {
  Brain,
  Search,
  Sparkles,
  CheckCircle2,
  Circle,
  Loader2,
  ChevronRight,
  ChevronDown,
  Lightbulb,
  FileText,
  ExternalLink,
  X,
  Minimize2,
  Maximize2
} from 'lucide-react';

// =============================================================================
// Types
// =============================================================================

export interface ThinkingEvent {
  type: 'thinking';
  data: {
    thought: string;
    detail?: string;
    phase?: string;
  };
  timestamp: string;
}

export interface PlanningEvent {
  type: 'planning';
  data: {
    goal: string;
    mode: string;
    intent: string;
    domain: string;
    steps: TaskStep[];
    estimated_time: string;
  };
  timestamp: string;
}

export interface TaskStep {
  step_id: number;
  step_type: string;
  title: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
}

export interface TaskUpdateEvent {
  type: 'task_update';
  data: {
    step_id?: number;
    task_id?: string;
    status: string;
    title: string;
    description?: string;
    progress?: number;
  };
  timestamp: string;
}

export interface SearchingEvent {
  type: 'searching';
  data: {
    status: string;
    message: string;
    sources_target?: number;
    sources_found?: number;
  };
  timestamp: string;
}

export interface SourceEvent {
  type: 'source';
  data: {
    title: string;
    url: string;
    snippet?: string;
    relevance: number;
  };
  timestamp: string;
}

export interface ProgressEvent {
  type: 'progress';
  data: {
    message: string;
    percentage: number;
  };
  timestamp: string;
}

export interface InsightEvent {
  type: 'insight';
  data: {
    icon?: string;
    title: string;
    description: string;
    importance: string;
  };
  timestamp: string;
}

export type StreamEvent = 
  | ThinkingEvent 
  | PlanningEvent 
  | TaskUpdateEvent 
  | SearchingEvent 
  | SourceEvent 
  | ProgressEvent 
  | InsightEvent
  | { type: 'analyzing' | 'generating' | 'complete' | 'error'; data: any; timestamp: string };

// =============================================================================
// ReasoningPanel Component
// =============================================================================

interface ReasoningPanelProps {
  events: StreamEvent[];
  isStreaming: boolean;
  onClose?: () => void;
  className?: string;
}

export function ReasoningPanel({ 
  events, 
  isStreaming, 
  onClose,
  className 
}: ReasoningPanelProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [showThoughts, setShowThoughts] = useState(true);
  const scrollRef = useRef<HTMLDivElement>(null);
  
  // Auto-scroll to bottom when new events arrive
  useEffect(() => {
    if (scrollRef.current && isStreaming) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [events, isStreaming]);
  
  // Extract different event types
  const thoughts = events.filter(e => e.type === 'thinking') as ThinkingEvent[];
  const planningEvent = events.find(e => e.type === 'planning') as PlanningEvent | undefined;
  const taskUpdates = events.filter(e => e.type === 'task_update') as TaskUpdateEvent[];
  const sources = events.filter(e => e.type === 'source') as SourceEvent[];
  const insights = events.filter(e => e.type === 'insight') as InsightEvent[];
  const progressEvents = events.filter(e => e.type === 'progress') as ProgressEvent[];
  
  // Get current progress
  const latestProgress = progressEvents[progressEvents.length - 1];
  const currentProgress = latestProgress?.data.percentage || 0;
  
  // Get task steps with updated statuses
  const taskSteps = planningEvent?.data.steps.map(step => {
    const update = taskUpdates.find(u => u.data.step_id === step.step_id);
    return {
      ...step,
      status: update?.data.status as TaskStep['status'] || step.status
    };
  }) || [];
  
  // Get current step
  const currentStep = taskSteps.find(s => s.status === 'in_progress');
  const completedSteps = taskSteps.filter(s => s.status === 'completed').length;
  
  if (!isExpanded) {
    return (
      <div className={cn(
        "fixed bottom-24 right-6 z-50",
        "bg-[#1A1A1A] border border-white/10 rounded-xl shadow-2xl",
        "p-3 cursor-pointer hover:bg-[#222]",
        "transition-all duration-200",
        className
      )}
      onClick={() => setIsExpanded(true)}
      >
        <div className="flex items-center gap-3">
          <div className="relative">
            <Brain className="h-5 w-5 text-purple-400" />
            {isStreaming && (
              <span className="absolute -top-1 -right-1 h-2 w-2 bg-green-500 rounded-full animate-pulse" />
            )}
          </div>
          <span className="text-sm text-white/80">
            {isStreaming ? 'AI is thinking...' : 'View reasoning'}
          </span>
          <Maximize2 className="h-4 w-4 text-white/40" />
        </div>
      </div>
    );
  }
  
  return (
    <div className={cn(
      "bg-gradient-to-b from-[#1A1A1A] to-[#141414]",
      "border border-white/10 rounded-xl shadow-2xl",
      "flex flex-col overflow-hidden",
      "w-full max-w-md",
      className
    )}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/10 bg-[#1A1A1A]">
        <div className="flex items-center gap-2">
          <Brain className="h-5 w-5 text-purple-400" />
          <span className="font-medium text-white text-sm">AI Reasoning</span>
          {isStreaming && (
            <span className="flex items-center gap-1 text-xs text-green-400">
              <span className="h-1.5 w-1.5 bg-green-400 rounded-full animate-pulse" />
              Live
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsExpanded(false)}
            className="p-1.5 text-white/40 hover:text-white/80 hover:bg-white/10 rounded-lg transition-colors"
          >
            <Minimize2 className="h-4 w-4" />
          </button>
          {onClose && (
            <button
              onClick={onClose}
              className="p-1.5 text-white/40 hover:text-white/80 hover:bg-white/10 rounded-lg transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>
      
      {/* Progress Bar */}
      {isStreaming && (
        <div className="px-4 py-2 border-b border-white/5">
          <div className="flex items-center justify-between text-xs text-white/50 mb-1">
            <span>{currentStep?.title || 'Processing...'}</span>
            <span>{currentProgress}%</span>
          </div>
          <div className="h-1 bg-white/10 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-purple-500 to-blue-500 transition-all duration-300"
              style={{ width: `${currentProgress}%` }}
            />
          </div>
        </div>
      )}
      
      {/* Content */}
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-4 space-y-4 max-h-[400px]"
      >
        {/* Goal */}
        {planningEvent && (
          <div className="bg-white/5 rounded-lg p-3">
            <div className="flex items-center gap-2 text-xs text-white/50 mb-1">
              <Sparkles className="h-3.5 w-3.5" />
              Goal
            </div>
            <p className="text-sm text-white/90">{planningEvent.data.goal}</p>
          </div>
        )}
        
        {/* Task Steps */}
        {taskSteps.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs text-white/50 uppercase tracking-wider">Task Progress</span>
              <span className="text-xs text-white/50">{completedSteps}/{taskSteps.length}</span>
            </div>
            {taskSteps.map((step, index) => (
              <TaskStepItem key={step.step_id} step={step} index={index} />
            ))}
          </div>
        )}
        
        {/* Thinking Process */}
        {thoughts.length > 0 && (
          <div className="space-y-2">
            <button
              onClick={() => setShowThoughts(!showThoughts)}
              className="flex items-center gap-2 text-xs text-white/50 uppercase tracking-wider hover:text-white/70"
            >
              {showThoughts ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
              Thinking ({thoughts.length})
            </button>
            {showThoughts && (
              <div className="space-y-2 pl-4 border-l border-white/10">
                {thoughts.slice(-5).map((thought, index) => (
                  <ThoughtItem key={index} thought={thought} />
                ))}
              </div>
            )}
          </div>
        )}
        
        {/* Sources Found */}
        {sources.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-xs text-white/50 uppercase tracking-wider">
              <Search className="h-3 w-3" />
              Sources Found ({sources.length})
            </div>
            <div className="space-y-1">
              {sources.slice(0, 5).map((source, index) => (
                <SourceItem key={index} source={source} />
              ))}
            </div>
          </div>
        )}
        
        {/* Insights Discovered */}
        {insights.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-xs text-white/50 uppercase tracking-wider">
              <Lightbulb className="h-3 w-3" />
              Insights ({insights.length})
            </div>
            <div className="space-y-2">
              {insights.map((insight, index) => (
                <InsightItem key={index} insight={insight} />
              ))}
            </div>
          </div>
        )}
        
        {/* Empty State */}
        {events.length === 0 && (
          <div className="text-center py-8">
            <Brain className="h-8 w-8 text-white/20 mx-auto mb-2" />
            <p className="text-sm text-white/40">Waiting for AI reasoning...</p>
          </div>
        )}
      </div>
      
      {/* Footer */}
      {planningEvent && (
        <div className="px-4 py-2 border-t border-white/10 bg-[#1A1A1A]">
          <div className="flex items-center justify-between text-xs text-white/40">
            <span>Mode: {planningEvent.data.mode}</span>
            <span>Est. {planningEvent.data.estimated_time}</span>
          </div>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Sub-components
// =============================================================================

function TaskStepItem({ step, index }: { step: TaskStep; index: number }) {
  const getStatusIcon = () => {
    switch (step.status) {
      case 'completed':
        return <CheckCircle2 className="h-4 w-4 text-green-400" />;
      case 'in_progress':
        return <Loader2 className="h-4 w-4 text-blue-400 animate-spin" />;
      case 'failed':
        return <X className="h-4 w-4 text-red-400" />;
      default:
        return <Circle className="h-4 w-4 text-white/20" />;
    }
  };
  
  const getStepIcon = () => {
    switch (step.step_type) {
      case 'thinking':
        return <Brain className="h-3.5 w-3.5" />;
      case 'searching':
        return <Search className="h-3.5 w-3.5" />;
      case 'analyzing':
        return <FileText className="h-3.5 w-3.5" />;
      case 'generating':
        return <Sparkles className="h-3.5 w-3.5" />;
      default:
        return <Circle className="h-3.5 w-3.5" />;
    }
  };
  
  return (
    <div className={cn(
      "flex items-start gap-3 p-2 rounded-lg transition-colors",
      step.status === 'in_progress' && "bg-blue-500/10 border border-blue-500/20",
      step.status === 'completed' && "opacity-60"
    )}>
      {getStatusIcon()}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className={cn(
            "text-sm font-medium",
            step.status === 'in_progress' ? "text-white" : "text-white/70"
          )}>
            {step.title}
          </span>
          <span className="text-white/30">{getStepIcon()}</span>
        </div>
        <p className="text-xs text-white/40 truncate">{step.description}</p>
      </div>
    </div>
  );
}

function ThoughtItem({ thought }: { thought: ThinkingEvent }) {
  return (
    <div className="text-sm text-white/60 py-1">
      <span className="text-purple-400/80">💭</span>{' '}
      {thought.data.thought}
    </div>
  );
}

function SourceItem({ source }: { source: SourceEvent }) {
  return (
    <a
      href={source.data.url}
      target="_blank"
      rel="noopener noreferrer"
      className="flex items-center gap-2 p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors group"
    >
      <div className="flex-1 min-w-0">
        <p className="text-xs text-white/80 truncate group-hover:text-white">
          {source.data.title}
        </p>
      </div>
      <ExternalLink className="h-3 w-3 text-white/30 group-hover:text-white/60 flex-shrink-0" />
    </a>
  );
}

function InsightItem({ insight }: { insight: InsightEvent }) {
  return (
    <div className={cn(
      "p-2 rounded-lg",
      insight.data.importance === 'high' ? "bg-yellow-500/10" : "bg-white/5"
    )}>
      <div className="flex items-start gap-2">
        <span className="text-sm">{insight.data.icon || '💡'}</span>
        <div>
          <p className="text-xs font-medium text-white/90">{insight.data.title}</p>
          <p className="text-xs text-white/50">{insight.data.description}</p>
        </div>
      </div>
    </div>
  );
}

export default ReasoningPanel;
