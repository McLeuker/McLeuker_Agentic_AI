'use client';

import React from 'react';
import { cn } from '@/lib/utils';

export type ChatMode = 'instant' | 'thinking' | 'agent' | 'swarm' | 'research' | 'code' | 'hybrid';

interface ModeConfig {
  id: ChatMode;
  label: string;
  description: string;
  color: string;
  bgColor: string;
  borderColor: string;
  icon: string;
  model: string;
}

const modes: ModeConfig[] = [
  {
    id: 'instant',
    label: 'Instant',
    description: 'Fast responses with Grok',
    color: 'text-green-500',
    bgColor: 'bg-green-500/10',
    borderColor: 'border-green-500/30',
    icon: '⚡',
    model: 'grok'
  },
  {
    id: 'thinking',
    label: 'Thinking',
    description: 'Step-by-step reasoning with Kimi-2.5',
    color: 'text-blue-500',
    bgColor: 'bg-blue-500/10',
    borderColor: 'border-blue-500/30',
    icon: '🧠',
    model: 'kimi-k2.5'
  },
  {
    id: 'agent',
    label: 'Agent',
    description: 'Tools + search + file generation',
    color: 'text-purple-500',
    bgColor: 'bg-purple-500/10',
    borderColor: 'border-purple-500/30',
    icon: '🤖',
    model: 'kimi-k2.5'
  },
  {
    id: 'swarm',
    label: 'Swarm',
    description: '5+ parallel agents for complex tasks',
    color: 'text-orange-500',
    bgColor: 'bg-orange-500/10',
    borderColor: 'border-orange-500/30',
    icon: '🐝',
    model: 'kimi-k2.5'
  },
  {
    id: 'research',
    label: 'Research',
    description: 'Deep research with report generation',
    color: 'text-red-500',
    bgColor: 'bg-red-500/10',
    borderColor: 'border-red-500/30',
    icon: '🔬',
    model: 'hybrid'
  },
  {
    id: 'code',
    label: 'Code',
    description: 'Code generation and execution',
    color: 'text-cyan-500',
    bgColor: 'bg-cyan-500/10',
    borderColor: 'border-cyan-500/30',
    icon: '💻',
    model: 'kimi-k2.5'
  },
  {
    id: 'hybrid',
    label: 'Hybrid',
    description: 'Kimi-2.5 + Grok working together',
    color: 'text-indigo-500',
    bgColor: 'bg-indigo-500/10',
    borderColor: 'border-indigo-500/30',
    icon: '🔗',
    model: 'hybrid'
  }
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

  return (
    <div ref={containerRef} className="relative">
      {/* Selected Mode Button */}
      <button
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className={cn(
          'flex items-center gap-2 px-3 py-2 rounded-lg border transition-all duration-200',
          'hover:shadow-md',
          selectedMode.bgColor,
          selectedMode.borderColor,
          disabled && 'opacity-50 cursor-not-allowed'
        )}
      >
        <span className="text-lg">{selectedMode.icon}</span>
        <div className="flex flex-col items-start">
          <span className={cn('text-xs font-medium', selectedMode.color)}>
            {selectedMode.label}
          </span>
          <span className="text-[10px] text-muted-foreground">
            {selectedMode.model}
          </span>
        </div>
        <svg
          className={cn(
            'w-4 h-4 ml-2 text-muted-foreground transition-transform',
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
        <div className="absolute bottom-full left-0 mb-2 w-72 bg-popover border rounded-xl shadow-lg overflow-hidden z-50 animate-in fade-in slide-in-from-bottom-2">
          <div className="p-2">
            <div className="text-xs font-medium text-muted-foreground px-2 py-1">
              Select Mode
            </div>
            {modes.map((m) => (
              <button
                key={m.id}
                onClick={() => {
                  onChange(m.id);
                  setIsOpen(false);
                }}
                className={cn(
                  'w-full flex items-start gap-3 p-2 rounded-lg transition-all duration-200',
                  'hover:bg-accent',
                  mode === m.id && m.bgColor
                )}
              >
                <span className="text-xl mt-0.5">{m.icon}</span>
                <div className="flex-1 text-left">
                  <div className="flex items-center gap-2">
                    <span className={cn('font-medium', m.color)}>{m.label}</span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-muted text-muted-foreground">
                      {m.model}
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    {m.description}
                  </p>
                </div>
                {mode === m.id && (
                  <svg className={cn('w-5 h-5 mt-0.5', m.color)} fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                )}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export { modes };
export default ModeSelector;
