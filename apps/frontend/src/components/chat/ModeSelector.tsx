'use client';

import React from 'react';
import { ChatMode } from '@/lib/api';

interface ModeSelectorProps {
  mode: ChatMode;
  onChange: (mode: ChatMode) => void;
}

const modes: { 
  id: ChatMode; 
  label: string; 
  description: string; 
  color: string;
  icon: string;
}[] = [
  { 
    id: 'instant', 
    label: 'Instant', 
    description: 'Fast responses, no reasoning shown',
    color: 'bg-green-500',
    icon: '⚡'
  },
  { 
    id: 'thinking', 
    label: 'Thinking', 
    description: 'Step-by-step reasoning visible',
    color: 'bg-blue-500',
    icon: '🧠'
  },
  { 
    id: 'agent', 
    label: 'Agent', 
    description: 'Tools + real-time search + file gen',
    color: 'bg-purple-500',
    icon: '🤖'
  },
  { 
    id: 'swarm', 
    label: 'Swarm', 
    description: '5-50 parallel agents for complex tasks',
    color: 'bg-orange-500',
    icon: '🐝'
  },
  { 
    id: 'research', 
    label: 'Research', 
    description: 'Deep research with report generation',
    color: 'bg-red-500',
    icon: '🔬'
  },
  { 
    id: 'code', 
    label: 'Code', 
    description: 'Code generation and execution',
    color: 'bg-gray-700',
    icon: '💻'
  }
];

export function ModeSelector({ mode, onChange }: ModeSelectorProps) {
  const [isOpen, setIsOpen] = React.useState(false);
  const currentMode = modes.find(m => m.id === mode);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`flex items-center gap-2 px-3 py-2 rounded-lg border-2 bg-white hover:bg-gray-50 transition ${
          currentMode?.color.replace('bg-', 'border-')
        }`}
      >
        <span>{currentMode?.icon}</span>
        <span className="text-sm font-medium hidden sm:inline">{currentMode?.label}</span>
        <svg className={`w-4 h-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <>
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setIsOpen(false)} 
          />
          <div className="absolute right-0 mt-2 w-72 bg-white rounded-xl shadow-xl border z-20 py-2">
            <div className="px-3 py-2 border-b">
              <p className="text-xs text-gray-500 font-medium">Select Mode</p>
            </div>
            {modes.map((m) => (
              <button
                key={m.id}
                onClick={() => {
                  onChange(m.id);
                  setIsOpen(false);
                }}
                className={`w-full px-4 py-3 text-left hover:bg-gray-50 flex items-start gap-3 transition ${
                  mode === m.id ? 'bg-blue-50' : ''
                }`}
              >
                <span className="text-xl">{m.icon}</span>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-sm">{m.label}</span>
                    {mode === m.id && (
                      <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">Active</span>
                    )}
                  </div>
                  <div className="text-xs text-gray-500 mt-0.5">{m.description}</div>
                </div>
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
