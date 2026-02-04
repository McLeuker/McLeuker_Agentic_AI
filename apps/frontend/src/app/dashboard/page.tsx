'use client';

import { useState, useEffect, useRef, useCallback } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { 
  Send, 
  Plus, 
  MessageSquare, 
  ChevronLeft,
  ChevronRight,
  Sparkles,
  ExternalLink,
  Lightbulb,
  ArrowRight,
  Brain,
  Search,
  Zap,
  Microscope,
  FileText,
  CheckCircle,
  AlertCircle,
  Loader2,
  LogOut,
  User,
  Trash2,
  Coins,
  RefreshCw
} from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useSector, SECTORS, Sector, DOMAIN_STARTERS } from "@/contexts/SectorContext";
import { useConversations, ChatMessage, Conversation } from "@/hooks/useConversations";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { UserMenu } from "@/components/dashboard/UserMenu";

// =============================================================================
// Types for Streaming Events (matches backend)
// =============================================================================

interface StreamEvent {
  type: 'thinking' | 'planning' | 'searching' | 'analyzing' | 'generating' | 'source' | 'insight' | 'progress' | 'content' | 'complete' | 'error';
  data: any;
  step: number;
  total_steps: number;
  timestamp: string;
}

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
  reasoning?: StreamEvent[];
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://web-production-29f3c.up.railway.app';

// =============================================================================
// Reasoning Panel Component (Manus AI-style)
// =============================================================================

function ReasoningPanel({ 
  events, 
  isActive, 
  onClose 
}: { 
  events: StreamEvent[]; 
  isActive: boolean;
  onClose: () => void;
}) {
  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (panelRef.current) {
      panelRef.current.scrollTop = panelRef.current.scrollHeight;
    }
  }, [events]);

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'thinking': return <Brain className="w-4 h-4" />;
      case 'planning': return <FileText className="w-4 h-4" />;
      case 'searching': return <Search className="w-4 h-4" />;
      case 'analyzing': return <Microscope className="w-4 h-4" />;
      case 'generating': return <Sparkles className="w-4 h-4" />;
      case 'source': return <ExternalLink className="w-4 h-4" />;
      case 'insight': return <Lightbulb className="w-4 h-4" />;
      case 'progress': return <Loader2 className="w-4 h-4 animate-spin" />;
      case 'complete': return <CheckCircle className="w-4 h-4" />;
      case 'error': return <AlertCircle className="w-4 h-4" />;
      default: return <Sparkles className="w-4 h-4" />;
    }
  };

  const getEventColor = (type: string) => {
    switch (type) {
      case 'thinking': return 'text-purple-400 bg-purple-500/10';
      case 'planning': return 'text-blue-400 bg-blue-500/10';
      case 'searching': return 'text-yellow-400 bg-yellow-500/10';
      case 'analyzing': return 'text-cyan-400 bg-cyan-500/10';
      case 'generating': return 'text-green-400 bg-green-500/10';
      case 'source': return 'text-gray-400 bg-gray-500/10';
      case 'insight': return 'text-amber-400 bg-amber-500/10';
      case 'complete': return 'text-emerald-400 bg-emerald-500/10';
      case 'error': return 'text-red-400 bg-red-500/10';
      default: return 'text-gray-400 bg-gray-500/10';
    }
  };

  return (
    <div className="h-full flex flex-col bg-gradient-to-b from-[#0D0D0D] to-[#080808] border-l border-white/[0.08]">
      <div className="h-14 flex items-center justify-between px-4 border-b border-white/[0.08]">
        <div className="flex items-center gap-2">
          <div className={cn(
            "w-2 h-2 rounded-full",
            isActive ? "bg-green-500 animate-pulse" : "bg-gray-500"
          )} />
          <Brain className="w-4 h-4 text-purple-400" />
          <span className="text-sm font-medium text-white/80">Reasoning</span>
        </div>
        <button 
          onClick={onClose}
          className="p-1.5 rounded-md hover:bg-white/[0.08] text-white/40 hover:text-white transition-colors"
        >
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>

      <div ref={panelRef} className="flex-1 overflow-y-auto p-4 space-y-3">
        {events.length === 0 ? (
          <div className="text-center text-white/40 text-sm py-12">
            <Brain className="w-10 h-10 mx-auto mb-3 text-white/20" />
            <p className="font-medium">Reasoning Process</p>
            <p className="text-xs mt-2 text-white/30">
              AI thinking steps will appear here
            </p>
          </div>
        ) : (
          events.map((event, index) => (
            <div 
              key={index} 
              className={cn(
                "flex gap-3 p-3 rounded-lg animate-fadeIn",
                getEventColor(event.type).split(' ')[1]
              )}
            >
              <div className={cn(
                "flex-shrink-0 mt-0.5",
                getEventColor(event.type).split(' ')[0]
              )}>
                {getEventIcon(event.type)}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className={cn(
                    "text-sm font-medium capitalize",
                    getEventColor(event.type).split(' ')[0]
                  )}>
                    {event.type}
                  </span>
                  {event.total_steps > 0 && (
                    <span className="text-xs text-white/30">
                      {event.step}/{event.total_steps}
                    </span>
                  )}
                </div>
                <div className="text-sm text-white/60 mt-1">
                  {event.type === 'thinking' && event.data?.thought}
                  {event.type === 'planning' && (
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <span className={cn(
                          "px-2 py-0.5 rounded text-xs font-medium",
                          event.data?.mode === 'deep' 
                            ? "bg-purple-500/20 text-purple-300" 
                            : "bg-blue-500/20 text-blue-300"
                        )}>
                          {event.data?.mode === 'deep' ? '🔬 Deep' : '⚡ Quick'}
                        </span>
                      </div>
                    </div>
                  )}
                  {event.type === 'searching' && event.data?.message}
                  {event.type === 'source' && (
                    <a 
                      href={event.data?.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-blue-400 hover:underline truncate block text-xs"
                    >
                      📄 {event.data?.title}
                    </a>
                  )}
                  {event.type === 'analyzing' && event.data?.message}
                  {event.type === 'generating' && event.data?.message}
                  {event.type === 'complete' && (
                    <div className="text-emerald-400 text-xs">
                      ✓ Generated with {event.data?.sources_used || 0} sources
                    </div>
                  )}
                  {event.type === 'error' && (
                    <div className="text-red-400 text-xs">{event.data?.message}</div>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {isActive && events.length > 0 && (
        <div className="p-3 border-t border-white/[0.08] bg-white/[0.02]">
          <div className="flex items-center gap-2">
            <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
            <span className="text-xs text-white/60">Processing...</span>
          </div>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Search Mode Selector Component
// =============================================================================

function SearchModeSelector({ 
  mode, 
  onModeChange 
}: { 
  mode: 'quick' | 'deep'; 
  onModeChange: (mode: 'quick' | 'deep') => void;
}) {
  return (
    <div className="flex items-center gap-1 bg-white/[0.05] rounded-lg p-1">
      <button
        onClick={() => onModeChange('quick')}
        className={cn(
          "flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-all",
          mode === 'quick' 
            ? "bg-blue-600 text-white shadow-lg shadow-blue-600/20" 
            : "text-white/60 hover:text-white hover:bg-white/[0.08]"
        )}
      >
        <Zap className="w-3.5 h-3.5" />
        Quick
      </button>
      <button
        onClick={() => onModeChange('deep')}
        className={cn(
          "flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-all",
          mode === 'deep' 
            ? "bg-purple-600 text-white shadow-lg shadow-purple-600/20" 
            : "text-white/60 hover:text-white hover:bg-white/[0.08]"
        )}
      >
        <Microscope className="w-3.5 h-3.5" />
        Deep
      </button>
    </div>
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
// Domain Starter Panel - Empty State
// =============================================================================

function DomainStarterPanel({ 
  onSelectPrompt 
}: { 
  onSelectPrompt: (prompt: string) => void;
}) {
  const { currentSector, getSectorConfig, getStarters } = useSector();
  const config = getSectorConfig();
  const starters = getStarters();

  return (
    <div className="text-center py-12 px-6 animate-fade-in">
      <div className="w-20 h-20 rounded-full bg-gradient-to-br from-purple-600/20 to-pink-600/20 border border-white/[0.08] flex items-center justify-center mx-auto mb-6">
        <Sparkles className="w-10 h-10 text-purple-400" />
      </div>
      
      <h1 className="text-3xl md:text-4xl font-serif text-white mb-3">
        {config.label}
      </h1>
      <p className="text-white/60 text-sm max-w-lg mx-auto mb-8">
        {config.tagline}
      </p>

      {/* Starter Questions */}
      <div className="max-w-xl mx-auto">
        <p className="text-xs text-white/40 uppercase tracking-wider mb-4">
          Explore {config.label}
        </p>
        <div className="grid gap-2">
          {starters.map((question, index) => (
            <button
              key={index}
              onClick={() => onSelectPrompt(question)}
              className={cn(
                "group flex items-center justify-between gap-4 p-4 rounded-lg",
                "bg-white/[0.03] border border-white/[0.08]",
                "hover:border-white/[0.15] hover:bg-white/[0.06]",
                "transition-all duration-200",
                "text-left"
              )}
            >
              <span className="text-[15px] text-white/90">
                {question}
              </span>
              <ArrowRight className={cn(
                "h-4 w-4 text-white/40 shrink-0",
                "group-hover:text-white group-hover:translate-x-0.5",
                "transition-all duration-200"
              )} />
            </button>
          ))}
        </div>
      </div>

      {/* Minimal branding */}
      <div className="mt-8 pt-6 border-t border-white/[0.08] max-w-xl mx-auto">
        <p className="text-xs text-white/40 text-center">
          Powered by McLeuker AI • {config.label} Intelligence Mode
        </p>
      </div>
    </div>
  );
}

// =============================================================================
// Dashboard Content Component
// =============================================================================

function DashboardContent() {
  const router = useRouter();
  const { user, signOut } = useAuth();
  const { currentSector, getSectorConfig, getDomainSystemPrompt } = useSector();
  const sectorConfig = getSectorConfig();
  const {
    conversations,
    currentConversation,
    messages,
    loading: conversationsLoading,
    createConversation,
    saveMessage,
    updateConversationTitle,
    deleteConversation,
    selectConversation,
    startNewChat,
  } = useConversations();

  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [reasoningOpen, setReasoningOpen] = useState(true);
  const [input, setInput] = useState('');
  const [searchMode, setSearchMode] = useState<'quick' | 'deep'>('quick');
  const [localMessages, setLocalMessages] = useState<LocalMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [reasoningEvents, setReasoningEvents] = useState<StreamEvent[]>([]);
  const [creditBalance, setCreditBalance] = useState(50);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Scroll to bottom when messages change
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

  // Clear messages when switching domains (optional - you may want to keep them)
  useEffect(() => {
    // Optionally clear messages when switching domains
    // setLocalMessages([]);
    // setReasoningEvents([]);
  }, [currentSector]);

  const handleSendMessage = async (messageText?: string) => {
    const text = messageText || input.trim();
    if (!text || isStreaming) return;

    const userMessage: LocalMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: new Date(),
    };

    setLocalMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsStreaming(true);
    setReasoningEvents([]);

    // Create assistant placeholder
    const assistantId = `assistant-${Date.now()}`;
    const assistantMessage: LocalMessage = {
      id: assistantId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isStreaming: true,
      reasoning: [],
    };
    setLocalMessages(prev => [...prev, assistantMessage]);

    try {
      // Get domain context
      const domainPrompt = getDomainSystemPrompt();
      const fullQuery = domainPrompt ? `${text}${domainPrompt}` : text;

      const response = await fetch(`${API_URL}/api/research/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user?.id || 'anonymous'}`,
        },
        body: JSON.stringify({
          query: fullQuery,
          mode: searchMode,
          domain: currentSector,
          user_id: user?.id,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let accumulatedContent = '';
      let sources: Array<{ title: string; url: string }> = [];
      let keyInsights: KeyInsight[] = [];
      let followUpQuestions: string[] = [];

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                
                // Add to reasoning events
                if (data.type !== 'content') {
                  setReasoningEvents(prev => [...prev, data]);
                }

                // Handle different event types
                switch (data.type) {
                  case 'content':
                    accumulatedContent += data.data?.chunk || '';
                    setLocalMessages(prev => prev.map(msg => 
                      msg.id === assistantId 
                        ? { ...msg, content: accumulatedContent }
                        : msg
                    ));
                    break;
                  case 'source':
                    if (data.data?.url && data.data?.title) {
                      sources.push({ title: data.data.title, url: data.data.url });
                    }
                    break;
                  case 'insight':
                    if (data.data) {
                      keyInsights.push(data.data);
                    }
                    break;
                  case 'complete':
                    if (data.data?.follow_up_questions) {
                      followUpQuestions = data.data.follow_up_questions;
                    }
                    if (data.data?.credits_used) {
                      setCreditBalance(prev => Math.max(0, prev - data.data.credits_used));
                    }
                    break;
                }
              } catch (e) {
                console.error('Error parsing SSE data:', e);
              }
            }
          }
        }
      }

      // Finalize message
      setLocalMessages(prev => prev.map(msg => 
        msg.id === assistantId 
          ? { 
              ...msg, 
              content: accumulatedContent || 'I apologize, but I was unable to generate a response. Please try again.',
              isStreaming: false,
              sources,
              keyInsights,
              followUpQuestions,
              reasoning: reasoningEvents,
            }
          : msg
      ));

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
    setReasoningEvents([]);
    startNewChat();
  };

  const handleSelectConversation = (conv: Conversation) => {
    selectConversation(conv);
    // Load messages for this conversation
    // For now, just clear local messages
    setLocalMessages([]);
    setReasoningEvents([]);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-[#070707] flex w-full overflow-x-hidden">
      {/* Sidebar */}
      <aside className={cn(
        "fixed left-0 top-0 h-screen z-40",
        "bg-gradient-to-b from-[#0D0D0D] to-[#080808]",
        "border-r border-white/[0.08]",
        "transition-all duration-200 flex flex-col",
        sidebarOpen ? "w-64" : "w-14"
      )}>
        {/* Logo */}
        <div className="h-14 flex items-center justify-between px-4 border-b border-white/[0.08]">
          {sidebarOpen && (
            <Link href="/" className="font-luxury text-lg text-white tracking-wide">
              McLeuker
            </Link>
          )}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-md hover:bg-white/[0.08] text-white/60 hover:text-white transition-colors"
          >
            {sidebarOpen ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
          </button>
        </div>

        {/* New Chat Button */}
        <div className="p-3">
          <button
            onClick={handleNewChat}
            className={cn(
              "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg",
              "bg-gradient-to-r from-blue-600/20 to-purple-600/20",
              "border border-white/[0.08]",
              "text-white/80 hover:text-white",
              "hover:from-blue-600/30 hover:to-purple-600/30",
              "transition-all",
              !sidebarOpen && "justify-center"
            )}
          >
            <Plus className="w-4 h-4" />
            {sidebarOpen && <span className="text-sm">New Chat</span>}
          </button>
        </div>

        {/* Conversations List */}
        {sidebarOpen && (
          <div className="px-3 py-2 overflow-y-auto flex-1">
            <p className="text-xs text-white/40 uppercase tracking-wider mb-2 px-2">Recent</p>
            <div className="space-y-1">
              {conversations.map(conv => (
                <div key={conv.id} className="group relative">
                  <button
                    onClick={() => handleSelectConversation(conv)}
                    className={cn(
                      "w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left",
                      "hover:bg-white/[0.08] transition-colors",
                      currentConversation?.id === conv.id 
                        ? "bg-white/[0.10] text-white" 
                        : "text-white/60"
                    )}
                  >
                    <MessageSquare className="w-4 h-4 flex-shrink-0" />
                    <span className="text-sm truncate flex-1">{conv.title}</span>
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteConversation(conv.id);
                    }}
                    className="absolute right-2 top-1/2 -translate-y-1/2 p-1 rounded opacity-0 group-hover:opacity-100 hover:bg-red-500/20 text-white/40 hover:text-red-400 transition-all"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* User Section */}
        {user && (
          <div className="p-3 border-t border-white/[0.08]">
            <UserMenu collapsed={!sidebarOpen} />
          </div>
        )}
      </aside>

      {/* Main Content */}
      <main className={cn(
        "flex-1 flex flex-col min-h-screen transition-all duration-200",
        sidebarOpen ? "ml-64" : "ml-14",
        reasoningOpen ? "mr-80" : "mr-0"
      )}>
        {/* Top Navigation with Domain Tabs */}
        <header className="h-[72px] border-b border-white/[0.08] flex items-center justify-between px-6 bg-gradient-to-b from-[#0F0F0F] to-[#0A0A0A] sticky top-0 z-30">
          {/* Left: Logo (hidden on desktop since sidebar has it) */}
          <div className="lg:hidden">
            <Link href="/" className="font-luxury text-lg text-white tracking-wide">
              McLeuker
            </Link>
          </div>
          
          {/* Center: Domain Tabs */}
          <div className="hidden lg:flex items-center absolute left-1/2 -translate-x-1/2">
            <DomainTabs />
          </div>
          
          {/* Right: Credits & Mode */}
          <div className="flex items-center gap-4 ml-auto">
            {/* Credits Display */}
            <Link
              href="/billing"
              className="hidden sm:flex items-center gap-1.5 px-2.5 py-1.5 rounded-md bg-white/5 hover:bg-white/10 border border-white/[0.08] transition-colors"
            >
              <Coins className="h-3.5 w-3.5 text-white/50" />
              <span className="text-xs font-medium text-white/80">{creditBalance} credits</span>
            </Link>
            
            <SearchModeSelector mode={searchMode} onModeChange={setSearchMode} />
            
            <button
              onClick={() => setReasoningOpen(!reasoningOpen)}
              className={cn(
                "flex items-center gap-2 px-3 py-1.5 rounded-lg transition-all",
                reasoningOpen 
                  ? "bg-purple-600/20 text-purple-400 border border-purple-500/30" 
                  : "bg-white/[0.05] text-white/60 hover:bg-white/[0.08] hover:text-white"
              )}
            >
              <Brain className="w-4 h-4" />
              <span className="text-sm hidden sm:inline">Reasoning</span>
            </button>
          </div>
        </header>

        {/* Mobile Domain Selector */}
        <MobileDomainSelector />

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto px-6 py-8">
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
                      <div className="flex items-center gap-2">
                        <Loader2 className="w-4 h-4 animate-spin text-white/60" />
                        <span className="text-white/60 text-sm">Generating response...</span>
                      </div>
                    ) : (
                      <p className={cn(
                        "leading-relaxed whitespace-pre-wrap",
                        message.role === 'user' ? "text-white" : "text-white/[0.88]"
                      )}>
                        {message.content}
                      </p>
                    )}

                    {/* Key Insights */}
                    {!message.isStreaming && message.keyInsights && message.keyInsights.length > 0 && (
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
                    {!message.isStreaming && message.sources && message.sources.length > 0 && (
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
                    {!message.isStreaming && message.followUpQuestions && message.followUpQuestions.length > 0 && (
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
                  </div>
                </div>
              ))
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="border-t border-white/[0.08] p-4 bg-gradient-to-b from-[#0A0A0A] to-[#070707]">
          <div className="max-w-3xl mx-auto">
            <div className="relative">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={sectorConfig.placeholder || `Ask McLeuker AI (${searchMode} mode)...`}
                disabled={isStreaming}
                className={cn(
                  "w-full min-h-[56px] max-h-[200px] px-5 py-4 pr-14",
                  "bg-white/[0.05] border border-white/[0.12] rounded-2xl",
                  "text-white placeholder:text-white/40",
                  "focus:outline-none focus:border-white/[0.25] focus:bg-white/[0.08]",
                  "resize-none transition-all",
                  isStreaming && "opacity-50 cursor-not-allowed"
                )}
                rows={1}
              />
              <button
                onClick={() => handleSendMessage()}
                disabled={!input.trim() || isStreaming}
                className={cn(
                  "absolute right-3 bottom-3 p-2.5 rounded-xl",
                  "bg-gradient-to-r from-blue-600 to-purple-600",
                  "text-white",
                  "hover:from-blue-500 hover:to-purple-500",
                  "disabled:opacity-50 disabled:cursor-not-allowed",
                  "transition-all"
                )}
              >
                {isStreaming ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </button>
            </div>
            <div className="flex items-center justify-between mt-2 px-2">
              <p className="text-xs text-white/40">
                {searchMode === 'quick' ? '4-12' : '50'} credits • Press Enter to send
              </p>
              <p className="text-xs text-white/40">
                Shift + Enter for new line
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Reasoning Panel */}
      {reasoningOpen && (
        <aside className="fixed right-0 top-0 h-screen w-80 z-40">
          <ReasoningPanel 
            events={reasoningEvents} 
            isActive={isStreaming} 
            onClose={() => setReasoningOpen(false)}
          />
        </aside>
      )}
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
