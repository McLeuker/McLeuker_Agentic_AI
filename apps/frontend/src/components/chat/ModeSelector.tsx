'use client';

import React from 'react';
import { cn } from '@/lib/utils';

/**
 * McLeuker AI V5.2 - Restructured Mode Selector
 * 
 * Each mode maps to a different backend search strategy and LLM approach:
 * - Quick: Grok fast model, minimal search (1-2 APIs), instant answers
 * - Deep Research: Kimi-2.5 thinking, all 8 APIs, file generation, quality check
 * - Agent: Multi-step agentic workflow with tool invocation and reasoning
 * - Creative: Multimodal (image/video analysis), code generation, vision-to-code
 */

export type ChatMode = 'instant' | 'thinking' | 'agent' | 'swarm' | 'research' | 'code' | 'hybrid';

interface ModeConfig {
  id: ChatMode;
  label: string;
  shortLabel: string;
  description: string;
  details: string[];
  color: string;
  bgColor: string;
  borderColor: string;
  activeGlow: string;
  icon: React.ReactNode;
  model: string;
  badge?: string;
}

const modes: ModeConfig[] = [
  {
    id: 'instant',
    label: 'Quick Search',
    shortLabel: 'Quick',
    description: 'Fast answers with real-time data',
    details: [
      'Grok-3 fast model for instant responses',
      'Top 2 search APIs (Perplexity + Google)',
      'Best for simple questions and quick lookups',
    ],
    color: 'text-emerald-400',
    bgColor: 'bg-emerald-500/10',
    borderColor: 'border-emerald-500/30',
    activeGlow: 'shadow-emerald-500/20',
    icon: (
      <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
    ),
    model: 'grok-3',
  },
  {
    id: 'research',
    label: 'Deep Research',
    shortLabel: 'Research',
    description: 'Comprehensive analysis with file generation',
    details: [
      'Kimi-2.5 reasoning with step-by-step thinking',
      'All 8 search APIs in parallel',
      'Auto-generates Excel, PDF, Word, PPT files',
      'Quality double-check with re-research loop',
    ],
    color: 'text-blue-400',
    bgColor: 'bg-blue-500/10',
    borderColor: 'border-blue-500/30',
    activeGlow: 'shadow-blue-500/20',
    icon: (
      <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="11" cy="11" r="8"/>
        <path d="M21 21l-4.35-4.35"/>
        <path d="M11 8v6M8 11h6"/>
      </svg>
    ),
    model: 'kimi-2.5',
    badge: 'Recommended',
  },
  {
    id: 'agent',
    label: 'Agent Mode',
    shortLabel: 'Agent',
    description: 'Multi-step reasoning with tool use',
    details: [
      'Agentic workflow with automatic planning',
      'Tools: web search, file analysis, code execution',
      'Multi-step task decomposition',
      'Best for complex, multi-part questions',
    ],
    color: 'text-violet-400',
    bgColor: 'bg-violet-500/10',
    borderColor: 'border-violet-500/30',
    activeGlow: 'shadow-violet-500/20',
    icon: (
      <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M12 2a4 4 0 014 4v1a4 4 0 01-8 0V6a4 4 0 014-4z"/>
        <path d="M6 21v-2a4 4 0 014-4h4a4 4 0 014 4v2"/>
        <circle cx="12" cy="7" r="1" fill="currentColor"/>
      </svg>
    ),
    model: 'kimi-2.5',
  },
  {
    id: 'code',
    label: 'Creative & Code',
    shortLabel: 'Creative',
    description: 'Image analysis, code gen, multimodal',
    details: [
      'Upload images/videos for AI analysis',
      'Vision-to-code: screenshot to React/HTML',
      'Code generation and explanation',
      'Multimodal understanding with Kimi-2.5 vision',
    ],
    color: 'text-amber-400',
    bgColor: 'bg-amber-500/10',
    borderColor: 'border-amber-500/30',
    activeGlow: 'shadow-amber-500/20',
    icon: (
      <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <polyline points="16 18 22 12 16 6"/>
        <polyline points="8 6 2 12 8 18"/>
        <line x1="12" y1="2" x2="12" y2="22" strokeDasharray="2 2"/>
      </svg>
    ),
    model: 'kimi-2.5',
  },
];

interface ModeSelectorProps {
  mode: ChatMode;
  onChange: (mode: ChatMode) => void;
  disabled?: boolean;
}

export function ModeSelector({ mode, onChange, disabled = false }: ModeSelectorProps) {
  const [isOpen, setIsOpen] = React.useState(false);
  const selectedMode = modes.find(m => m.id === mode) || modes[1];
  const containerRef = React.useRef<HTMLDivElement>(null);

  // Close on click outside
  React.useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Close on Escape
  React.useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') setIsOpen(false);
    }
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <div ref={containerRef} className="relative">
      {/* Selected Mode Button */}
      <button
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className={cn(
          'flex items-center gap-2.5 px-3.5 py-2 rounded-xl border transition-all duration-200',
          'hover:shadow-lg',
          selectedMode.bgColor,
          selectedMode.borderColor,
          isOpen && `shadow-lg ${selectedMode.activeGlow}`,
          disabled && 'opacity-50 cursor-not-allowed'
        )}
      >
        <span className={cn(selectedMode.color)}>{selectedMode.icon}</span>
        <div className="flex flex-col items-start">
          <span className={cn('text-xs font-semibold leading-tight', selectedMode.color)}>
            {selectedMode.shortLabel}
          </span>
          <span className="text-[10px] text-muted-foreground/70 leading-tight">
            {selectedMode.model}
          </span>
        </div>
        <svg
          className={cn(
            'w-3.5 h-3.5 ml-1 text-muted-foreground/50 transition-transform duration-200',
            isOpen && 'rotate-180'
          )}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute bottom-full left-0 mb-2 w-[340px] bg-popover/95 backdrop-blur-xl border border-border/50 rounded-2xl shadow-2xl overflow-hidden z-50 animate-in fade-in slide-in-from-bottom-3 duration-200">
          {/* Header */}
          <div className="px-4 pt-3 pb-2 border-b border-border/30">
            <div className="text-xs font-semibold text-foreground/80">Search Mode</div>
            <div className="text-[10px] text-muted-foreground mt-0.5">
              Choose how McLeuker AI processes your query
            </div>
          </div>

          {/* Mode Options */}
          <div className="p-2 space-y-1">
            {modes.map((m) => {
              const isSelected = mode === m.id;
              return (
                <button
                  key={m.id}
                  onClick={() => {
                    onChange(m.id);
                    setIsOpen(false);
                  }}
                  className={cn(
                    'w-full flex items-start gap-3 p-3 rounded-xl transition-all duration-150',
                    'hover:bg-accent/80',
                    isSelected && `${m.bgColor} ${m.borderColor} border`
                  )}
                >
                  {/* Icon */}
                  <div className={cn(
                    'mt-0.5 p-1.5 rounded-lg',
                    isSelected ? m.bgColor : 'bg-muted/50',
                    m.color
                  )}>
                    {m.icon}
                  </div>

                  {/* Content */}
                  <div className="flex-1 text-left min-w-0">
                    <div className="flex items-center gap-2">
                      <span className={cn('text-sm font-semibold', isSelected ? m.color : 'text-foreground')}>
                        {m.label}
                      </span>
                      {m.badge && (
                        <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-blue-500/20 text-blue-400 font-medium">
                          {m.badge}
                        </span>
                      )}
                      <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-muted/80 text-muted-foreground font-mono">
                        {m.model}
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground mt-0.5 leading-relaxed">
                      {m.description}
                    </p>
                    
                    {/* Feature list - show on hover or when selected */}
                    {isSelected && (
                      <div className="mt-2 space-y-1">
                        {m.details.map((detail, i) => (
                          <div key={i} className="flex items-start gap-1.5">
                            <svg className={cn('w-3 h-3 mt-0.5 flex-shrink-0', m.color)} viewBox="0 0 20 20" fill="currentColor">
                              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                            <span className="text-[11px] text-muted-foreground leading-tight">{detail}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Checkmark */}
                  {isSelected && (
                    <svg className={cn('w-5 h-5 mt-0.5 flex-shrink-0', m.color)} fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  )}
                </button>
              );
            })}
          </div>

          {/* Footer */}
          <div className="px-4 py-2 border-t border-border/30 bg-muted/20">
            <p className="text-[10px] text-muted-foreground/60 text-center">
              Mode affects search depth, LLM model, and output quality
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export { modes };
export default ModeSelector;
