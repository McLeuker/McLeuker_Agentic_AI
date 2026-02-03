'use client';

import { Message } from '@/types';
import { User, Bot, ExternalLink } from 'lucide-react';

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  const response = message.response;

  return (
    <div className={`flex gap-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {/* Avatar */}
      {!isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
          <Bot size={18} className="text-white" />
        </div>
      )}

      {/* Message Content */}
      <div className={`max-w-3xl ${isUser ? 'order-first' : ''}`}>
        <div
          className={`rounded-2xl px-4 py-3 ${
            isUser
              ? 'bg-purple-600 text-white'
              : 'bg-gray-100 text-gray-800'
          }`}
        >
          {/* Main Content */}
          <div className="prose prose-sm max-w-none">
            {isUser ? (
              <p className="m-0">{message.content}</p>
            ) : (
              <div 
                className="whitespace-pre-wrap"
                dangerouslySetInnerHTML={{ 
                  __html: formatMarkdown(message.content) 
                }}
              />
            )}
          </div>
        </div>

        {/* V5.1 Response Extras */}
        {!isUser && response && (
          <div className="mt-3 space-y-3">
            {/* Key Insights */}
            {response.key_insights && response.key_insights.length > 0 && (
              <div className="bg-purple-50 rounded-xl p-4">
                <h4 className="text-sm font-semibold text-purple-800 mb-2">Key Insights</h4>
                <ul className="space-y-2">
                  {response.key_insights.map((insight, idx) => (
                    <li key={idx} className="text-sm text-purple-700">
                      <strong>{insight.title}:</strong> {insight.description}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Sources */}
            {response.sources && response.sources.length > 0 && (
              <div className="bg-gray-50 rounded-xl p-4">
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Sources</h4>
                <ul className="space-y-2">
                  {response.sources.map((source, idx) => (
                    <li key={idx}>
                      <a
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-800"
                      >
                        <ExternalLink size={14} />
                        <span>{source.title}</span>
                      </a>
                      {source.snippet && (
                        <p className="text-xs text-gray-500 mt-1 ml-6">{source.snippet}</p>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Follow-up Questions */}
            {response.follow_up_questions && response.follow_up_questions.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {response.follow_up_questions.map((question, idx) => (
                  <button
                    key={idx}
                    className="text-sm px-3 py-1 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-full transition-colors"
                  >
                    {question}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* User Avatar */}
      {isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center">
          <User size={18} className="text-gray-600" />
        </div>
      )}
    </div>
  );
}

// Simple markdown formatter
function formatMarkdown(text: string): string {
  if (!text) return '';
  
  return text
    // Bold
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    // Italic
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    // Headers
    .replace(/^### (.*$)/gm, '<h3 class="text-lg font-semibold mt-4 mb-2">$1</h3>')
    .replace(/^## (.*$)/gm, '<h2 class="text-xl font-semibold mt-4 mb-2">$1</h2>')
    .replace(/^# (.*$)/gm, '<h1 class="text-2xl font-bold mt-4 mb-2">$1</h1>')
    // Lists
    .replace(/^- (.*$)/gm, '<li class="ml-4">$1</li>')
    .replace(/^• (.*$)/gm, '<li class="ml-4">$1</li>')
    // Line breaks
    .replace(/\n/g, '<br />');
}
