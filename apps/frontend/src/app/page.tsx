'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Plus, MessageSquare, Sparkles, ExternalLink, ChevronDown, ChevronUp } from 'lucide-react';
import { useChatStore } from '@/stores/useStore';
import { cn } from '@/lib/utils';

// Example prompts for the starter panel
const EXAMPLE_PROMPTS = [
  "What are the latest sustainable fashion trends for 2026?",
  "Compare luxury skincare brands for anti-aging",
  "Find emerging fashion designers from Copenhagen",
  "Analyze the athleisure market growth",
];

export default function Home() {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  
  const {
    conversations,
    currentConversationId,
    isLoading,
    error,
    createConversation,
    setCurrentConversation,
    sendMessage,
    getCurrentMessages,
    clearError,
  } = useChatStore();

  const messages = getCurrentMessages();

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [input]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    
    const message = input.trim();
    setInput('');
    await sendMessage(message);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handlePromptClick = async (prompt: string) => {
    setInput('');
    await sendMessage(prompt);
  };

  return (
    <div className="flex h-screen bg-black">
      {/* Sidebar */}
      <aside className="hidden lg:flex w-72 flex-col graphite-glass h-full">
        {/* Header */}
        <div className="px-4 pt-5 pb-3 flex items-center justify-between shrink-0">
          <span className="font-medium text-[13px] text-white/80">Chat History</span>
        </div>

        {/* New Chat Button */}
        <div className="px-4 pb-3 shrink-0">
          <button
            onClick={() => createConversation()}
            className={cn(
              "w-full flex items-center justify-center gap-2",
              "bg-white text-black hover:bg-white/90",
              "h-10 rounded-full text-[13px] font-medium",
              "transition-all duration-160"
            )}
          >
            <Plus className="h-4 w-4" />
            New Chat
          </button>
        </div>

        {/* Chat count */}
        <div className="px-4 pb-2 shrink-0">
          <p className="text-[10px] font-medium text-white/40 uppercase tracking-wider">
            {conversations.length} {conversations.length === 1 ? 'chat' : 'chats'}
          </p>
        </div>

        {/* Conversation List */}
        <div className="flex-1 overflow-y-auto px-4 pb-4 space-y-2">
          {conversations.length === 0 ? (
            <div className="px-2 py-8 text-center">
              <MessageSquare className="h-8 w-8 text-white/25 mx-auto mb-3" />
              <p className="text-[13px] text-white/50">No chats yet</p>
              <p className="text-[11px] text-white/35 mt-1">Start a new chat to begin</p>
            </div>
          ) : (
            conversations.map((conv) => (
              <button
                key={conv.id}
                onClick={() => setCurrentConversation(conv.id)}
                className={cn(
                  "w-full text-left px-4 py-3 rounded-xl",
                  "chat-sidebar-item premium-hover",
                  currentConversationId === conv.id && "chat-sidebar-item-active"
                )}
              >
                <div className="flex items-center gap-2.5">
                  <MessageSquare className="h-4 w-4 text-white/50 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-[12px] font-medium text-white/90 line-clamp-2 leading-relaxed">
                      {conv.title}
                    </p>
                    <p className="text-[10px] text-white/45 mt-1.5">
                      {conv.messages.length} messages
                    </p>
                  </div>
                </div>
              </button>
            ))
          )}
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-h-0 overflow-hidden">
        {/* Header */}
        <header className="h-[72px] px-6 flex items-center justify-between border-b border-white/[0.08] bg-black shrink-0">
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-semibold text-white">McLeuker AI</h1>
            <span className="text-[11px] px-2 py-0.5 rounded-full bg-white/10 text-white/60">
              Fashion Intelligence
            </span>
          </div>
        </header>

        {/* Chat Area */}
        <div className="flex-1 flex flex-col min-h-0 overflow-hidden chat-panel-gradient relative">
          {messages.length === 0 ? (
            /* Starter Panel */
            <div className="flex-1 flex flex-col items-center justify-center px-6 premium-ombre-bg">
              <div className="max-w-2xl w-full text-center">
                <h2 className="text-3xl font-editorial text-white mb-2">
                  What can I help you discover?
                </h2>
                <p className="text-white/55 text-[15px] mb-8">
                  Fashion trends, market intelligence, sourcing insights, and more.
                </p>
                
                {/* Example Prompts */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {EXAMPLE_PROMPTS.map((prompt, index) => (
                    <button
                      key={index}
                      onClick={() => handlePromptClick(prompt)}
                      className={cn(
                        "text-left px-4 py-3 rounded-xl",
                        "bg-white/[0.04] hover:bg-white/[0.08]",
                        "border border-white/[0.08] hover:border-white/[0.12]",
                        "transition-all duration-160"
                      )}
                    >
                      <div className="flex items-start gap-2.5">
                        <Sparkles className="h-4 w-4 text-white/50 mt-0.5 flex-shrink-0" />
                        <span className="text-[13px] text-white/70">{prompt}</span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            /* Messages */
            <div className="flex-1 overflow-y-auto py-6 pb-[140px]">
              <div className="max-w-[1040px] mx-auto px-6 lg:px-8 space-y-4">
                {messages.map((message) => (
                  <div key={message.id} className={cn(
                    "py-3",
                    message.role === 'user' ? 'flex justify-end' : ''
                  )}>
                    {message.role === 'user' ? (
                      <div className="max-w-[75%] lg:max-w-[65%]">
                        <p className="text-[15px] text-white/[0.88] leading-[1.7] text-right">
                          {message.content}
                        </p>
                      </div>
                    ) : (
                      <div className="max-w-[800px]">
                        <div className="ai-message-content">
                          {message.content}
                        </div>
                        
                        {/* Sources */}
                        {message.response?.sources && message.response.sources.length > 0 && (
                          <SourcesSection sources={message.response.sources} />
                        )}
                        
                        {/* Follow-up Questions */}
                        {message.response?.follow_up_questions && message.response.follow_up_questions.length > 0 && (
                          <FollowUpSection 
                            questions={message.response.follow_up_questions} 
                            onFollowUp={handlePromptClick}
                          />
                        )}
                      </div>
                    )}
                  </div>
                ))}
                
                {/* Loading indicator */}
                {isLoading && (
                  <div className="flex justify-start py-2">
                    <div className="max-w-[65%] graphite-bubble-ai rounded-[20px] px-5 py-4">
                      <div className="flex items-center gap-3">
                        <div className="flex-shrink-0 w-6 h-6 rounded-full bg-white/10 flex items-center justify-center">
                          <div className="h-3 w-3 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        </div>
                        <span className="text-[14px] text-white/55">McLeuker AI is thinking...</span>
                      </div>
                    </div>
                  </div>
                )}
                
                <div ref={messagesEndRef} />
              </div>
            </div>
          )}

          {/* Input Area - Fixed at bottom */}
          <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black via-black to-transparent">
            <div className="max-w-[800px] mx-auto">
              <form onSubmit={handleSubmit} className="relative">
                <textarea
                  ref={textareaRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask McLeuker AI about fashion, trends, or market intelligence..."
                  disabled={isLoading}
                  rows={1}
                  className={cn(
                    "w-full min-h-[60px] max-h-[200px] pr-14 resize-none",
                    "rounded-[20px] px-5 py-4",
                    "bg-gradient-to-b from-[#1B1B1B] to-[#111111]",
                    "border border-white/[0.10]",
                    "text-white/[0.88] text-[15px]",
                    "placeholder:text-white/40",
                    "shadow-[0_4px_16px_rgba(0,0,0,0.3)]",
                    "focus:border-white/[0.18] focus:outline-none",
                    "focus:ring-[3px] focus:ring-white/[0.06]",
                    "transition-all duration-160"
                  )}
                />
                <button
                  type="submit"
                  disabled={!input.trim() || isLoading}
                  className={cn(
                    "absolute right-3 bottom-3 h-9 w-9 rounded-full",
                    "flex items-center justify-center",
                    "transition-all duration-160",
                    input.trim() && !isLoading
                      ? "bg-white text-black hover:bg-white/90"
                      : "bg-white/[0.08] text-white/40"
                  )}
                >
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </button>
              </form>
              
              {/* Credit hint */}
              <div className="flex items-center justify-between text-[11px] text-white/50 px-1 mt-2">
                <span>4-12 credits • Press Enter to send</span>
                <span className="hidden sm:inline">Shift + Enter for new line</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

// Sources Section Component
function SourcesSection({ sources }: { sources: Array<{ title: string; url: string; snippet?: string }> }) {
  const [expanded, setExpanded] = useState(false);
  
  if (!sources || sources.length === 0) return null;

  const displaySources = expanded ? sources : sources.slice(0, 3);

  return (
    <div className="mt-6 pt-6 border-t border-white/[0.08]">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-[13px] font-medium text-white/[0.55]">Sources</h4>
        {sources.length > 3 && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-[12px] text-white/[0.45] hover:text-white/70 flex items-center gap-1"
          >
            {expanded ? (
              <>Show less <ChevronUp className="h-3 w-3" /></>
            ) : (
              <>Show {sources.length - 3} more <ChevronDown className="h-3 w-3" /></>
            )}
          </button>
        )}
      </div>
      <div className="space-y-2">
        {displaySources.map((source, index) => (
          <a
            key={index}
            href={source.url}
            target="_blank"
            rel="noopener noreferrer"
            className="block p-3 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] transition-colors border border-white/[0.06]"
          >
            <div className="flex items-start gap-2.5">
              <span className="text-[11px] text-white/[0.40] font-mono">[{index + 1}]</span>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-1.5">
                  <span className="text-[13px] text-[#60A5FA] hover:underline truncate">
                    {source.title}
                  </span>
                  <ExternalLink className="h-3 w-3 text-white/[0.35] flex-shrink-0" />
                </div>
                {source.snippet && (
                  <p className="text-[12px] text-white/[0.50] mt-1 line-clamp-2">
                    {source.snippet}
                  </p>
                )}
              </div>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}

// Follow-up Section Component
function FollowUpSection({ questions, onFollowUp }: { questions: string[]; onFollowUp: (q: string) => void }) {
  if (!questions || questions.length === 0) return null;

  return (
    <div className="mt-6 pt-6 border-t border-white/[0.08]">
      <h4 className="text-[13px] font-medium text-white/[0.55] mb-3">Follow-up questions</h4>
      <div className="flex flex-wrap gap-2">
        {questions.map((question, index) => (
          <button
            key={index}
            onClick={() => onFollowUp(question)}
            className={cn(
              "text-[12px] text-white/[0.65]",
              "border border-white/[0.12] hover:bg-white/[0.06] hover:text-white/80",
              "flex items-center gap-1.5 py-1.5 px-3 rounded-full",
              "transition-all duration-160"
            )}
          >
            <Sparkles className="h-3 w-3" />
            {question}
          </button>
        ))}
      </div>
    </div>
  );
}
