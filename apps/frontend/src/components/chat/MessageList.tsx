'use client';

import React from 'react';
import { Message } from './ChatInterface';
import { DownloadButton } from './DownloadButton';
import { SearchResults } from './SearchResults';
import ReactMarkdown from 'react-markdown';

interface MessageListProps {
  messages: Message[];
}

export function MessageList({ messages }: MessageListProps) {
  return (
    <div className="space-y-4">
      {messages.map((message) => (
        <MessageItem key={message.id} message={message} />
      ))}
    </div>
  );
}

function MessageItem({ message }: { message: Message }) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[85%] ${isUser ? 'bg-blue-600 text-white' : 'bg-white border'} rounded-2xl px-4 py-3 shadow-sm`}>
        {/* Avatar and role */}
        {!isUser && (
          <div className="flex items-center gap-2 mb-2">
            <div className="w-6 h-6 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
              <span className="text-xs text-white font-bold">AI</span>
            </div>
            <span className="text-xs text-gray-500">McLeuker AI</span>
          </div>
        )}

        {/* Content */}
        <div className={`prose ${isUser ? 'prose-invert' : ''} max-w-none`}>
          {message.isStreaming && !message.content ? (
            <div className="flex items-center gap-2 text-gray-400">
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" />
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce delay-100" />
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce delay-200" />
            </div>
          ) : (
            <ReactMarkdown>{message.content}</ReactMarkdown>
          )}
        </div>

        {/* Reasoning (collapsible) */}
        {message.reasoning && (
          <details className="mt-3 text-sm">
            <summary className="cursor-pointer text-gray-500 hover:text-gray-700 flex items-center gap-1">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              Show reasoning
            </summary>
            <div className="mt-2 p-3 bg-gray-100 rounded-lg text-gray-700 text-xs">
              {message.reasoning}
            </div>
          </details>
        )}

        {/* Search Results */}
        {message.searchResults && message.searchResults.length > 0 && (
          <SearchResults results={message.searchResults} />
        )}

        {/* Download Buttons */}
        {message.downloads && message.downloads.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {message.downloads.map((file, i) => (
              <DownloadButton key={i} file={file} />
            ))}
          </div>
        )}

        {/* Timestamp */}
        <div className={`mt-2 text-xs ${isUser ? 'text-blue-200' : 'text-gray-400'}`}>
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
    </div>
  );
}
