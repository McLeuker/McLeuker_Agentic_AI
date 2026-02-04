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
  Lightbulb,
  ArrowRight,
  Zap,
  Brain,
  Loader2,
  Trash2,
  Coins,
  Search,
  X,
  PanelLeftClose,
  PanelLeft,
  MoreHorizontal,
  CheckCircle2,
  Circle
} from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useSector, SECTORS, Sector, DOMAIN_STARTERS } from "@/contexts/SectorContext";
import { useConversations, Conversation } from "@/hooks/useConversations";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { UserMenu } from "@/components/dashboard/UserMenu";
import { ReasoningPanel, StreamEvent } from "@/components/reasoning/ReasoningPanel";
import { StructuredOutput, ResponseData } from "@/components/reasoning/StructuredOutput";

// =============================================================================
// Types
// =============================================================================

interface KeyInsight {
  id?: string;
  icon?: string;
  title?: string;
  text?: string;
  description?: string;
  importance: string;
}

interface LocalMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: Array<{ title: string; url: string; }>;
  keyInsights?: KeyInsight[];
  followUpQuestions?: string[];
  isStreaming?: boolean;
  responseData?: ResponseData;
  reasoningEvents?: StreamEvent[];
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://web-production-29f3c.up.railway.app';

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
            "focus:outline-none focus:ring-2 focus:ring-white/20 focus:ring-offset-2 focus:ring-offset-[#0A0A0A]",
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
// Mobile Domain Selector
// =============================================================================

function MobileDomainSelector() {
  const { currentSector, setSector } = useSector();
  
  return (
    <div className="lg:hidden border-t border-white/[0.08] px-4 py-2 overflow-x-auto bg-[#0A0A0A]">
      <div className="flex items-center gap-1 min-w-max">
        {SECTORS.map((sector) => (
          <button
            key={sector.id}
            onClick={() => setSector(sector.id)}
            className={cn(
              "px-2.5 py-1 text-xs font-medium rounded-md transition-colors whitespace-nowrap",
              "focus:outline-none focus:ring-2 focus:ring-white/20",
              currentSector === sector.id
                ? "bg-white/10 text-white"
                : "text-white/50 hover:text-white/80"
            )}
          >
            {sector.label}
          </button>
        ))}
      </div>
    </div>
  );
}

// =============================================================================
// Research Mode Toggle Component
// =============================================================================

function ResearchModeToggle({ 
  mode, 
  onModeChange,
  disabled = false
}: { 
  mode: 'quick' | 'deep'; 
  onModeChange: (mode: 'quick' | 'deep') => void;
  disabled?: boolean;
}) {
  return (
    <div className="inline-flex items-center rounded-full bg-white/10 p-1">
      <button
        type="button"
        onClick={() => onModeChange('quick')}
        disabled={disabled}
        className={cn(
          "flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-full transition-colors",
          mode === 'quick'
            ? "bg-white text-black shadow-sm"
            : "text-white/60 hover:text-white",
          disabled && "opacity-50 cursor-not-allowed"
        )}
      >
        <Zap className="h-3.5 w-3.5" />
        Quick
        <span className={cn(
          "flex items-center gap-0.5",
          mode === 'quick' ? "text-black/50" : "text-white/40"
        )}>
          <Coins className="h-3 w-3" />2
        </span>
      </button>

      <button
        type="button"
        onClick={() => onModeChange('deep')}
        disabled={disabled}
        className={cn(
          "flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-full transition-colors",
          mode === 'deep'
            ? "bg-white text-black shadow-sm"
            : "text-white/60 hover:text-white",
          disabled && "opacity-50 cursor-not-allowed"
        )}
      >
        <Brain className="h-3.5 w-3.5" />
        Deep
        <span className={cn(
          "flex items-center gap-0.5",
          mode === 'deep' ? "text-black/50" : "text-white/40"
        )}>
          <Coins className="h-3 w-3" />5
        </span>
      </button>
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
      <aside className={cn(
        "hidden lg:flex w-14 flex-col fixed left-0 top-[72px] bottom-0 z-40",
        "bg-gradient-to-b from-[#0D0D0D] to-[#080808]",
        "border-r border-white/[0.08]"
      )}>
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
    <aside className={cn(
      "hidden lg:flex w-72 flex-col fixed left-0 top-[72px] bottom-0 z-40",
      "bg-gradient-to-b from-[#0D0D0D] to-[#080808]",
      "border-r border-white/[0.08]"
    )}>
      <div className="px-4 pt-5 pb-3 flex items-center justify-between shrink-0">
        <span className="font-medium text-[13px] text-white/80">Chat History</span>
        <button
          onClick={onToggle}
          className="h-8 w-8 flex items-center justify-center text-white/50 hover:text-white hover:bg-white/[0.08] rounded-lg transition-colors"
        >
          <PanelLeftClose className="h-4 w-4" />
        </button>
      </div>

      {onNewConversation && (
        <div className="px-4 pb-3 shrink-0">
          <button
            onClick={onNewConversation}
            className={cn(
              "w-full justify-center gap-2 flex items-center",
              "bg-white text-black hover:bg-white/90",
              "h-10 rounded-full text-[13px] font-medium",
              "transition-colors"
            )}
          >
            <Plus className="h-4 w-4" />
            New Chat
          </button>
        </div>
      )}

      <div className="px-4 pb-3 shrink-0">
        <div className="relative">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-white/40" />
          <input
            placeholder="Search chats..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className={cn(
              "w-full pl-10 pr-10 h-10 text-[13px]",
              "bg-white/[0.05] border border-white/[0.08] rounded-full",
              "text-white placeholder:text-white/35",
              "focus:border-white/[0.15] focus:outline-none focus:ring-1 focus:ring-white/[0.06]",
              "transition-all"
            )}
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery("")}
              className="absolute right-3.5 top-1/2 -translate-y-1/2 text-white/40 hover:text-white/70 transition-colors"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          )}
        </div>
      </div>

      <div className="px-4 pb-2 shrink-0">
        <p className="text-[10px] font-medium text-white/40 uppercase tracking-wider">
          {filteredConversations.length} {filteredConversations.length === 1 ? 'chat' : 'chats'}
        </p>
      </div>

      <div className="flex-1 overflow-y-auto px-4 pb-4 space-y-2">
        {filteredConversations.length === 0 ? (
          <div className="px-2 py-8 text-center">
            <MessageSquare className="h-8 w-8 text-white/25 mx-auto mb-3" />
            <p className="text-[13px] text-white/50">
              {searchQuery ? "No matching chats" : "No chats yet"}
            </p>
            <p className="text-[11px] text-white/35 mt-1">
              {searchQuery ? "Try a different search" : "Start a new chat to begin"}
            </p>
          </div>
        ) : (
          filteredConversations.map((conv) => (
            <div
              key={conv.id}
              className={cn(
                "group relative w-full text-left px-4 py-3 rounded-xl min-h-fit",
                "transition-all cursor-pointer",
                currentConversation?.id === conv.id
                  ? "bg-white/[0.08] border border-white/[0.12]"
                  : "hover:bg-white/[0.04] border border-transparent"
              )}
              onClick={() => onSelectConversation(conv)}
            >
              <div className="flex items-start gap-3">
                <MessageSquare className="h-4 w-4 text-white/40 mt-0.5 shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-[13px] font-medium text-white/80 truncate">
                    {conv.title}
                  </p>
                  <p className="text-[11px] text-white/40 mt-0.5">
                    {new Date(conv.updatedAt).toLocaleDateString()}
                  </p>
                </div>
              </div>
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
// Domain Starter Panel
// =============================================================================

function DomainStarterPanel({ onSelectPrompt }: { onSelectPrompt: (prompt: string) => void }) {
  const { currentSector, getStarters } = useSector();
  const sectorConfig = SECTORS.find(s => s.id === currentSector) || SECTORS[0];
  
  const starterPrompts = getStarters();

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] px-4">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-white mb-3">
          {currentSector === 'all' ? 'McLeuker AI' : sectorConfig.label}
        </h1>
        <p className="text-white/50 max-w-md">
          {sectorConfig.tagline || 'Your AI-powered fashion intelligence platform'}
        </p>
      </div>
      
      <div className="grid gap-3 w-full max-w-2xl">
        {starterPrompts.map((prompt, index) => (
          <button
            key={index}
            onClick={() => onSelectPrompt(prompt)}
            className={cn(
              "text-left p-4 rounded-xl",
              "bg-white/[0.03] hover:bg-white/[0.06] border border-white/[0.08] hover:border-white/[0.15]",
              "text-white/70 hover:text-white/90",
              "transition-all duration-200 group"
            )}
          >
            <div className="flex items-center justify-between">
              <span className="text-sm">{prompt}</span>
              <ArrowRight className="h-4 w-4 text-white/30 group-hover:text-white/60 group-hover:translate-x-1 transition-all" />
            </div>
          </button>
        ))}
      </div>
    </div>
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
    loading: conversationsLoading,
    selectConversation,
    startNewChat,
    deleteConversation,
  } = useConversations();

  // State
  const [input, setInput] = useState('');
  const [localMessages, setLocalMessages] = useState<LocalMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [searchMode, setSearchMode] = useState<'quick' | 'deep'>('quick');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [creditBalance, setCreditBalance] = useState(50);
  const [showReasoningPanel, setShowReasoningPanel] = useState(false);
  const [currentStreamEvents, setCurrentStreamEvents] = useState<StreamEvent[]>([]);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [localMessages]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [input]);

  // ==========================================================================
  // Send Message with SSE Streaming (Manus AI Style)
  // ==========================================================================
  
  const handleSendMessage = async (overrideQuery?: string) => {
    const fullQuery = overrideQuery || input.trim();
    if (!fullQuery || isStreaming) return;

    setInput('');
    setIsStreaming(true);
    setShowReasoningPanel(true);
    setCurrentStreamEvents([]);

    // Add user message
    const userMessageId = Date.now().toString();
    const userMessage: LocalMessage = {
      id: userMessageId,
      role: 'user',
      content: fullQuery,
      timestamp: new Date(),
    };
    setLocalMessages(prev => [...prev, userMessage]);

    // Add assistant message placeholder
    const assistantId = (Date.now() + 1).toString();
    const assistantMessage: LocalMessage = {
      id: assistantId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isStreaming: true,
      reasoningEvents: [],
    };
    setLocalMessages(prev => [...prev, assistantMessage]);

    try {
      // Use SSE streaming endpoint
      const response = await fetch(`${API_URL}/api/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: fullQuery,
          mode: searchMode,
          domain_filter: currentSector !== 'all' ? currentSector : null,
          session_id: user?.id || null,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      const collectedEvents: StreamEvent[] = [];

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const eventData = JSON.parse(line.slice(6));
                collectedEvents.push(eventData);
                setCurrentStreamEvents([...collectedEvents]);

                // Update assistant message with events
                setLocalMessages(prev => prev.map(msg =>
                  msg.id === assistantId
                    ? { ...msg, reasoningEvents: [...collectedEvents] }
                    : msg
                ));

                // Handle complete event
                if (eventData.type === 'complete') {
                  const responseData = eventData.data.response;
                  const creditsUsed = eventData.data.credits_used || 2;

                  // Update credit balance
                  setCreditBalance(prev => Math.max(0, prev - creditsUsed));

                  // Update assistant message with final response
                  setLocalMessages(prev => prev.map(msg =>
                    msg.id === assistantId
                      ? {
                          ...msg,
                          content: responseData.main_content || responseData.summary || '',
                          isStreaming: false,
                          sources: responseData.sources?.map((s: any) => ({
                            title: s.title || 'Source',
                            url: s.url || '#'
                          })) || [],
                          keyInsights: responseData.key_insights || [],
                          followUpQuestions: responseData.follow_up_questions || [],
                          responseData: responseData,
                          reasoningEvents: collectedEvents,
                        }
                      : msg
                  ));
                }

                // Handle error event
                if (eventData.type === 'error') {
                  throw new Error(eventData.data.message || 'An error occurred');
                }
              } catch (parseError) {
                // Skip invalid JSON
              }
            }
          }
        }
      }

    } catch (error) {
      console.error('Error sending message:', error);
      setLocalMessages(prev => prev.map(msg =>
        msg.id === assistantId
          ? {
              ...msg,
              content: 'I apologize, but there was an error processing your request. Please try again.',
              isStreaming: false,
            }
          : msg
      ));
    } finally {
      setIsStreaming(false);
    }
  };

  const handleFollowUpClick = (question: string) => {
    handleSendMessage(question);
  };

  const handleNewChat = () => {
    setLocalMessages([]);
    setCurrentStreamEvents([]);
    setShowReasoningPanel(false);
    startNewChat();
  };

  const handleSelectConversation = (conv: Conversation) => {
    selectConversation(conv);
    setLocalMessages([]);
    setCurrentStreamEvents([]);
    setShowReasoningPanel(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-[#070707] flex w-full overflow-x-hidden">
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
        sidebarOpen ? "lg:ml-72" : "lg:ml-14"
      )}>
        {/* Top Navigation */}
        <header className="h-[72px] border-b border-white/[0.08] flex items-center justify-between px-6 bg-gradient-to-b from-[#0F0F0F] to-[#0A0A0A] sticky top-0 z-30">
          <div className="flex items-center gap-4 shrink-0">
            <Link href="/" className="font-luxury text-xl lg:text-2xl text-white tracking-[0.02em]">
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

        <MobileDomainSelector />

        {/* Messages Area */}
        <div className="flex-1 flex">
          {/* Chat Messages */}
          <div className={cn(
            "flex-1 overflow-y-auto px-6 py-8 transition-all duration-300",
            showReasoningPanel && isStreaming ? "lg:pr-[420px]" : ""
          )}>
            <div className="max-w-3xl mx-auto space-y-6">
              {localMessages.length === 0 ? (
                <DomainStarterPanel onSelectPrompt={handleSendMessage} />
              ) : (
                localMessages.map(message => (
                  <div key={message.id} className={cn(
                    "flex",
                    message.role === 'user' ? "justify-end" : "justify-start"
                  )}>
                    <div className={cn(
                      "max-w-[85%] rounded-[20px] p-5",
                      message.role === 'user'
                        ? "bg-gradient-to-r from-blue-600 to-blue-700 text-white"
                        : "bg-gradient-to-b from-[#1A1A1A] to-[#141414] border border-white/[0.08]"
                    )}>
                      {message.isStreaming ? (
                        <div className="space-y-3">
                          <div className="flex items-center gap-2">
                            <Brain className="w-4 h-4 text-purple-400 animate-pulse" />
                            <span className="text-white/80 text-sm font-medium">AI is thinking...</span>
                          </div>
                          
                          {/* Show current task step */}
                          {message.reasoningEvents && message.reasoningEvents.length > 0 && (
                            <div className="space-y-2">
                              {message.reasoningEvents
                                .filter(e => e.type === 'task_update' && e.data.status === 'in_progress')
                                .slice(-1)
                                .map((event, i) => (
                                  <div key={i} className="flex items-center gap-2 text-sm text-white/60">
                                    <Loader2 className="w-3 h-3 animate-spin" />
                                    <span>{event.data.title}</span>
                                  </div>
                                ))}
                              
                              {/* Show completed steps */}
                              {message.reasoningEvents
                                .filter(e => e.type === 'task_update' && e.data.status === 'completed')
                                .map((event, i) => (
                                  <div key={i} className="flex items-center gap-2 text-sm text-white/40">
                                    <CheckCircle2 className="w-3 h-3 text-green-400" />
                                    <span>{event.data.title}</span>
                                  </div>
                                ))}
                            </div>
                          )}
                        </div>
                      ) : message.responseData ? (
                        <StructuredOutput
                          response={message.responseData}
                          onFollowUp={handleFollowUpClick}
                        />
                      ) : (
                        <>
                          <p className={cn(
                            "leading-relaxed whitespace-pre-wrap",
                            message.role === 'user' ? "text-white" : "text-white/[0.88]"
                          )}>
                            {message.content}
                          </p>

                          {/* Key Insights */}
                          {message.keyInsights && message.keyInsights.length > 0 && (
                            <div className="mt-5 pt-5 border-t border-white/[0.08]">
                              <div className="flex items-center gap-2 mb-3">
                                <Lightbulb className="w-4 h-4 text-amber-400" />
                                <span className="text-sm font-medium text-white/70">Key Insights</span>
                              </div>
                              <ul className="space-y-3">
                                {message.keyInsights.map((insight, i) => (
                                  <li key={i} className={cn(
                                    "flex items-start gap-3 text-sm p-3 rounded-lg",
                                    insight.importance === 'high'
                                      ? "bg-amber-500/10 border border-amber-500/20"
                                      : "bg-white/[0.03]"
                                  )}>
                                    <span className="text-lg">{insight.icon || '💡'}</span>
                                    <div>
                                      {insight.title && (
                                        <span className="font-medium text-white/80">{insight.title}: </span>
                                      )}
                                      <span className="text-white/60">
                                        {insight.text || insight.description}
                                      </span>
                                    </div>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {/* Sources */}
                          {message.sources && message.sources.length > 0 && (
                            <div className="mt-5 pt-5 border-t border-white/[0.08]">
                              <div className="flex items-center gap-2 mb-3">
                                <ExternalLink className="w-4 h-4 text-blue-400" />
                                <span className="text-sm font-medium text-white/70">Sources</span>
                              </div>
                              <div className="flex flex-wrap gap-2">
                                {message.sources.map((source, i) => (
                                  <a
                                    key={i}
                                    href={source.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-xs px-3 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-300 hover:bg-blue-500/20 transition-colors"
                                  >
                                    {source.title}
                                  </a>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Follow-up Questions */}
                          {message.followUpQuestions && message.followUpQuestions.length > 0 && (
                            <div className="mt-5 pt-5 border-t border-white/[0.08]">
                              <p className="text-xs text-white/50 mb-3">Explore further:</p>
                              <div className="flex flex-wrap gap-2">
                                {message.followUpQuestions.map((question, i) => (
                                  <button
                                    key={i}
                                    onClick={() => handleFollowUpClick(question)}
                                    className="text-xs px-3 py-1.5 rounded-full border border-white/[0.12] text-white/70 hover:bg-white/[0.08] hover:text-white transition-colors flex items-center gap-1"
                                  >
                                    {question}
                                    <ArrowRight className="w-3 h-3" />
                                  </button>
                                ))}
                              </div>
                            </div>
                          )}
                        </>
                      )}
                    </div>
                  </div>
                ))
              )}

              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Reasoning Panel (Fixed Right) */}
          {showReasoningPanel && isStreaming && (
            <div className="hidden lg:block fixed right-6 top-[100px] bottom-[180px] w-[400px] z-20">
              <ReasoningPanel
                events={currentStreamEvents}
                isStreaming={isStreaming}
                onClose={() => setShowReasoningPanel(false)}
                className="h-full"
              />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t border-white/[0.08] p-4 bg-gradient-to-b from-[#0A0A0A] to-[#070707]">
          <div className="max-w-3xl mx-auto space-y-3">
            <div className="flex items-center justify-between gap-2 flex-wrap w-full">
              <ResearchModeToggle
                mode={searchMode}
                onModeChange={setSearchMode}
                disabled={isStreaming}
              />
              <div className="flex items-center gap-2">
                <Link
                  href="/billing"
                  className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-full bg-white/5 hover:bg-white/10 border border-white/[0.08] transition-colors"
                >
                  <Coins className="h-3.5 w-3.5 text-white/50" />
                  <span className="text-xs font-medium text-white/80">{creditBalance} credits</span>
                </Link>
              </div>
            </div>

            <div className="relative">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={
                  searchMode === 'deep'
                    ? "Describe your research task in detail for comprehensive analysis..."
                    : sectorConfig.placeholder || "Ask McLeuker AI about fashion intelligence..."
                }
                disabled={isStreaming}
                className={cn(
                  "w-full min-h-[60px] max-h-[200px] px-5 py-4 pr-14",
                  "rounded-[20px]",
                  "bg-gradient-to-b from-[#1B1B1B] to-[#111111]",
                  "border border-white/[0.10]",
                  "text-white/[0.88]",
                  "placeholder:text-white/40",
                  "shadow-[0_4px_16px_rgba(0,0,0,0.3)]",
                  "focus:border-white/[0.18]",
                  "focus:outline-none focus:ring-[3px] focus:ring-white/[0.06]",
                  "resize-none transition-all",
                  isStreaming && "opacity-50 cursor-not-allowed"
                )}
                rows={2}
              />
              <button
                onClick={() => handleSendMessage()}
                disabled={!input.trim() || isStreaming}
                className={cn(
                  "absolute right-3 bottom-3 h-9 w-9 rounded-full flex items-center justify-center",
                  "transition-all",
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

            <div className="flex items-center justify-between text-[11px] text-white/50 px-1">
              <span>
                {searchMode === 'deep' ? '5 credits' : '2 credits'} • Press Enter to send
              </span>
              <span className="hidden sm:inline">Shift + Enter for new line</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

// =============================================================================
// Dashboard Page with Protected Route
// =============================================================================

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}
