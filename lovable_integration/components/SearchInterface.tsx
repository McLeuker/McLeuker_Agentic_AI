/**
 * McLeuker Agentic AI Platform - Search Interface Component
 * 
 * A complete AI-powered search interface component for Lovable integration.
 * Copy this file into your Lovable project's `src/components/` directory.
 */

import { useState } from 'react';
import { useSearch } from '@/hooks/useSearch';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { 
  Loader2, 
  Search, 
  ExternalLink, 
  ChevronRight,
  Sparkles
} from 'lucide-react';

interface SearchInterfaceProps {
  className?: string;
  title?: string;
  placeholder?: string;
}

export function SearchInterface({
  className = '',
  title = 'AI-Powered Search',
  placeholder = 'Search for anything...',
}: SearchInterfaceProps) {
  const [query, setQuery] = useState('');
  const { results, isLoading, error, performSearch, clearResults } = useSearch();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;
    await performSearch(query);
  };

  const handleFollowUp = async (question: string) => {
    setQuery(question);
    await performSearch(question);
  };

  return (
    <Card className={`flex flex-col ${className}`}>
      <CardHeader className="py-4 border-b">
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-blue-500" />
          {title}
        </CardTitle>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col p-4">
        {/* Search Form */}
        <form onSubmit={handleSubmit} className="flex gap-2 mb-4">
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={placeholder}
            disabled={isLoading}
            className="flex-1"
          />
          <Button type="submit" disabled={isLoading || !query.trim()}>
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Search className="w-4 h-4" />
            )}
          </Button>
        </form>

        {/* Error Display */}
        {error && (
          <div className="p-3 mb-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-600">{error.message}</p>
          </div>
        )}

        {/* Results */}
        {results && (
          <ScrollArea className="flex-1">
            <div className="space-y-6">
              {/* Summary */}
              {results.summary && (
                <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <h3 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
                    <Sparkles className="w-4 h-4" />
                    AI Summary
                  </h3>
                  <p className="text-sm text-blue-800 whitespace-pre-wrap">
                    {results.summary}
                  </p>
                </div>
              )}

              {/* Search Results */}
              {results.results.length > 0 && (
                <div>
                  <h3 className="font-semibold text-gray-700 mb-3">
                    Sources ({results.total_results} results)
                  </h3>
                  <div className="space-y-3">
                    {results.results.map((result, idx) => (
                      <a
                        key={idx}
                        href={result.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block p-3 border rounded-lg hover:bg-gray-50 transition-colors"
                      >
                        <div className="flex items-start gap-2">
                          <div className="flex-1 min-w-0">
                            <h4 className="font-medium text-blue-600 hover:underline truncate">
                              {result.title}
                            </h4>
                            <p className="text-xs text-green-700 truncate mt-1">
                              {result.url}
                            </p>
                            <p className="text-sm text-gray-600 mt-2 line-clamp-2">
                              {result.snippet}
                            </p>
                          </div>
                          <ExternalLink className="w-4 h-4 text-gray-400 flex-shrink-0" />
                        </div>
                      </a>
                    ))}
                  </div>
                </div>
              )}

              {/* Follow-up Questions */}
              {results.follow_up_questions && results.follow_up_questions.length > 0 && (
                <div>
                  <h3 className="font-semibold text-gray-700 mb-3">
                    Related Questions
                  </h3>
                  <div className="space-y-2">
                    {results.follow_up_questions.map((question, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleFollowUp(question)}
                        className="w-full flex items-center gap-2 p-3 text-left border rounded-lg hover:bg-gray-50 transition-colors"
                      >
                        <ChevronRight className="w-4 h-4 text-blue-500 flex-shrink-0" />
                        <span className="text-sm text-gray-700">{question}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Query Analysis (for debugging) */}
              {results.expanded_queries && results.expanded_queries.length > 1 && (
                <div className="pt-4 border-t">
                  <p className="text-xs text-gray-500 mb-2">
                    Also searched for:
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {results.expanded_queries.slice(1).map((q, idx) => (
                      <Badge key={idx} variant="secondary" className="text-xs">
                        {q}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </ScrollArea>
        )}

        {/* Empty State */}
        {!results && !isLoading && (
          <div className="flex-1 flex items-center justify-center text-gray-400">
            <div className="text-center">
              <Search className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p className="text-sm">
                Enter a query to search with AI-powered analysis
              </p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default SearchInterface;
