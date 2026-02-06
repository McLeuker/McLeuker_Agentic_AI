'use client';

import React from 'react';
import { SearchSource } from '@/lib/api';

interface SearchSourcesPanelProps {
  sources: SearchSource[];
  onClose: () => void;
}

export function SearchSourcesPanel({ sources, onClose }: SearchSourcesPanelProps) {
  const searchSources = sources.filter(s => s.type === 'search');
  const allSources = searchSources.flatMap(s => s.sources || []);
  const uniqueSources = [...new Set(allSources)];

  const sourceInfo: Record<string, { name: string; description: string; color: string }> = {
    'perplexity': { 
      name: 'Perplexity AI', 
      description: 'Real-time web search with AI synthesis',
      color: 'bg-teal-100 text-teal-700'
    },
    'exa': { 
      name: 'Exa', 
      description: 'Neural search engine',
      color: 'bg-indigo-100 text-indigo-700'
    },
    'youtube': { 
      name: 'YouTube', 
      description: 'Video content search',
      color: 'bg-red-100 text-red-700'
    },
    'grok': { 
      name: 'Grok/X AI', 
      description: 'X/Twitter real-time data',
      color: 'bg-gray-100 text-gray-700'
    }
  };

  return (
    <div className="fixed right-0 top-16 bottom-0 w-80 bg-white border-l shadow-xl z-30 overflow-y-auto">
      <div className="sticky top-0 bg-white border-b px-4 py-3 flex items-center justify-between">
        <div>
          <h3 className="font-semibold text-gray-900">Search Sources</h3>
          <p className="text-xs text-gray-500">{uniqueSources.length} source(s) consulted</p>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div className="p-4 space-y-3">
        {uniqueSources.map((source, i) => {
          const info = sourceInfo[source] || { 
            name: source, 
            description: 'Search source',
            color: 'bg-gray-100 text-gray-700'
          };
          
          return (
            <div key={i} className="p-3 rounded-lg border hover:shadow-sm transition">
              <div className={`inline-block px-2 py-1 rounded text-xs font-medium mb-2 ${info.color}`}>
                {info.name}
              </div>
              <p className="text-sm text-gray-600">{info.description}</p>
            </div>
          );
        })}
      </div>

      <div className="p-4 border-t bg-gray-50">
        <p className="text-xs text-gray-500">
          Results are synthesized from multiple real-time sources to provide accurate, up-to-date information.
        </p>
      </div>
    </div>
  );
}
