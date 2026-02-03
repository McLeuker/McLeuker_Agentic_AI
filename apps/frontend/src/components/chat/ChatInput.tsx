'use client';

import { useState, KeyboardEvent } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { useChatStore } from '@/stores/useStore';

export default function ChatInput() {
  const [input, setInput] = useState('');
  const { sendMessage, isLoading } = useChatStore();

  const handleSubmit = async () => {
    if (!input.trim() || isLoading) return;
    
    const message = input.trim();
    setInput('');
    await sendMessage(message);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="border-t border-gray-200 bg-white p-4">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-end gap-3 bg-gray-50 rounded-2xl border border-gray-200 p-3">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about fashion trends, beauty tips, sustainability..."
            className="flex-1 resize-none bg-transparent border-none outline-none text-gray-800 placeholder-gray-400 min-h-[24px] max-h-[200px]"
            rows={1}
            disabled={isLoading}
          />
          <button
            onClick={handleSubmit}
            disabled={!input.trim() || isLoading}
            className="flex-shrink-0 p-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-xl transition-colors"
          >
            {isLoading ? (
              <Loader2 size={20} className="animate-spin" />
            ) : (
              <Send size={20} />
            )}
          </button>
        </div>
        <p className="text-xs text-gray-400 text-center mt-2">
          McLeuker AI provides fashion intelligence powered by real-time research
        </p>
      </div>
    </div>
  );
}
