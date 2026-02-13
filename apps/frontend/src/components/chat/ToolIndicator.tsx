'use client';

import React from 'react';

interface ToolIndicatorProps {
  isSearching: boolean;
  isGeneratingFile: boolean;
  isExecutingCode: boolean;
}

export function ToolIndicator({ isSearching, isGeneratingFile, isExecutingCode }: ToolIndicatorProps) {
  const activeTools = [];
  
  if (isSearching) {
    activeTools.push({
      name: 'Searching',
      icon: '🔍',
      color: 'bg-blue-50 text-blue-700 border-blue-200',
      sources: ['Perplexity', 'Exa', 'YouTube', 'Grok']
    });
  }
  
  if (isGeneratingFile) {
    activeTools.push({
      name: 'Generating File',
      icon: '📄',
      color: 'bg-green-50 text-green-700 border-green-200',
      sources: []
    });
  }
  
  if (isExecutingCode) {
    activeTools.push({
      name: 'Executing Code',
      icon: '💻',
      color: 'bg-purple-50 text-purple-700 border-purple-200',
      sources: []
    });
  }

  if (activeTools.length === 0) return null;

  return (
    <div className="bg-white border-b px-4 py-3">
      <div className="flex flex-wrap gap-3">
        {activeTools.map((tool, i) => (
          <div 
            key={i}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg border ${tool.color}`}
          >
            <span className="text-lg">{tool.icon}</span>
            <div>
              <span className="text-sm font-medium">{tool.name}</span>
              {tool.sources.length > 0 && (
                <div className="flex gap-1 mt-0.5">
                  {tool.sources.map((source, j) => (
                    <span key={j} className="text-xs px-1.5 py-0.5 bg-white/50 rounded">
                      {source}
                    </span>
                  ))}
                </div>
              )}
            </div>
            <div className="ml-2 flex gap-1">
              <span className="w-1.5 h-1.5 bg-current rounded-full animate-pulse" />
              <span className="w-1.5 h-1.5 bg-current rounded-full animate-pulse delay-75" />
              <span className="w-1.5 h-1.5 bg-current rounded-full animate-pulse delay-150" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
