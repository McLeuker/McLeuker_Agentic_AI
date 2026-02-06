'use client';

import React from 'react';

interface ToolIndicatorProps {
  isSearching: boolean;
  isGeneratingFile: boolean;
}

export function ToolIndicator({ isSearching, isGeneratingFile }: ToolIndicatorProps) {
  return (
    <div className="bg-blue-50 border-b border-blue-100 px-4 py-2">
      <div className="flex items-center gap-4">
        {isSearching && (
          <div className="flex items-center gap-2 text-sm text-blue-700">
            <div className="relative">
              <div className="w-4 h-4 border-2 border-blue-300 border-t-blue-600 rounded-full animate-spin" />
            </div>
            <span>Searching real-time sources...</span>
            <span className="flex gap-1">
              <span className="px-1.5 py-0.5 bg-blue-200 rounded text-xs">Perplexity</span>
              <span className="px-1.5 py-0.5 bg-blue-200 rounded text-xs">Exa</span>
              <span className="px-1.5 py-0.5 bg-blue-200 rounded text-xs">YouTube</span>
            </span>
          </div>
        )}
        
        {isGeneratingFile && (
          <div className="flex items-center gap-2 text-sm text-green-700">
            <div className="relative">
              <div className="w-4 h-4 border-2 border-green-300 border-t-green-600 rounded-full animate-spin" />
            </div>
            <span>Generating file...</span>
          </div>
        )}
      </div>
    </div>
  );
}
