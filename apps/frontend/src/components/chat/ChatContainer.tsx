'use client';

import { useEffect, useRef } from 'react';
import { useChatStore } from '@/stores/useStore';
import MessageBubble from './MessageBubble';
import ChatInput from './ChatInput';
import { Sparkles, TrendingUp, Palette, Leaf } from 'lucide-react';

export default function ChatContainer() {
  const { getCurrentMessages, isLoading, error, clearError, sendMessage } = useChatStore();
  const messages = getCurrentMessages();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Example prompts for empty state
  const examplePrompts = [
    { icon: TrendingUp, text: "What are the top fashion trends for 2026?" },
    { icon: Palette, text: "Best skincare routine for combination skin" },
    { icon: Leaf, text: "Sustainable fashion brands to watch" },
    { icon: Sparkles, text: "Latest beauty innovations and products" },
  ];

  return (
    <div className="flex flex-col h-full">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto space-y-6">
          {messages.length === 0 ? (
            // Empty State
            <div className="flex flex-col items-center justify-center h-full py-12">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center mb-6">
                <Sparkles size={32} className="text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-800 mb-2">
                Welcome to McLeuker AI
              </h2>
              <p className="text-gray-500 text-center max-w-md mb-8">
                Your intelligent assistant for fashion, beauty, skincare, and sustainability insights.
                Ask me anything!
              </p>

              {/* Example Prompts */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full max-w-2xl">
                {examplePrompts.map((prompt, idx) => (
                  <button
                    key={idx}
                    onClick={() => sendMessage(prompt.text)}
                    className="flex items-center gap-3 p-4 bg-gray-50 hover:bg-gray-100 rounded-xl text-left transition-colors"
                  >
                    <prompt.icon size={20} className="text-purple-500" />
                    <span className="text-sm text-gray-700">{prompt.text}</span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            // Messages List
            <>
              {messages.map((message) => (
                <MessageBubble key={message.id} message={message} />
              ))}

              {/* Loading Indicator */}
              {isLoading && (
                <div className="flex gap-4">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                    <Sparkles size={18} className="text-white animate-pulse" />
                  </div>
                  <div className="bg-gray-100 rounded-2xl px-4 py-3">
                    <div className="flex gap-1">
                      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                  </div>
                </div>
              )}

              {/* Error Message */}
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-xl p-4">
                  <p className="text-red-700 text-sm">{error}</p>
                  <button
                    onClick={clearError}
                    className="text-red-600 text-sm underline mt-2"
                  >
                    Dismiss
                  </button>
                </div>
              )}
            </>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <ChatInput />
    </div>
  );
}
