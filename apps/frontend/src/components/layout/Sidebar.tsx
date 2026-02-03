'use client';

import { Plus, MessageSquare, Settings, LogOut } from 'lucide-react';
import { useChatStore } from '@/stores/useStore';

export default function Sidebar() {
  const { conversations, currentConversationId, createConversation, setCurrentConversation } = useChatStore();

  return (
    <aside className="w-64 bg-gray-900 text-white flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <h1 className="text-xl font-bold bg-gradient-to-r from-purple-400 to-pink-500 bg-clip-text text-transparent">
          McLeuker AI
        </h1>
        <p className="text-xs text-gray-400 mt-1">Fashion Intelligence Platform</p>
      </div>

      {/* New Chat Button */}
      <div className="p-4">
        <button
          onClick={() => createConversation()}
          className="w-full flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors"
        >
          <Plus size={18} />
          <span>New Chat</span>
        </button>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto px-2">
        <p className="px-2 py-1 text-xs text-gray-500 uppercase">Recent Chats</p>
        {conversations.length === 0 ? (
          <p className="px-2 py-4 text-sm text-gray-500 text-center">No conversations yet</p>
        ) : (
          <ul className="space-y-1">
            {conversations.map((conv) => (
              <li key={conv.id}>
                <button
                  onClick={() => setCurrentConversation(conv.id)}
                  className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-left text-sm transition-colors ${
                    currentConversationId === conv.id
                      ? 'bg-gray-700 text-white'
                      : 'text-gray-300 hover:bg-gray-800'
                  }`}
                >
                  <MessageSquare size={16} />
                  <span className="truncate">{conv.title}</span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-700 space-y-2">
        <button className="w-full flex items-center gap-2 px-3 py-2 text-gray-300 hover:bg-gray-800 rounded-lg text-sm transition-colors">
          <Settings size={16} />
          <span>Settings</span>
        </button>
        <button className="w-full flex items-center gap-2 px-3 py-2 text-gray-300 hover:bg-gray-800 rounded-lg text-sm transition-colors">
          <LogOut size={16} />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
}
