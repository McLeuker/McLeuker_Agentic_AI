'use client';

import { useState, useEffect, useRef, useCallback } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { 
  Send, 
  Plus, 
  MessageSquare, 
  Sparkles,
  ExternalLink,
  Zap,
  Brain,
  Loader2,
  Trash2,
  Coins,
  Search,
  X,
  PanelLeftClose,
  PanelLeft,
  CheckCircle2,
  Circle,
  Globe,
  FileText,
  ChevronDown,
  ChevronUp,
  Copy,
  Check
} from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useSector, SECTORS } from "@/contexts/SectorContext";
import { useConversations, Conversation } from "@/hooks/useConversations";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { UserMenu } from "@/components/dashboard/UserMenu";

// =============================================================================
// Types - Reasoning First (No Preset Templates)
// =============================================================================

interface ReasoningStep {
  id: string;
  type: 'thinking' | 'searching' | 'analyzing' | 'writing';
  title: string;
  content: string;
  status: 'active' | 'complete';
  timestamp: Date;
}

interface Source {
  title: string;
  url: string;
  snippet?: string;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  reasoning: ReasoningStep[];
  sources: Source[];
  timestamp: Date;
  isStreaming: boolean;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://web-production-29f3c.up.railway.app';

// =============================================================================
// Reasoning Step Component - Shows AI thinking in real-time
// =============================================================================

function ReasoningStepItem({ step, isLatest }: { step: ReasoningStep; isLatest: boolean }) {
  const getIcon = () => {
    switch (step.type) {
      case 'thinking': return <Brain className="h-4 w-4" />;
      case 'searching': return <Globe className="h-4 w-4" />;
      case 'analyzing': return <FileText className="h-4 w-4" />;
      case 'writing': return <Sparkles className="h-4 w-4" />;
      default: return <Circle className="h-4 w-4" />;
    }
  };

  const getColor = () => {
    if (step.status === 'complete') return 'text-green-400';
    switch (step.type) {
      case 'thinking': return 'text-purple-400';
      case 'searching': return 'text-blue-400';
      case 'analyzing': return 'text-amber-400';
      case 'writing': return 'text-emerald-400';
      default: return 'text-white/60';
    }
  };

  return (
    <div className={cn(
      "flex items-start gap-3 py-2 px-3 rounded-lg transition-all",
      isLatest && step.status === 'active' ? "bg-white/5" : ""
    )}>
      <div className={cn("mt-0.5", getColor())}>
        {step.status === 'complete' ? (
          <CheckCircle2 className="h-4 w-4" />
        ) : (
          <div className="animate-pulse">{getIcon()}</div>
        )}
      </div>
      <div className="flex-1 min-w-0">
        <div className={cn(
          "text-sm font-medium",
          step.status === 'complete' ? "text-white/60" : "text-white/90"
        )}>
          {step.title}
        </div>
        {step.content && (
          <div className="text-xs text-white/40 mt-0.5 line-clamp-2">
            {step.content}
          </div>
        )}
      </div>
      {step.status === 'active' && (
        <Loader2 className="h-3 w-3 animate-spin text-white/40 mt-1" />
      )}
    </div>
  );
}

// =============================================================================
// Message Content Component - Renders the final response
// =============================================================================

function MessageContent({ content, sources }: { content: string; sources: Source[] }) {
  const [copied, setCopied] = useState(false);
  const [expanded, setExpanded] = useState(true);

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Simple markdown-like rendering
  const renderContent = (text: string) => {
    return text.split('\n').map((line, i) => {
      if (!line.trim()) return <br key={i} />;
      
      // Headers
      if (line.startsWith('### ')) {
        return <h3 key={i} className="text-lg font-semibold text-white mt-4 mb-2">{line.slice(4)}</h3>;
      }
      if (line.startsWith('## ')) {
        return <h2 key={i} className="text-xl font-semibold text-white mt-5 mb-3">{line.slice(3)}</h2>;
      }
      if (line.startsWith('# ')) {
        return <h1 key={i} className="text-2xl font-bold text-white mt-6 mb-4">{line.slice(2)}</h1>;
      }
      
      // Bold text
      const boldRegex = /\*\*(.*?)\*\*/g;
      const parts = line.split(boldRegex);
      
      return (
        <p key={i} className="text-white/80 leading-relaxed mb-2">
          {parts.map((part, j) => 
            j % 2 === 1 ? <strong key={j} className="text-white font-medium">{part}</strong> : part
          )}
        </p>
      );
    });
  };

  return (
    <div className="space-y-4">
      {/* Response Content */}
      <div className="relative">
        <div className={cn(
          "prose prose-invert prose-sm max-w-none",
          !expanded && "max-h-[300px] overflow-hidden"
        )}>
          {renderContent(content)}
        </div>
        
        {content.length > 1000 && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-1 text-xs text-purple-400 hover:text-purple-300 mt-2"
          >
            {expanded ? (
              <>Show less <ChevronUp className="h-3 w-3" /></>
            ) : (
              <>Show more <ChevronDown className="h-3 w-3" /></>
            )}
          </button>
        )}
        
        {/* Copy Button */}
        <button
          onClick={handleCopy}
          className="absolute top-0 right-0 p-2 text-white/40 hover:text-white/70 transition-colors"
        >
          {copied ? <Check className="h-4 w-4 text-green-400" /> : <Copy className="h-4 w-4" />}
        </button>
      </div>
      
      {/* Sources */}
      {sources.length > 0 && (
        <div className="pt-4 border-t border-white/10">
          <div className="flex items-center gap-2 mb-3">
            <ExternalLink className="h-4 w-4 text-blue-400" />
            <span className="text-sm font-medium text-white/70">Sources</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {sources.map((source, i) => (
              <a
                key={i}
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs px-3 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-300 hover:bg-blue-500/20 transition-colors"
              >
                {source.title.length > 40 ? source.title.slice(0, 40) + '...' : source.title}
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Chat Sidebar Component
// =============================================================================

function ChatSidebar({
  conversations,
  currentConversation,
  isOpen,
  onToggle,
  onSelectConversation,
  onDeleteConversation,
  onNewConversation,
}: {
  conversations: Conversation[];
  currentConversation: Conversation | null;
  isOpen: boolean;
  onToggle: () => void;
  onSelectConversation: (conversation: Conversation) => void;
  onDeleteConversation: (conversationId: string) => void;
  onNewConversation?: () => void;
}) {
  const [searchQuery, setSearchQuery] = useState("");

  const filteredConversations = conversations.filter((conv) =>
    conv.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (!isOpen) {
    return (
      <aside className="hidden lg:flex w-14 flex-col fixed left-0 top-[60px] bottom-0 z-40 bg-[#0D0D0D] border-r border-white/[0.08]">
        <div className="p-2 pt-4">
          <button
            onClick={onToggle}
            className="w-10 h-10 flex items-center justify-center text-white/60 hover:text-white hover:bg-white/[0.08] rounded-lg transition-colors"
          >
            <PanelLeft className="h-4 w-4" />
          </button>
        </div>
      </aside>
    );
  }

  return (
    <aside className="hidden lg:flex w-64 flex-col fixed left-0 top-[60px] bottom-0 z-40 bg-[#0D0D0D] border-r border-white/[0.08]">
      <div className="px-4 pt-4 pb-3 flex items-center justify-between">
        <span className="font-medium text-sm text-white/80">Chats</span>
        <button
          onClick={onToggle}
          className="h-8 w-8 flex items-center justify-center text-white/50 hover:text-white hover:bg-white/[0.08] rounded-lg transition-colors"
        >
          <PanelLeftClose className="h-4 w-4" />
        </button>
      </div>

      {onNewConversation && (
        <div className="px-4 pb-3">
          <button
            onClick={onNewConversation}
            className="w-full flex items-center justify-center gap-2 bg-white text-black hover:bg-white/90 h-9 rounded-lg text-sm font-medium transition-colors"
          >
            <Plus className="h-4 w-4" />
            New Chat
          </button>
        </div>
      )}

      <div className="px-4 pb-3">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-white/40" />
          <input
            placeholder="Search..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-8 h-9 text-sm bg-white/[0.05] border border-white/[0.08] rounded-lg text-white placeholder:text-white/35 focus:border-white/[0.15] focus:outline-none transition-all"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery("")}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-white/40 hover:text-white/70"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-3 pb-4 space-y-1">
        {filteredConversations.length === 0 ? (
          <div className="px-2 py-8 text-center">
            <MessageSquare className="h-8 w-8 text-white/25 mx-auto mb-3" />
            <p className="text-sm text-white/50">
              {searchQuery ? "No matching chats" : "No chats yet"}
            </p>
          </div>
        ) : (
          filteredConversations.map((conv) => (
            <div
              key={conv.id}
              className={cn(
                "group relative w-full text-left px-3 py-2.5 rounded-lg cursor-pointer transition-all",
                currentConversation?.id === conv.id
                  ? "bg-white/[0.08]"
                  : "hover:bg-white/[0.04]"
              )}
              onClick={() => onSelectConversation(conv)}
            >
              <p className="text-sm text-white/80 truncate pr-6">{conv.title}</p>
              <p className="text-xs text-white/40 mt-0.5">
                {new Date(conv.updatedAt).toLocaleDateString()}
              </p>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteConversation(conv.id);
                }}
                className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 text-white/30 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-all"
              >
                <Trash2 className="h-3.5 w-3.5" />
              </button>
            </div>
          ))
        )}
      </div>
    </aside>
  );
}

// =============================================================================
// Domain Tabs Component
// =============================================================================

function DomainTabs() {
  const { currentSector, setSector } = useSector();
  
  return (
    <nav className="hidden lg:flex items-center gap-0.5">
      {SECTORS.map((sector) => (
        <button
          key={sector.id}
          onClick={() => setSector(sector.id)}
          className={cn(
            "px-3 py-1.5 text-xs font-medium rounded-md transition-colors",
            currentSector === sector.id
              ? "bg-white/10 text-white"
              : "text-white/50 hover:text-white/80 hover:bg-white/5"
          )}
        >
          {sector.label}
        </button>
      ))}
    </nav>
  );
}

// =============================================================================
// Main Dashboard Content
// =============================================================================

function DashboardContent() {
  const router = useRouter();
  const { user, signOut } = useAuth();
  const { currentSector } = useSector();
  const sectorConfig = SECTORS.find(s => s.id === currentSector) || SECTORS[0];
  
  const {
    conversations,
    currentConversation,
    selectConversation,
    startNewChat,
    deleteConversation,
  } = useConversations();

  // State
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [searchMode, setSearchMode] = useState<'quick' | 'deep'>('quick');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [creditBalance, setCreditBalance] = useState(50);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom
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

  // ==========================================================================
  // Send Message with Real-Time Reasoning (SSE Streaming)
  // ==========================================================================
  
  const handleSendMessage = async (overrideQuery?: string) => {
    const query = overrideQuery || input.trim();
    if (!query || isStreaming) return;

    setInput('');
    setIsStreaming(true);

    // Add user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: query,
      reasoning: [],
      sources: [],
      timestamp: new Date(),
      isStreaming: false,
    };
    setMessages(prev => [...prev, userMessage]);

    // Add assistant message placeholder
    const assistantId = `assistant-${Date.now()}`;
    const assistantMessage: Message = {
      id: assistantId,
      role: 'assistant',
      content: '',
      reasoning: [],
      sources: [],
      timestamp: new Date(),
      isStreaming: true,
    };
    setMessages(prev => [...prev, assistantMessage]);

    try {
      // Use SSE streaming endpoint
      const response = await fetch(`${API_URL}/api/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: query,
          mode: searchMode,
          session_id: user?.id,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No response body');
      }

      let currentReasoning: ReasoningStep[] = [];
      let currentSources: Source[] = [];
      let currentContent = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const event = JSON.parse(line.slice(6));
              const eventType = event.type;
              const eventData = event.data || {};

              if (eventType === 'thinking' || eventType === 'searching' || eventType === 'analyzing' || eventType === 'writing') {
                // Add or update reasoning step
                const stepId = eventData.step_id || `step-${Date.now()}`;
                const existingIndex = currentReasoning.findIndex(s => s.id === stepId);
                
                const step: ReasoningStep = {
                  id: stepId,
                  type: eventType,
                  title: eventData.title || eventType.charAt(0).toUpperCase() + eventType.slice(1),
                  content: eventData.content || '',
                  status: eventData.status || 'active',
                  timestamp: new Date(),
                };

                if (existingIndex >= 0) {
                  currentReasoning[existingIndex] = step;
                } else {
                  currentReasoning.push(step);
                }

                setMessages(prev => prev.map(m =>
                  m.id === assistantId
                    ? { ...m, reasoning: [...currentReasoning] }
                    : m
                ));
              } else if (eventType === 'source') {
                currentSources.push({
                  title: eventData.title || 'Source',
                  url: eventData.url || '',
                  snippet: eventData.snippet || '',
                });

                setMessages(prev => prev.map(m =>
                  m.id === assistantId
                    ? { ...m, sources: [...currentSources] }
                    : m
                ));
              } else if (eventType === 'content') {
                currentContent = eventData.full_content || currentContent + (eventData.chunk || '');

                setMessages(prev => prev.map(m =>
                  m.id === assistantId
                    ? { ...m, content: currentContent }
                    : m
                ));
              } else if (eventType === 'complete') {
                const finalContent = eventData.content || currentContent;
                const creditsUsed = eventData.credits_used || (searchMode === 'quick' ? 2 : 5);

                // Mark all reasoning steps as complete
                currentReasoning = currentReasoning.map(s => ({ ...s, status: 'complete' as const }));

                setMessages(prev => prev.map(m =>
                  m.id === assistantId
                    ? {
                        ...m,
                        content: finalContent,
                        reasoning: currentReasoning,
                        sources: eventData.sources || currentSources,
                        isStreaming: false,
                      }
                    : m
                ));

                setCreditBalance(prev => Math.max(0, prev - creditsUsed));
              } else if (eventType === 'error') {
                throw new Error(eventData.message || 'Unknown error');
              }
            } catch (parseError) {
              // Skip invalid JSON
            }
          }
        }
      }
    } catch (error) {
      console.error('Error:', error);
      
      setMessages(prev => prev.map(m =>
        m.id === assistantId
          ? {
              ...m,
              content: 'I apologize, but there was an error processing your request. Please try again.',
              isStreaming: false,
            }
          : m
      ));
    } finally {
      setIsStreaming(false);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    startNewChat();
  };

  const handleSelectConversation = (conv: Conversation) => {
    selectConversation(conv);
    setMessages([]);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Starter questions
  const starterQuestions = [
    "What are the latest trends in sustainable fashion?",
    "How is AI transforming the beauty industry?",
    "Analyze the luxury market outlook for 2026",
    "What innovations are shaping textile manufacturing?",
  ];

  return (
    <div className="min-h-screen bg-[#070707] flex w-full">
      {/* Chat Sidebar */}
      <ChatSidebar
        conversations={conversations}
        currentConversation={currentConversation}
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        onSelectConversation={handleSelectConversation}
        onDeleteConversation={deleteConversation}
        onNewConversation={handleNewChat}
      />

      {/* Main Content */}
      <main className={cn(
        "flex-1 flex flex-col min-h-screen transition-all duration-200",
        sidebarOpen ? "lg:ml-64" : "lg:ml-14"
      )}>
        {/* Header */}
        <header className="h-[60px] border-b border-white/[0.08] flex items-center justify-between px-4 bg-[#0A0A0A] sticky top-0 z-30">
          <div className="flex items-center gap-4">
            <Link href="/" className="font-luxury text-xl text-white tracking-wide">
              McLeuker
            </Link>
          </div>
          
          <div className="hidden lg:flex items-center absolute left-1/2 -translate-x-1/2">
            <DomainTabs />
          </div>
          
          <div className="flex items-center gap-3">
            <UserMenu collapsed={false} />
          </div>
        </header>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto">
          <div className="max-w-3xl mx-auto px-4 py-6">
            {messages.length === 0 ? (
              /* Empty State - Starter Questions */
              <div className="flex flex-col items-center justify-center min-h-[60vh]">
                <div className="text-center mb-8">
                  <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center mx-auto mb-4">
                    <Brain className="h-8 w-8 text-white" />
                  </div>
                  <h1 className="text-2xl font-bold text-white mb-2">
                    {currentSector === 'all' ? 'McLeuker AI' : sectorConfig.label}
                  </h1>
                  <p className="text-white/50 max-w-md">
                    Ask me anything. I'll reason through your question step by step.
                  </p>
                </div>
                
                <div className="grid gap-3 w-full max-w-xl">
                  {starterQuestions.map((question, i) => (
                    <button
                      key={i}
                      onClick={() => handleSendMessage(question)}
                      className="text-left p-4 rounded-xl bg-white/[0.03] hover:bg-white/[0.06] border border-white/[0.08] hover:border-white/[0.15] text-white/70 hover:text-white/90 transition-all"
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              /* Messages */
              <div className="space-y-6">
                {messages.map(message => (
                  <div key={message.id} className={cn(
                    "flex",
                    message.role === 'user' ? "justify-end" : "justify-start"
                  )}>
                    <div className={cn(
                      "max-w-[90%] rounded-2xl",
                      message.role === 'user'
                        ? "bg-gradient-to-r from-purple-600 to-purple-700 px-4 py-3"
                        : "bg-[#111111] border border-white/[0.08] p-4"
                    )}>
                      {message.role === 'user' ? (
                        <p className="text-white">{message.content}</p>
                      ) : (
                        <div className="space-y-4">
                          {/* Reasoning Steps - Show AI thinking in real-time */}
                          {message.reasoning.length > 0 && (
                            <div className="space-y-1 pb-4 border-b border-white/[0.08]">
                              <div className="flex items-center gap-2 mb-2">
                                <Brain className="h-4 w-4 text-purple-400" />
                                <span className="text-sm font-medium text-white/70">
                                  {message.isStreaming ? 'Reasoning...' : 'Reasoning'}
                                </span>
                              </div>
                              {message.reasoning.map((step, i) => (
                                <ReasoningStepItem 
                                  key={step.id} 
                                  step={step} 
                                  isLatest={i === message.reasoning.length - 1}
                                />
                              ))}
                            </div>
                          )}
                          
                          {/* Response Content */}
                          {message.content ? (
                            <MessageContent 
                              content={message.content} 
                              sources={message.sources} 
                            />
                          ) : message.isStreaming ? (
                            <div className="flex items-center gap-2 text-white/50">
                              <Loader2 className="h-4 w-4 animate-spin" />
                              <span className="text-sm">Generating response...</span>
                            </div>
                          ) : null}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>
        </div>

        {/* Input Area */}
        <div className="border-t border-white/[0.08] p-4 bg-[#0A0A0A]">
          <div className="max-w-3xl mx-auto space-y-3">
            {/* Mode Toggle & Credits */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setSearchMode('quick')}
                  disabled={isStreaming}
                  className={cn(
                    "flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-colors",
                    searchMode === 'quick'
                      ? "bg-white text-black"
                      : "text-white/60 hover:text-white bg-white/5"
                  )}
                >
                  <Zap className="h-3.5 w-3.5" />
                  Quick
                  <span className="text-white/40 ml-1">2</span>
                </button>
                <button
                  onClick={() => setSearchMode('deep')}
                  disabled={isStreaming}
                  className={cn(
                    "flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-colors",
                    searchMode === 'deep'
                      ? "bg-white text-black"
                      : "text-white/60 hover:text-white bg-white/5"
                  )}
                >
                  <Brain className="h-3.5 w-3.5" />
                  Deep
                  <span className="text-white/40 ml-1">5</span>
                </button>
              </div>
              
              <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/5">
                <Coins className="h-3.5 w-3.5 text-yellow-400" />
                <span className="text-xs font-medium text-white/80">{creditBalance}</span>
              </div>
            </div>

            {/* Input */}
            <div className="relative">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask me anything..."
                disabled={isStreaming}
                className={cn(
                  "w-full min-h-[52px] max-h-[200px] px-4 py-3 pr-12",
                  "rounded-xl bg-[#111111] border border-white/[0.10]",
                  "text-white placeholder:text-white/40",
                  "focus:border-white/[0.18] focus:outline-none focus:ring-1 focus:ring-white/[0.06]",
                  "resize-none transition-all",
                  isStreaming && "opacity-50 cursor-not-allowed"
                )}
                rows={1}
              />
              <button
                onClick={() => handleSendMessage()}
                disabled={!input.trim() || isStreaming}
                className={cn(
                  "absolute right-2 bottom-2 h-8 w-8 rounded-lg flex items-center justify-center transition-all",
                  input.trim() && !isStreaming
                    ? "bg-white text-black hover:bg-white/90"
                    : "bg-white/[0.08] text-white/40"
                )}
              >
                {isStreaming ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </button>
            </div>
            
            <p className="text-xs text-white/30 text-center">
              Press Enter to send • Shift + Enter for new line
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}

// =============================================================================
// Export
// =============================================================================

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}
