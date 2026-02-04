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
  Trash2
} from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useConversations, ChatMessage, Conversation } from "@/hooks/useConversations";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";

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
// Dashboard Content Component
// =============================================================================

function DashboardContent() {
  const router = useRouter();
  const { user, signOut } = useAuth();
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
    setCurrentConversation,
  } = useConversations();

  const [localMessages, setLocalMessages] = useState<LocalMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [reasoningOpen, setReasoningOpen] = useState(true);
  const [searchMode, setSearchMode] = useState<'quick' | 'deep'>('quick');
  const [reasoningEvents, setReasoningEvents] = useState<StreamEvent[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Sync local messages with Supabase messages
  useEffect(() => {
    if (messages.length > 0) {
      const converted: LocalMessage[] = messages.map(msg => ({
        id: msg.id,
        role: msg.role,
        content: msg.content,
        timestamp: new Date(msg.created_at),
        sources: msg.sources,
        keyInsights: msg.keyInsights,
        followUpQuestions: msg.followUpQuestions,
      }));
      setLocalMessages(converted);
    } else {
      setLocalMessages([]);
    }
  }, [messages]);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [localMessages]);

  const handleSignOut = async () => {
    await signOut();
    router.push('/');
  };

  const handleNewChat = () => {
    startNewChat();
    setLocalMessages([]);
    setReasoningEvents([]);
  };

  const handleSelectConversation = async (conv: Conversation) => {
    await selectConversation(conv);
    setReasoningEvents([]);
  };

  const handleSendMessage = async (messageText?: string) => {
    const text = messageText || input;
    if (!text.trim() || isLoading) return;

    setInput("");
    setIsLoading(true);
    setReasoningEvents([]);

    // Create conversation if none exists
    let convId = currentConversation?.id;
    if (!convId) {
      const newConv = await createConversation(text.slice(0, 50) + (text.length > 50 ? "..." : ""));
      if (!newConv) {
        setIsLoading(false);
        return;
      }
      convId = newConv.id;
    }

    // Add user message locally
    const userMessage: LocalMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date(),
    };
    setLocalMessages(prev => [...prev, userMessage]);

    // Save user message to Supabase
    await saveMessage(convId, 'user', text);

    // Add placeholder assistant message
    const assistantId = (Date.now() + 1).toString();
    const assistantMessage: LocalMessage = {
      id: assistantId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isStreaming: true,
    };
    setLocalMessages(prev => [...prev, assistantMessage]);

    try {
      // Call the API
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          mode: searchMode,
          session_id: convId,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      
      // Parse the response
      let content = '';
      let sources: Array<{ title: string; url: string }> = [];
      let keyInsights: KeyInsight[] = [];
      let followUpQuestions: string[] = [];

      if (data.response) {
        const resp = data.response;
        content = resp.main_content || resp.summary || '';
        
        if (resp.sources) {
          sources = resp.sources.map((s: any) => ({
            title: s.title || 'Source',
            url: s.url || '',
          }));
        }
        
        if (resp.key_insights) {
          keyInsights = resp.key_insights.map((i: any) => ({
            icon: i.icon || '💡',
            title: i.title,
            text: i.description,
            importance: i.importance || 'medium',
          }));
        }
        
        if (resp.follow_up_questions) {
          followUpQuestions = resp.follow_up_questions;
        }
      }

      // Update local message
      setLocalMessages(prev => prev.map(msg => 
        msg.id === assistantId 
          ? {
              ...msg,
              content,
              sources,
              keyInsights,
              followUpQuestions,
              isStreaming: false,
            }
          : msg
      ));

      // Save assistant message to Supabase
      await saveMessage(convId, 'assistant', JSON.stringify({
        content,
        sources,
        keyInsights,
        followUpQuestions,
      }));

      // Update conversation title if first message
      if (localMessages.length <= 2) {
        await updateConversationTitle(convId, text.slice(0, 50) + (text.length > 50 ? "..." : ""));
      }

    } catch (error) {
      console.error("Error sending message:", error);
      setLocalMessages(prev => prev.map(msg => 
        msg.id === assistantId 
          ? {
              ...msg,
              content: 'Sorry, there was an error processing your request. Please try again.',
              isStreaming: false,
            }
          : msg
      ));
    } finally {
      setIsLoading(false);
    }
  };

  const handleFollowUpClick = (question: string) => {
    setInput(question);
    handleSendMessage(question);
  };

  return (
    <div className="min-h-screen bg-[#070707] flex">
      {/* Left Sidebar - Conversations */}
      <aside className={cn(
        "fixed left-0 top-0 h-full z-40",
        "bg-gradient-to-b from-[#0D0D0D] to-[#080808]",
        "border-r border-white/[0.08]",
        "transition-all duration-200",
        sidebarOpen ? "w-64" : "w-14"
      )}>
        {/* Sidebar Header */}
        <div className="h-14 flex items-center justify-between px-4 border-b border-white/[0.08]">
          {sidebarOpen && (
            <Link href="/" className="font-editorial text-lg text-white">
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
          <div className="px-3 py-2 overflow-y-auto max-h-[calc(100vh-200px)]">
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
        {sidebarOpen && user && (
          <div className="absolute bottom-0 left-0 right-0 p-3 border-t border-white/[0.08]">
            <div className="flex items-center gap-3 px-2 py-2">
              <div className="w-8 h-8 rounded-full bg-purple-600/30 flex items-center justify-center">
                <User className="w-4 h-4 text-purple-400" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-white/80 truncate">
                  {user.email}
                </p>
              </div>
              <button
                onClick={handleSignOut}
                className="p-1.5 rounded hover:bg-white/[0.08] text-white/40 hover:text-white transition-colors"
                title="Sign out"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </aside>

      {/* Main Content */}
      <main className={cn(
        "flex-1 flex flex-col min-h-screen transition-all duration-200",
        sidebarOpen ? "ml-64" : "ml-14",
        reasoningOpen ? "mr-80" : "mr-0"
      )}>
        {/* Header */}
        <header className="h-14 border-b border-white/[0.08] flex items-center justify-between px-6 bg-[#0A0A0A]">
          <div className="flex items-center gap-3">
            <Sparkles className="w-5 h-5 text-purple-400" />
            <span className="text-white/80 font-medium">
              {currentConversation?.title || "McLeuker AI"}
            </span>
          </div>
          
          <div className="flex items-center gap-4">
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
              <span className="text-sm">Reasoning</span>
            </button>
          </div>
        </header>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto px-6 py-8">
          <div className="max-w-3xl mx-auto space-y-6">
            {localMessages.length === 0 ? (
              <div className="text-center py-20">
                <div className="w-20 h-20 rounded-full bg-gradient-to-br from-purple-600/20 to-pink-600/20 border border-white/[0.08] flex items-center justify-center mx-auto mb-6">
                  <Sparkles className="w-10 h-10 text-purple-400" />
                </div>
                <h2 className="text-2xl font-editorial text-white/90 mb-3">
                  Welcome, {user?.user_metadata?.full_name || user?.email?.split('@')[0] || 'User'}
                </h2>
                <p className="text-white/50 max-w-md mx-auto mb-8">
                  Your AI-powered fashion intelligence assistant. Ask about trends, 
                  sustainability, market analysis, and more.
                </p>
                
                {/* Example Prompts */}
                <div className="grid grid-cols-2 gap-3 max-w-xl mx-auto">
                  {[
                    "What are the top sustainable fashion trends for 2026?",
                    "Analyze the luxury market in Asia Pacific",
                    "Compare fast fashion vs slow fashion impact",
                    "What materials are trending in haute couture?"
                  ].map((prompt, i) => (
                    <button
                      key={i}
                      onClick={() => {
                        setInput(prompt);
                        handleSendMessage(prompt);
                      }}
                      className="p-4 bg-white/[0.03] hover:bg-white/[0.06] border border-white/[0.08] rounded-xl text-left text-sm text-white/60 hover:text-white transition-all"
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
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
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={`Ask McLeuker AI (${searchMode} mode)...`}
                className={cn(
                  "w-full h-24 px-5 py-4 pr-14",
                  "rounded-[18px]",
                  "bg-gradient-to-b from-[#1B1B1B] to-[#111111]",
                  "border border-white/[0.10]",
                  "text-white/[0.88] placeholder:text-white/40",
                  "focus:outline-none focus:border-white/[0.18]",
                  "focus:ring-[3px] focus:ring-white/[0.06]",
                  "resize-none text-sm"
                )}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
              />
              <div className="absolute bottom-4 right-4 flex items-center gap-2">
                <span className={cn(
                  "text-xs px-2 py-1 rounded",
                  searchMode === 'quick' 
                    ? "bg-blue-600/20 text-blue-400" 
                    : "bg-purple-600/20 text-purple-400"
                )}>
                  {searchMode === 'quick' ? '⚡ Quick' : '🔬 Deep'}
                </span>
                <button
                  onClick={() => handleSendMessage()}
                  disabled={!input.trim() || isLoading}
                  className={cn(
                    "w-10 h-10 rounded-full",
                    "bg-gradient-to-r from-blue-600 to-purple-600 text-white",
                    "hover:from-blue-500 hover:to-purple-500",
                    "disabled:from-gray-600 disabled:to-gray-600 disabled:text-white/40",
                    "transition-all flex items-center justify-center"
                  )}
                >
                  {isLoading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Send className="w-5 h-5" />
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Right Panel - Reasoning (Manus AI-style) */}
      {reasoningOpen && (
        <aside className="fixed right-0 top-0 h-full w-80 z-40">
          <ReasoningPanel 
            events={reasoningEvents} 
            isActive={isLoading}
            onClose={() => setReasoningOpen(false)}
          />
        </aside>
      )}

      {/* Global Styles */}
      <style jsx global>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out forwards;
        }
      `}</style>
    </div>
  );
}

// =============================================================================
// Main Dashboard Page with Protected Route
// =============================================================================

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}
