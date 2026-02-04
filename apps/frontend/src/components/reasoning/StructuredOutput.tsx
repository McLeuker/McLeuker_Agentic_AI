'use client';

import { useState } from 'react';
import { cn } from '@/lib/utils';
import {
  Lightbulb,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Copy,
  Check,
  MessageSquare,
  FileText,
  Sparkles
} from 'lucide-react';

// =============================================================================
// Types
// =============================================================================

export interface Source {
  id: string;
  title: string;
  url: string;
  snippet?: string;
  publisher?: string;
  type?: string;
}

export interface KeyInsight {
  icon?: string;
  title: string;
  description: string;
  importance: 'high' | 'medium' | 'low';
}

export interface ResponseData {
  summary: string;
  main_content: string;
  key_insights: KeyInsight[];
  sources: Source[];
  follow_up_questions: string[];
  intent?: string;
  domain?: string;
  credits_used?: number;
}

// =============================================================================
// StructuredOutput Component
// =============================================================================

interface StructuredOutputProps {
  response: ResponseData;
  onFollowUp?: (question: string) => void;
  className?: string;
}

export function StructuredOutput({ 
  response, 
  onFollowUp,
  className 
}: StructuredOutputProps) {
  const [showFullContent, setShowFullContent] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  
  const handleCopy = async (text: string, id: string) => {
    await navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };
  
  // Truncate content for initial view
  const contentPreview = response.main_content.slice(0, 800);
  const hasMoreContent = response.main_content.length > 800;
  
  return (
    <div className={cn("space-y-6", className)}>
      {/* Summary Section */}
      <div className="bg-gradient-to-r from-purple-500/10 to-blue-500/10 border border-purple-500/20 rounded-xl p-4">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-purple-500/20 rounded-lg">
            <Sparkles className="h-5 w-5 text-purple-400" />
          </div>
          <div className="flex-1">
            <h3 className="text-sm font-medium text-white/60 mb-1">Summary</h3>
            <p className="text-white/90 leading-relaxed">{response.summary}</p>
          </div>
          <button
            onClick={() => handleCopy(response.summary, 'summary')}
            className="p-2 text-white/40 hover:text-white/80 hover:bg-white/10 rounded-lg transition-colors"
          >
            {copiedId === 'summary' ? (
              <Check className="h-4 w-4 text-green-400" />
            ) : (
              <Copy className="h-4 w-4" />
            )}
          </button>
        </div>
      </div>
      
      {/* Key Insights */}
      {response.key_insights && response.key_insights.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Lightbulb className="h-5 w-5 text-yellow-400" />
            <h3 className="text-sm font-medium text-white/80">Key Insights</h3>
          </div>
          <div className="grid gap-3">
            {response.key_insights.map((insight, index) => (
              <InsightCard key={index} insight={insight} index={index} />
            ))}
          </div>
        </div>
      )}
      
      {/* Main Content */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-blue-400" />
            <h3 className="text-sm font-medium text-white/80">Detailed Analysis</h3>
          </div>
          <button
            onClick={() => handleCopy(response.main_content, 'content')}
            className="flex items-center gap-1 px-2 py-1 text-xs text-white/40 hover:text-white/80 hover:bg-white/10 rounded-lg transition-colors"
          >
            {copiedId === 'content' ? (
              <>
                <Check className="h-3 w-3 text-green-400" />
                Copied
              </>
            ) : (
              <>
                <Copy className="h-3 w-3" />
                Copy
              </>
            )}
          </button>
        </div>
        <div className="bg-[#1A1A1A] border border-white/10 rounded-xl p-4">
          <div 
            className={cn(
              "prose prose-invert prose-sm max-w-none",
              "prose-headings:text-white/90 prose-headings:font-semibold",
              "prose-p:text-white/70 prose-p:leading-relaxed",
              "prose-strong:text-white/90",
              "prose-ul:text-white/70 prose-li:text-white/70",
              !showFullContent && hasMoreContent && "max-h-[300px] overflow-hidden relative"
            )}
          >
            <FormattedContent 
              content={showFullContent ? response.main_content : contentPreview} 
            />
            {!showFullContent && hasMoreContent && (
              <div className="absolute bottom-0 left-0 right-0 h-20 bg-gradient-to-t from-[#1A1A1A] to-transparent" />
            )}
          </div>
          {hasMoreContent && (
            <button
              onClick={() => setShowFullContent(!showFullContent)}
              className="flex items-center gap-1 mt-4 text-sm text-purple-400 hover:text-purple-300 transition-colors"
            >
              {showFullContent ? (
                <>
                  <ChevronUp className="h-4 w-4" />
                  Show less
                </>
              ) : (
                <>
                  <ChevronDown className="h-4 w-4" />
                  Show more
                </>
              )}
            </button>
          )}
        </div>
      </div>
      
      {/* Sources */}
      {response.sources && response.sources.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <ExternalLink className="h-5 w-5 text-green-400" />
            <h3 className="text-sm font-medium text-white/80">
              Sources ({response.sources.length})
            </h3>
          </div>
          <div className="grid gap-2">
            {response.sources.map((source, index) => (
              <SourceCard key={source.id || index} source={source} index={index} />
            ))}
          </div>
        </div>
      )}
      
      {/* Follow-up Questions */}
      {response.follow_up_questions && response.follow_up_questions.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5 text-cyan-400" />
            <h3 className="text-sm font-medium text-white/80">Continue Exploring</h3>
          </div>
          <div className="grid gap-2">
            {response.follow_up_questions.map((question, index) => (
              <button
                key={index}
                onClick={() => onFollowUp?.(question)}
                className={cn(
                  "text-left p-3 rounded-xl",
                  "bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20",
                  "text-sm text-white/70 hover:text-white/90",
                  "transition-all duration-200"
                )}
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}
      
      {/* Credits Used */}
      {response.credits_used !== undefined && (
        <div className="text-center text-xs text-white/30 pt-2">
          {response.credits_used} credits used for this response
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Sub-components
// =============================================================================

function InsightCard({ insight, index }: { insight: KeyInsight; index: number }) {
  const importanceColors = {
    high: 'border-yellow-500/30 bg-yellow-500/5',
    medium: 'border-blue-500/30 bg-blue-500/5',
    low: 'border-white/10 bg-white/5'
  };
  
  return (
    <div className={cn(
      "p-4 rounded-xl border",
      importanceColors[insight.importance]
    )}>
      <div className="flex items-start gap-3">
        <span className="text-xl">{insight.icon || '💡'}</span>
        <div className="flex-1">
          <h4 className="font-medium text-white/90 mb-1">{insight.title}</h4>
          <p className="text-sm text-white/60 leading-relaxed">{insight.description}</p>
        </div>
      </div>
    </div>
  );
}

function SourceCard({ source, index }: { source: Source; index: number }) {
  return (
    <a
      href={source.url}
      target="_blank"
      rel="noopener noreferrer"
      className={cn(
        "flex items-start gap-3 p-3 rounded-xl",
        "bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20",
        "transition-all duration-200 group"
      )}
    >
      <span className="flex items-center justify-center w-6 h-6 rounded-full bg-white/10 text-xs text-white/60">
        {index + 1}
      </span>
      <div className="flex-1 min-w-0">
        <h4 className="text-sm font-medium text-white/80 group-hover:text-white truncate">
          {source.title}
        </h4>
        {source.snippet && (
          <p className="text-xs text-white/40 mt-1 line-clamp-2">{source.snippet}</p>
        )}
        <p className="text-xs text-white/30 mt-1 truncate">{source.url}</p>
      </div>
      <ExternalLink className="h-4 w-4 text-white/30 group-hover:text-white/60 flex-shrink-0" />
    </a>
  );
}

function FormattedContent({ content }: { content: string }) {
  // Simple markdown-like formatting
  const formatContent = (text: string) => {
    // Split by double newlines for paragraphs
    const paragraphs = text.split(/\n\n+/);
    
    return paragraphs.map((para, i) => {
      // Check for headers
      if (para.startsWith('## ')) {
        return (
          <h2 key={i} className="text-lg font-semibold text-white/90 mt-4 mb-2">
            {para.replace('## ', '')}
          </h2>
        );
      }
      if (para.startsWith('### ')) {
        return (
          <h3 key={i} className="text-base font-semibold text-white/90 mt-3 mb-2">
            {para.replace('### ', '')}
          </h3>
        );
      }
      
      // Check for bullet points
      if (para.includes('\n- ') || para.startsWith('- ')) {
        const items = para.split('\n').filter(line => line.trim());
        return (
          <ul key={i} className="list-disc list-inside space-y-1 my-2">
            {items.map((item, j) => (
              <li key={j} className="text-white/70">
                {item.replace(/^[-•*]\s*/, '')}
              </li>
            ))}
          </ul>
        );
      }
      
      // Regular paragraph with bold text support
      const formattedPara = para.replace(
        /\*\*(.+?)\*\*/g, 
        '<strong class="text-white/90">$1</strong>'
      );
      
      return (
        <p 
          key={i} 
          className="text-white/70 leading-relaxed mb-3"
          dangerouslySetInnerHTML={{ __html: formattedPara }}
        />
      );
    });
  };
  
  return <>{formatContent(content)}</>;
}

export default StructuredOutput;
