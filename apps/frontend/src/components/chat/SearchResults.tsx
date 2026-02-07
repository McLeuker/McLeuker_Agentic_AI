'use client';

import React, { useState } from 'react';
import { SearchSource } from '@/lib/api';

interface SearchResultsProps {
  sources: SearchSource[];
}

export function SearchResults({ sources }: SearchResultsProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  // Extract sources from search results
  const searchSources = sources.filter(s => s.type === 'search');
  if (searchSources.length === 0) return null;

  const allSources = searchSources.flatMap(s => s.sources || []);
  const uniqueSources = [...new Set(allSources)];

  return (
    <div className="mt-4 border rounded-lg overflow-hidden bg-gray-50">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-100 transition"
      >
        <div className="flex items-center gap-2">
          <svg className="w-4 h-4 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <span className="text-sm font-medium text-gray-700">
            Sources consulted ({uniqueSources.length})
          </span>
        </div>
        <svg 
          className={`w-4 h-4 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`} 
          fill="none" 
          viewBox="0 0 24 24" 
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isExpanded && (
        <div className="px-4 py-3 border-t bg-white">
          <div className="flex flex-wrap gap-2">
            {uniqueSources.map((source, i) => (
              <span 
                key={i}
                className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full capitalize"
              >
                {source}
              </span>
            ))}
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Results from real-time search across multiple sources
          </p>
        </div>
      )}
    </div>
  );
}
