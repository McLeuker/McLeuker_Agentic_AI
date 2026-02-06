'use client';

import React from 'react';
import { ChatMode } from './ChatInterface';

interface ModeSelectorProps {
  mode: ChatMode;
  onChange: (mode: ChatMode) => void;
}

const modes: { id: ChatMode; label: string; description: string; color: string }[] = [
  { 
    id: 'instant', 
    label: 'Instant', 
    description: 'Quick responses, no reasoning',
    color: 'bg-green-500'
  },
  { 
    id: 'thinking', 
    label: 'Thinking', 
    description: 'Step-by-step reasoning shown',
    color: 'bg-blue-500'
  },
  { 
    id: 'agent', 
    label: 'Agent', 
    description: 'Tools + real-time search',
    color: 'bg-purple-500'
  },
  { 
    id: 'swarm', 
    label: 'Swarm', 
    description: '5-20 parallel agents',
    color: 'bg-orange-500'
  },
  { 
    id: 'research', 
    label: 'Research', 
    description: 'Deep research + reports',
    color: 'bg-red-500'
  }
];

export function ModeSelector({ mode, onChange }: ModeSelectorProps) {
  const [isOpen, setIsOpen] = React.useState(false);
  const currentMode = modes.find(m => m.id === mode);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border hover:bg-gray-50 transition ${
          currentMode?.color.replace('bg-', 'border-')
        }`}
      >
        <span className={`w-2 h-2 rounded-full ${currentMode?.color}`} />
        <span className="text-sm font-medium">{currentMode?.label}</span>
        <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <>
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setIsOpen(false)} 
          />
          <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-lg border z-20 py-1">
            {modes.map((m) => (
              <button
                key={m.id}
                onClick={() => {
                  onChange(m.id);
                  setIsOpen(false);
                }}
                className={`w-full px-4 py-3 text-left hover:bg-gray-50 flex items-start gap-3 ${
                  mode === m.id ? 'bg-blue-50' : ''
                }`}
              >
                <span className={`w-2 h-2 rounded-full mt-1.5 ${m.color}`} />
                <div>
                  <div className="font-medium text-sm">{m.label}</div>
                  <div className="text-xs text-gray-500">{m.description}</div>
                </div>
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
