'use client';

import React, { useState } from 'react';
import { Message } from './ChatInterface';
import { DownloadButton } from './DownloadButton';
import { SearchResults } from './SearchResults';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { formatTokenCount, formatLatency } from '@/lib/api';

interface MessageListProps {
  messages: Message[];
}

export function MessageList({ messages }: MessageListProps) {
  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {messages.map((message) => (
        <MessageItem key={message.id} message={message} />
      ))}
    </div>
  );
}

function MessageItem({ message }: { message: Message }) {
  const isUser = message.role === 'user';
  const [showReasoning, setShowReasoning] = useState(false);

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div 
        className={`max-w-[90%] sm:max-w-[85%] rounded-2xl px-5 py-4 ${
          isUser 
            ? 'bg-blue-600 text-white' 
            : 'bg-white border shadow-sm'
        }`}
      >
        {/* Avatar and role */}
        {!isUser && (
          <div className="flex items-center gap-2 mb-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
              <span className="text-white font-bold text-xs">AI</span>
            </div>
            <span className="text-sm font-medium text-gray-700">McLeuker AI</span>
            {message.metadata && (
              <span className="text-xs text-gray-400 ml-auto">
                {message.metadata.latency_ms && formatLatency(message.metadata.latency_ms)}
                {message.metadata.tokens && ` • ${formatTokenCount(message.metadata.tokens.total_tokens)} tokens`}
              </span>
            )}
          </div>
        )}

        {/* Content */}
        <div className={`prose ${isUser ? 'prose-invert' : 'prose-gray'} max-w-none prose-pre:p-0`}>
          {message.isStreaming && !message.content ? (
            <StreamingIndicator />
          ) : (
            <ReactMarkdown
              components={{
                code({ node, inline, className, children, ...props }: any) {
                  const match = /language-(\w+)/.exec(className || '');
                  return !inline && match ? (
                    <SyntaxHighlighter
                      style={vscDarkPlus}
                      language={match[1]}
                      PreTag="div"
                      {...props}
                    >
                      {String(children).replace(/\n$/, '')}
                    </SyntaxHighlighter>
                  ) : (
                    <code className={className} {...props}>
                      {children}
                    </code>
                  );
                }
              }}
            >
              {message.content}
            </ReactMarkdown>
          )}
        </div>

        {/* Reasoning toggle */}
        {message.reasoning && (
          <div className="mt-3">
            <button
              onClick={() => setShowReasoning(!showReasoning)}
              className={`flex items-center gap-1 text-xs ${
                isUser ? 'text-blue-200' : 'text-gray-500'
              } hover:underline`}
            >
              <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              {showReasoning ? 'Hide reasoning' : 'Show reasoning'}
            </button>
            
            {showReasoning && (
              <div className={`mt-2 p-3 rounded-lg text-xs ${
                isUser ? 'bg-blue-700 text-blue-100' : 'bg-gray-100 text-gray-600'
              }`}>
                <p className="font-medium mb-1">Thinking Process:</p>
                {message.reasoning}
              </div>
            )}
          </div>
        )}

        {/* Search Results */}
        {message.searchSources && message.searchSources.length > 0 && (
          <SearchResults sources={message.searchSources} />
        )}

        {/* Download Buttons */}
        {message.downloads && message.downloads.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2">
            {message.downloads.map((file, i) => (
              <DownloadButton key={i} file={file} />
            ))}
          </div>
        )}

        {/* Timestamp */}
        <div className={`mt-3 text-xs ${isUser ? 'text-blue-200' : 'text-gray-400'}`}>
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
    </div>
  );
}

function StreamingIndicator() {
  return (
    <div className="flex items-center gap-2 py-2">
      <div className="flex gap-1">
        <span className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
        <span className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
        <span className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
      </div>
      <span className="text-sm text-gray-500">Thinking...</span>
    </div>
  );
}
