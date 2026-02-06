'use client';

import React, { useState } from 'react';

interface SearchResultsProps {
  results: any[];
}

export function SearchResults({ results }: SearchResultsProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const perplexityResult = results.find(r => r.results?.sources?.perplexity);
  const exaResult = results.find(r => r.results?.sources?.exa);
  const youtubeResult = results.find(r => r.results?.sources?.youtube);

  return (
    <div className="mt-3 border rounded-lg overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-3 py-2 bg-gray-50 hover:bg-gray-100 flex items-center justify-between text-sm"
      >
        <span className="flex items-center gap-2">
          <svg className="w-4 h-4 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          Sources searched
        </span>
        <svg 
          className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-180' : ''}`} 
          fill="none" 
          viewBox="0 0 24 24" 
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isExpanded && (
        <div className="p-3 space-y-3 text-sm">
          {perplexityResult?.results?.sources?.perplexity && (
            <div>
              <h4 className="font-medium text-purple-700 mb-1">Perplexity AI</h4>
              <p className="text-gray-600 text-xs">
                {perplexityResult.results.sources.perplexity.answer?.substring(0, 200)}...
              </p>
              {perplexityResult.results.sources.perplexity.citations && (
                <div className="mt-1 flex flex-wrap gap-1">
                  {perplexityResult.results.sources.perplexity.citations.slice(0, 3).map((cite: string, i: number) => (
                    <a 
                      key={i} 
                      href={cite} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-xs text-blue-600 hover:underline truncate max-w-[150px]"
                    >
                      Source {i + 1}
                    </a>
                  ))}
                </div>
              )}
            </div>
          )}

          {exaResult?.results?.sources?.exa?.results && (
            <div>
              <h4 className="font-medium text-green-700 mb-1">Web Search</h4>
              <ul className="space-y-1">
                {exaResult.results.sources.exa.results.slice(0, 3).map((result: any, i: number) => (
                  <li key={i} className="text-xs">
                    <a 
                      href={result.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline"
                    >
                      {result.title}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {youtubeResult?.results?.sources?.youtube?.videos && (
            <div>
              <h4 className="font-medium text-red-700 mb-1">YouTube</h4>
              <div className="grid grid-cols-2 gap-2">
                {youtubeResult.results.sources.youtube.videos.slice(0, 2).map((video: any, i: number) => (
                  <a 
                    key={i}
                    href={video.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block group"
                  >
                    <img 
                      src={video.thumbnail} 
                      alt={video.title}
                      className="w-full h-20 object-cover rounded group-hover:opacity-80 transition"
                    />
                    <p className="text-xs text-gray-700 mt-1 line-clamp-2">{video.title}</p>
                  </a>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
