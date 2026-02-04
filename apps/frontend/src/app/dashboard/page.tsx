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
  Check,
  Image as ImageIcon,
  Paperclip,
  Settings,
  LogOut
} from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useSector, SECTORS } from "@/contexts/SectorContext";
import { supabase } from "@/integrations/supabase/client";
import { useConversations, Conversation } from "@/hooks/useConversations";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";

// =============================================================================
// Types - Multi-Layer Agentic Reasoning
// =============================================================================

interface ReasoningLayer {
  id: string;
  layer_num: number;
  type: 'understanding' | 'planning' | 'research' | 'analysis' | 'synthesis' | 'writing';
  title: string;
  content: string;
  sub_steps: { step: string; result?: string; status?: string }[];
  status: 'active' | 'complete';
  expanded: boolean;
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
  reasoning_layers: ReasoningLayer[];
  sources: Source[];
  follow_up_questions: string[];
  timestamp: Date;
  isStreaming: boolean;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://web-production-29f3c.up.railway.app';

// =============================================================================
// Reasoning Layer Component - Expandable multi-layer reasoning
// =============================================================================

function ReasoningLayerItem({ 
  layer, 
  isLatest,
  onToggleExpand 
}: { 
  layer: ReasoningLayer; 
  isLatest: boolean;
  onToggleExpand: () => void;
}) {
  const getIcon = () => {
    switch (layer.type) {
      case 'understanding': return <Brain className="h-4 w-4" />;
      case 'planning': return <FileText className="h-4 w-4" />;
      case 'research': return <Globe className="h-4 w-4" />;
      case 'analysis': return <Search className="h-4 w-4" />;
      case 'synthesis': return <Sparkles className="h-4 w-4" />;
      case 'writing': return <MessageSquare className="h-4 w-4" />;
      default: return <Circle className="h-4 w-4" />;
    }
  };

  const getColor = () => {
    if (layer.status === 'complete') return 'text-green-400';
    switch (layer.type) {
      case 'understanding': return 'text-purple-400';
      case 'planning': return 'text-blue-400';
      case 'research': return 'text-cyan-400';
      case 'analysis': return 'text-amber-400';
      case 'synthesis': return 'text-pink-400';
      case 'writing': return 'text-emerald-400';
      default: return 'text-white/60';
    }
  };

  return (
    <div className="border-l-2 border-white/10 pl-3 py-1">
      <button
        onClick={onToggleExpand}
        className={cn(
          "flex items-center gap-2 w-full text-left py-1.5 px-2 rounded-lg transition-all",
          isLatest && layer.status === 'active' ? "bg-white/5" : "hover:bg-white/5"
        )}
      >
        <div className={cn("flex-shrink-0", getColor())}>
          {layer.status === 'complete' ? (
            <CheckCircle2 className="h-4 w-4" />
          ) : (
            <div className="animate-pulse">{getIcon()}</div>
          )}
        </div>
        <div className="flex-1 min-w-0">
          <div className={cn(
            "text-sm font-medium",
            layer.status === 'complete' ? "text-white/70" : "text-white/90"
          )}>
            Layer {layer.layer_num}: {layer.title}
          </div>
        </div>
        {layer.sub_steps.length > 0 && (
          <div className="flex-shrink-0">
            {layer.expanded ? (
              <ChevronUp className="h-3.5 w-3.5 text-white/40" />
            ) : (
              <ChevronDown className="h-3.5 w-3.5 text-white/40" />
            )}
          </div>
        )}
        {layer.status === 'active' && (
          <Loader2 className="h-3 w-3 animate-spin text-white/40 flex-shrink-0" />
        )}
      </button>
      
      {/* Sub-steps - Expandable */}
      {layer.expanded && layer.sub_steps.length > 0 && (
        <div className="ml-6 mt-1 space-y-1">
          {layer.sub_steps.map((subStep, i) => (
            <div key={i} className="flex items-start gap-2 py-1">
              <div className={cn(
                "mt-1 w-1.5 h-1.5 rounded-full flex-shrink-0",
                subStep.status === 'complete' ? "bg-green-400" : "bg-white/30"
              )} />
              <p className="text-xs text-white/50 leading-relaxed">
                {subStep.step}
              </p>
            </div>
          ))}
        </div>
      )}
      
      {/* Layer content summary */}
      {layer.content && layer.expanded && (
        <div className="ml-6 mt-2 p-2 rounded bg-white/5 border border-white/10">
          <p className="text-xs text-white/60 leading-relaxed line-clamp-3">
            {layer.content}
          </p>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Message Content Component - Renders the final response
// =============================================================================

function MessageContent({ 
  content, 
  sources, 
  followUpQuestions,
  onFollowUpClick 
}: { 
  content: string; 
  sources: Source[]; 
  followUpQuestions: string[];
  onFollowUpClick: (question: string) => void;
}) {
  const [copied, setCopied] = useState(false);
  const [expanded, setExpanded] = useState(true);

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Enhanced markdown rendering with bullet points, numbered lists, and emojis
  const renderContent = (text: string) => {
    const lines = text.split('\n');
    const elements: React.ReactNode[] = [];
    let listItems: string[] = [];
    let listType: 'ul' | 'ol' | null = null;
    
    const processInlineFormatting = (line: string) => {
      // Bold text
      const boldRegex = /\*\*(.*?)\*\*/g;
      const parts = line.split(boldRegex);
      return parts.map((part, j) => 
        j % 2 === 1 ? <strong key={j} className="text-white font-medium">{part}</strong> : part
      );
    };
    
    const flushList = () => {
      if (listItems.length > 0 && listType) {
        const ListTag = listType === 'ul' ? 'ul' : 'ol';
        elements.push(
          <ListTag key={`list-${elements.length}`} className={`${listType === 'ul' ? 'list-disc' : 'list-decimal'} list-inside space-y-1 my-3 ml-2`}>
            {listItems.map((item, idx) => (
              <li key={idx} className="text-white/80 leading-relaxed">
                {processInlineFormatting(item)}
              </li>
            ))}
          </ListTag>
        );
        listItems = [];
        listType = null;
      }
    };
    
    lines.forEach((line, i) => {
      // Empty line
      if (!line.trim()) {
        flushList();
        elements.push(<br key={i} />);
        return;
      }
      
      // Headers
      if (line.startsWith('### ')) {
        flushList();
        elements.push(<h3 key={i} className="text-lg font-semibold text-white mt-4 mb-2">{line.slice(4)}</h3>);
        return;
      }
      if (line.startsWith('## ')) {
        flushList();
        elements.push(<h2 key={i} className="text-xl font-semibold text-white mt-5 mb-3">{line.slice(3)}</h2>);
        return;
      }
      if (line.startsWith('# ')) {
        flushList();
        elements.push(<h1 key={i} className="text-2xl font-bold text-white mt-6 mb-4">{line.slice(2)}</h1>);
        return;
      }
      
      // Bullet points (-, *, •)
      const bulletMatch = line.match(/^\s*[-*•]\s+(.+)/);
      if (bulletMatch) {
        if (listType !== 'ul') {
          flushList();
          listType = 'ul';
        }
        listItems.push(bulletMatch[1]);
        return;
      }
      
      // Numbered lists (1., 2., etc.)
      const numberedMatch = line.match(/^\s*\d+\.\s+(.+)/);
      if (numberedMatch) {
        if (listType !== 'ol') {
          flushList();
          listType = 'ol';
        }
        listItems.push(numberedMatch[1]);
        return;
      }
      
      // Regular paragraph
      flushList();
      elements.push(
        <p key={i} className="text-white/80 leading-relaxed mb-2">
          {processInlineFormatting(line)}
        </p>
      );
    });
    
    flushList();
    return elements;
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
      
      {/* Sources - Dynamic count */}
      {sources.length > 0 && (
        <div className="pt-4 border-t border-white/10">
          <div className="flex items-center gap-2 mb-3">
            <ExternalLink className="h-4 w-4 text-blue-400" />
            <span className="text-sm font-medium text-white/70">Sources ({sources.length})</span>
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
      
      {/* Follow-up Questions */}
      {followUpQuestions && followUpQuestions.length > 0 && (
        <div className="pt-4 border-t border-white/10">
          <div className="flex items-center gap-2 mb-3">
            <Sparkles className="h-4 w-4 text-purple-400" />
            <span className="text-sm font-medium text-white/70">Suggested Follow-ups</span>
          </div>
          <div className="flex flex-col gap-2">
            {followUpQuestions.slice(0, 5).map((question, i) => (
              <button
                key={i}
                onClick={() => onFollowUpClick(question)}
                className="text-left text-sm px-4 py-2.5 rounded-lg bg-purple-500/10 border border-purple-500/20 text-purple-300 hover:bg-purple-500/20 hover:border-purple-500/30 transition-all"
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Chat Sidebar Component - With proper chat history
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
              className="absolute right-2 top-1/2 -translate-y-1/2 text-white/40 hover:text-white/70"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Chat Count */}
      <div className="px-4 pb-2">
        <span className="text-xs text-white/40">{filteredConversations.length} chats</span>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto px-2">
        {filteredConversations.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <MessageSquare className="h-8 w-8 text-white/20 mb-2" />
            <p className="text-sm text-white/40">No chats yet</p>
            <p className="text-xs text-white/30 mt-1">Start a conversation</p>
          </div>
        ) : (
          filteredConversations.map((conv) => (
            <div
              key={conv.id}
              className={cn(
                "group relative px-3 py-2.5 rounded-lg cursor-pointer mb-1 transition-colors",
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
// Domain Tabs Component - Now navigates to domain pages
// =============================================================================

function DomainTabs() {
  const { currentSector, setSector } = useSector();
  
  const handleDomainClick = (sectorId: string) => {
    // Stay on dashboard, just change the sector context
    setSector(sectorId as any);
  };
  
  return (
    <nav className="hidden lg:flex items-center gap-0.5 overflow-x-auto max-w-[600px]">
      {SECTORS.map((sector) => (
        <button
          key={sector.id}
          onClick={() => handleDomainClick(sector.id)}
          className={cn(
            "px-3 py-1.5 text-xs font-medium rounded-md transition-colors whitespace-nowrap",
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
// Profile Button Component - Image only, no name/email
// =============================================================================

function ProfileButton() {
  const router = useRouter();
  const { user, signOut } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSignOut = async () => {
    await signOut();
    router.push('/login');
  };

  const getInitials = (name: string | undefined, email: string | undefined) => {
    if (name) {
      return name.split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2);
    }
    if (email) {
      return email.slice(0, 2).toUpperCase();
    }
    return 'U';
  };

  const initials = getInitials(user?.user_metadata?.full_name, user?.email);
  const avatarUrl = user?.user_metadata?.avatar_url;

  if (!user) return null;

  return (
    <div ref={menuRef} className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          'w-9 h-9 rounded-full flex items-center justify-center overflow-hidden',
          'border border-white/[0.12] hover:border-white/30',
          'transition-all duration-200',
          isOpen && 'ring-2 ring-purple-500/30'
        )}
      >
        {avatarUrl ? (
          <img src={avatarUrl} alt="Profile" className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full bg-gradient-to-br from-purple-600/30 to-pink-600/30 flex items-center justify-center">
            <span className="text-sm font-medium text-white">{initials}</span>
          </div>
        )}
      </button>

      {isOpen && (
        <div className="absolute top-full right-0 mt-2 w-48 bg-[#1A1A1A] border border-white/[0.08] rounded-lg shadow-xl overflow-hidden z-50">
          <Link
            href="/settings"
            onClick={() => setIsOpen(false)}
            className="flex items-center gap-3 px-3 py-2.5 text-sm text-white/70 hover:text-white hover:bg-white/[0.05] transition-colors"
          >
            <Settings className="w-4 h-4" />
            Settings
          </Link>
          <div className="border-t border-white/[0.08]">
            <button
              onClick={handleSignOut}
              className="w-full flex items-center gap-3 px-3 py-2.5 text-sm text-red-400 hover:text-red-300 hover:bg-red-500/10 transition-colors"
            >
              <LogOut className="w-4 h-4" />
              Sign Out
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// File Upload Button Component
// =============================================================================

function FileUploadButton({ onFileSelect }: { onFileSelect: (file: File) => void }) {
  const [isOpen, setIsOpen] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onFileSelect(file);
      setIsOpen(false);
    }
  };

  return (
    <div ref={menuRef} className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "h-8 w-8 rounded-lg flex items-center justify-center transition-all",
          "bg-white/[0.05] text-white/50 hover:text-white hover:bg-white/[0.10]",
          isOpen && "bg-white/[0.10] text-white"
        )}
      >
        <Plus className="w-4 h-4" />
      </button>

      {isOpen && (
        <div className="absolute bottom-full left-0 mb-2 w-48 bg-[#1A1A1A] border border-white/[0.08] rounded-lg shadow-xl overflow-hidden z-50">
          <button
            onClick={() => fileInputRef.current?.click()}
            className="w-full flex items-center gap-3 px-3 py-2.5 text-sm text-white/70 hover:text-white hover:bg-white/[0.05] transition-colors"
          >
            <Paperclip className="w-4 h-4" />
            Upload File
          </button>
          <button
            onClick={() => {
              // TODO: Implement Nano Banana image generation
              alert('Image generation coming soon!');
              setIsOpen(false);
            }}
            className="w-full flex items-center gap-3 px-3 py-2.5 text-sm text-white/70 hover:text-white hover:bg-white/[0.05] transition-colors"
          >
            <ImageIcon className="w-4 h-4" />
            Generate Image
          </button>
        </div>
      )}

      <input
        ref={fileInputRef}
        type="file"
        onChange={handleFileChange}
        className="hidden"
        accept="image/*,.pdf,.doc,.docx,.txt"
      />
    </div>
  );
}

// =============================================================================
// Main Dashboard Content
// =============================================================================

function DashboardContent() {
  const router = useRouter();
  const { user } = useAuth();
  const { currentSector } = useSector();
  const sectorConfig = SECTORS.find(s => s.id === currentSector) || SECTORS[0];
  
  const {
    conversations,
    currentConversation,
    selectConversation,
    startNewChat,
    deleteConversation,
    createConversation,
    saveMessage,
    updateConversationTitle,
    loadConversations,
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

  // Toggle layer expansion
  const toggleLayerExpand = (messageId: string, layerId: string) => {
    setMessages(prev => prev.map(m => {
      if (m.id === messageId) {
        return {
          ...m,
          reasoning_layers: m.reasoning_layers.map(l => 
            l.id === layerId ? { ...l, expanded: !l.expanded } : l
          )
        };
      }
      return m;
    }));
  };

  // Handle file upload
  const handleFileSelect = (file: File) => {
    // TODO: Implement file upload and analysis
    console.log('File selected:', file.name);
    setInput(prev => prev + `\n[Attached: ${file.name}]`);
  };

  // Send message with chat history saving
  const handleSendMessage = async (overrideMessage?: string) => {
    const messageText = overrideMessage || input.trim();
    if (!messageText || isStreaming) return;

    setInput('');
    setIsStreaming(true);

    // Create or get conversation
    let conversationId = currentConversation?.id;
    if (!conversationId) {
      const newConv = await createConversation(messageText.slice(0, 50));
      if (newConv) {
        conversationId = newConv.id;
      }
    }

    // Add user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: messageText,
      reasoning_layers: [],
      sources: [],
      follow_up_questions: [],
      timestamp: new Date(),
      isStreaming: false,
    };
    setMessages(prev => [...prev, userMessage]);

    // Save user message to database
    if (conversationId) {
      await saveMessage(conversationId, 'user', messageText);
    }

    // Add assistant message placeholder
    const assistantId = `assistant-${Date.now()}`;
    const assistantMessage: Message = {
      id: assistantId,
      role: 'assistant',
      content: '',
      reasoning_layers: [],
      sources: [],
      follow_up_questions: [],
      timestamp: new Date(),
      isStreaming: true,
    };
    setMessages(prev => [...prev, assistantMessage]);

    // Track reasoning state
    let currentLayers: ReasoningLayer[] = [];
    let currentSources: Source[] = [];
    let currentContent = '';

    try {
      const response = await fetch(`${API_URL}/api/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: messageText,
          mode: searchMode,
          sector: currentSector === 'all' ? null : currentSector,
        }),
      });

      if (!response.ok) throw new Error('API error');

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n').filter(line => line.trim());

          for (const line of lines) {
            if (!line.startsWith('data: ')) continue;
            
            try {
              const data = JSON.parse(line.slice(6));
              const eventType = data.type;
              const eventData = data.data || {};

              if (eventType === 'layer_start') {
                // New reasoning layer started
                const newLayer: ReasoningLayer = {
                  id: eventData.layer_id,
                  layer_num: eventData.layer_num,
                  type: eventData.type,
                  title: eventData.title,
                  content: '',
                  sub_steps: [],
                  status: 'active',
                  expanded: true,
                };
                currentLayers.push(newLayer);
                
                setMessages(prev => prev.map(m =>
                  m.id === assistantId
                    ? { ...m, reasoning_layers: [...currentLayers] }
                    : m
                ));
              } else if (eventType === 'sub_step') {
                // Sub-step within a layer
                const layerIndex = currentLayers.findIndex(l => l.id === eventData.layer_id);
                if (layerIndex >= 0) {
                  currentLayers[layerIndex].sub_steps.push({
                    step: eventData.step,
                    status: eventData.status,
                  });
                  
                  setMessages(prev => prev.map(m =>
                    m.id === assistantId
                      ? { ...m, reasoning_layers: [...currentLayers] }
                      : m
                  ));
                }
              } else if (eventType === 'layer_complete') {
                // Layer completed
                const layerIndex = currentLayers.findIndex(l => l.id === eventData.layer_id);
                if (layerIndex >= 0) {
                  currentLayers[layerIndex].status = 'complete';
                  currentLayers[layerIndex].content = eventData.content || '';
                  
                  setMessages(prev => prev.map(m =>
                    m.id === assistantId
                      ? { ...m, reasoning_layers: [...currentLayers] }
                      : m
                  ));
                }
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
                currentContent += eventData.chunk || '';

                setMessages(prev => prev.map(m =>
                  m.id === assistantId
                    ? { ...m, content: currentContent }
                    : m
                ));
              } else if (eventType === 'follow_up') {
                // Handle follow-up questions
                const questions = eventData.questions || [];
                setMessages(prev => prev.map(m =>
                  m.id === assistantId
                    ? { ...m, follow_up_questions: questions }
                    : m
                ));
              } else if (eventType === 'complete') {
                const finalContent = eventData.content || currentContent;
                const creditsUsed = eventData.credits_used || (searchMode === 'quick' ? 2 : 5);
                const followUpQuestions = eventData.follow_up_questions || [];

                // Mark all layers as complete
                currentLayers = currentLayers.map(l => ({ ...l, status: 'complete' as const }));

                setMessages(prev => prev.map(m =>
                  m.id === assistantId
                    ? {
                        ...m,
                        content: finalContent,
                        reasoning_layers: currentLayers,
                        sources: eventData.sources || currentSources,
                        follow_up_questions: followUpQuestions,
                        isStreaming: false,
                      }
                    : m
                ));

                setCreditBalance(prev => Math.max(0, prev - creditsUsed));

                // Save assistant message to database
                if (conversationId) {
                  await saveMessage(conversationId, 'assistant', finalContent, 'grok-3', creditsUsed);
                  
                  // Update conversation title if it's a new conversation
                  if (messages.length === 0) {
                    await updateConversationTitle(conversationId, messageText.slice(0, 50));
                  }
                }

                // Reload conversations to show updated list
                await loadConversations();
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

  const handleSelectConversation = async (conv: Conversation) => {
    await selectConversation(conv);
    // Load messages for this conversation from the hook
    const { data, error } = await supabase
      .from("chat_messages")
      .select("*")
      .eq("conversation_id", conv.id)
      .order("created_at", { ascending: true });
    
    if (!error && data) {
      const loadedMessages: Message[] = data.map((msg: any) => ({
        id: msg.id,
        role: msg.role as 'user' | 'assistant',
        content: msg.content,
        reasoning_layers: [],
        sources: [],
        follow_up_questions: [],
        timestamp: new Date(msg.created_at),
        isStreaming: false,
      }));
      setMessages(loadedMessages);
    }
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
            <ProfileButton />
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
                    Ask me anything. I'll reason through your question with multiple layers of analysis.
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
                          {/* Multi-Layer Reasoning - Expandable */}
                          {message.reasoning_layers.length > 0 && (
                            <div className="space-y-1 pb-4 border-b border-white/[0.08]">
                              <div className="flex items-center gap-2 mb-3">
                                <Brain className="h-4 w-4 text-purple-400" />
                                <span className="text-sm font-medium text-white/70">
                                  {message.isStreaming ? 'Reasoning...' : `Reasoning (${message.reasoning_layers.length} layers)`}
                                </span>
                              </div>
                              {message.reasoning_layers.map((layer, i) => (
                                <ReasoningLayerItem 
                                  key={layer.id} 
                                  layer={layer} 
                                  isLatest={i === message.reasoning_layers.length - 1}
                                  onToggleExpand={() => toggleLayerExpand(message.id, layer.id)}
                                />
                              ))}
                            </div>
                          )}
                          
                          {/* Response Content */}
                          {message.content ? (
                            <MessageContent 
                              content={message.content} 
                              sources={message.sources}
                              followUpQuestions={message.follow_up_questions}
                              onFollowUpClick={(q) => handleSendMessage(q)}
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

            {/* Input with File Upload */}
            <div className="relative flex items-end gap-2">
              <FileUploadButton onFileSelect={handleFileSelect} />
              
              <div className="flex-1 relative">
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
