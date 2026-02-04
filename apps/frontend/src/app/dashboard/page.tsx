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
  LogOut,
  User,
  CreditCard,
  HelpCircle,
  MoreHorizontal,
  Star
} from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useSector, SECTORS } from "@/contexts/SectorContext";
import { supabase } from "@/integrations/supabase/client";
import { useConversations, Conversation } from "@/hooks/useConversations";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { formatDistanceToNow } from "date-fns";

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
  is_favorite?: boolean;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://web-production-29f3c.up.railway.app';

// =============================================================================
// Reasoning Layer Component - Updated with McLeuker green colors
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

  // Updated colors - McLeuker green palette instead of purple
  const getColor = () => {
    if (layer.status === 'complete') return 'text-green-400';
    switch (layer.type) {
      case 'understanding': return 'text-[#177b57]';
      case 'planning': return 'text-[#266a2e]';
      case 'research': return 'text-[#3d665c]';
      case 'analysis': return 'text-[#4c7748]';
      case 'synthesis': return 'text-[#457556]';
      case 'writing': return 'text-emerald-400';
      default: return 'text-white/60';
    }
  };

  return (
    <div className="border-l-2 border-[#177b57]/30 pl-3 py-1">
      <button
        onClick={onToggleExpand}
        className={cn(
          "flex items-center gap-2 w-full text-left py-1.5 px-2 rounded-lg transition-all",
          isLatest && layer.status === 'active' ? "bg-[#177b57]/10" : "hover:bg-[#177b57]/5"
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
          <Loader2 className="h-3 w-3 animate-spin text-[#177b57] flex-shrink-0" />
        )}
      </button>
      
      {/* Sub-steps - Expandable */}
      {layer.expanded && layer.sub_steps.length > 0 && (
        <div className="ml-6 mt-1 space-y-1">
          {layer.sub_steps.map((subStep, i) => (
            <div key={i} className="flex items-start gap-2 py-1">
              <div className={cn(
                "mt-1 w-1.5 h-1.5 rounded-full flex-shrink-0",
                subStep.status === 'complete' ? "bg-green-400" : "bg-[#177b57]/50"
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
        <div className="ml-6 mt-2 p-2 rounded bg-[#177b57]/5 border border-[#177b57]/20">
          <p className="text-xs text-white/60 leading-relaxed line-clamp-3">
            {layer.content}
          </p>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Message Content Component - Updated with McLeuker green
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
            className="flex items-center gap-1 text-xs text-[#177b57] hover:text-[#266a2e] mt-2"
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
        <div className="pt-3 border-t border-white/[0.08]">
          <p className="text-xs font-medium text-white/50 mb-2">Sources ({sources.length})</p>
          <div className="flex flex-wrap gap-2">
            {sources.map((source, i) => (
              <a
                key={i}
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-white/[0.05] hover:bg-[#177b57]/10 border border-white/[0.08] hover:border-[#177b57]/30 text-xs text-white/70 hover:text-white transition-colors"
              >
                <ExternalLink className="h-3 w-3" />
                <span className="max-w-[150px] truncate">{source.title}</span>
              </a>
            ))}
          </div>
        </div>
      )}
      
      {/* Follow-up Questions */}
      {followUpQuestions.length > 0 && (
        <div className="pt-3 border-t border-white/[0.08]">
          <p className="text-xs font-medium text-white/50 mb-2">Continue exploring</p>
          <div className="space-y-2">
            {followUpQuestions.map((question, i) => (
              <button
                key={i}
                onClick={() => onFollowUpClick(question)}
                className="w-full text-left px-3 py-2 rounded-lg bg-white/[0.03] hover:bg-[#177b57]/10 border border-white/[0.06] hover:border-[#177b57]/30 text-sm text-white/70 hover:text-white/90 transition-all"
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
// Chat Sidebar - Premium bubble styling with green hover
// =============================================================================

interface ChatSidebarProps {
  conversations: Conversation[];
  currentConversation: Conversation | null;
  isOpen: boolean;
  onToggle: () => void;
  onSelectConversation: (conversation: Conversation) => void;
  onDeleteConversation: (conversationId: string) => void;
  onNewConversation: () => void;
}

function ChatSidebar({
  conversations,
  currentConversation,
  isOpen,
  onToggle,
  onSelectConversation,
  onDeleteConversation,
  onNewConversation,
}: ChatSidebarProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [conversationToDelete, setConversationToDelete] = useState<string | null>(null);

  const filteredConversations = conversations.filter((conv) =>
    conv.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleDeleteClick = (e: React.MouseEvent, conversationId: string) => {
    e.stopPropagation();
    setConversationToDelete(conversationId);
    setDeleteDialogOpen(true);
  };

  const handleConfirmDelete = () => {
    if (conversationToDelete) {
      onDeleteConversation(conversationToDelete);
    }
    setDeleteDialogOpen(false);
    setConversationToDelete(null);
  };

  // Collapsed state
  if (!isOpen) {
    return (
      <aside className={cn(
        "hidden lg:flex w-14 flex-col fixed left-0 top-[60px] bottom-0 z-30",
        "bg-gradient-to-b from-[#0F0F0F] to-[#0A0A0A]",
        "border-r border-white/[0.08]"
      )}>
        <div className="p-2 pt-4">
          <button
            onClick={onToggle}
            className="w-10 h-10 flex items-center justify-center text-white/60 hover:text-white hover:bg-[#177b57]/10 rounded-lg transition-colors"
          >
            <PanelLeft className="h-4 w-4" />
          </button>
        </div>
      </aside>
    );
  }

  return (
    <>
      <aside className={cn(
        "hidden lg:flex w-64 flex-col fixed left-0 top-[60px] bottom-0 z-30",
        "bg-gradient-to-b from-[#0F0F0F] to-[#0A0A0A]",
        "border-r border-white/[0.08]"
      )}>
        {/* Header with collapse toggle */}
        <div className="px-4 pt-5 pb-3 flex items-center justify-between shrink-0">
          <span className="font-medium text-[13px] text-white/80">Chat History</span>
          <button
            onClick={onToggle}
            className="h-8 w-8 flex items-center justify-center text-white/50 hover:text-white hover:bg-[#177b57]/10 rounded-lg transition-colors"
          >
            <PanelLeftClose className="h-4 w-4" />
          </button>
        </div>

        {/* New Chat Button - McLeuker green */}
        <div className="px-4 pb-3 shrink-0">
          <button
            onClick={onNewConversation}
            className={cn(
              "w-full justify-center gap-2 flex items-center",
              "bg-gradient-to-r from-[#177b57] to-[#266a2e] text-white hover:from-[#1a8a62] hover:to-[#2d7a35]",
              "h-10 rounded-full text-[13px] font-medium transition-all"
            )}
          >
            <Plus className="h-4 w-4" />
            New Chat
          </button>
        </div>

        {/* Search */}
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
                "focus:border-[#177b57]/40 focus:outline-none focus:ring-1 focus:ring-[#177b57]/20",
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

        {/* Chat count */}
        <div className="px-4 pb-2 shrink-0">
          <p className="text-[10px] font-medium text-white/40 uppercase tracking-wider">
            {filteredConversations.length} {filteredConversations.length === 1 ? 'chat' : 'chats'}
          </p>
        </div>

        {/* Conversation List - Premium bubble styling */}
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
                  "group relative w-full text-left px-4 py-3 cursor-pointer",
                  "chat-sidebar-item",
                  currentConversation?.id === conv.id && "chat-sidebar-item-active"
                )}
                onClick={() => onSelectConversation(conv)}
              >
                <div className="flex items-center gap-2.5 relative z-10">
                  <MessageSquare className="h-4 w-4 text-white/50 flex-shrink-0" />
                  <div className="flex-1 min-w-0 pr-6">
                    <p className="text-[12px] font-medium text-white/90 line-clamp-2 leading-relaxed">
                      {conv.title}
                    </p>
                    <p className="text-[10px] text-white/45 mt-1.5">
                      {formatDistanceToNow(conv.updatedAt, { addSuffix: true })}
                    </p>
                  </div>
                </div>

                {/* Delete Button */}
                <button
                  onClick={(e) => handleDeleteClick(e, conv.id)}
                  className={cn(
                    "absolute right-2 top-1/2 -translate-y-1/2 h-7 w-7 flex items-center justify-center z-10",
                    "opacity-0 group-hover:opacity-100 transition-opacity",
                    "text-white/50 hover:text-red-400 hover:bg-red-500/10 rounded-lg"
                  )}
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            ))
          )}
        </div>
      </aside>

      {/* Delete Confirmation Dialog */}
      {deleteDialogOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-[#1A1A1A] border border-white/[0.08] rounded-xl p-6 max-w-sm w-full mx-4">
            <h3 className="text-lg font-semibold text-white mb-2">Delete this chat?</h3>
            <p className="text-sm text-white/60 mb-6">
              This will permanently delete this chat and all its messages. This action cannot be undone.
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setDeleteDialogOpen(false)}
                className="px-4 py-2 text-sm text-white/70 hover:text-white hover:bg-white/[0.05] rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmDelete}
                className="px-4 py-2 text-sm bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

// =============================================================================
// Domain Tabs Component - Static, centered with green glow underline
// =============================================================================

function DomainTabs() {
  const { currentSector, setSector } = useSector();
  
  const handleDomainClick = (sectorId: string) => {
    setSector(sectorId as any);
  };
  
  return (
    <nav className="flex items-center gap-0.5 flex-wrap justify-center">
      {SECTORS.map((sector) => (
        <button
          key={sector.id}
          onClick={() => handleDomainClick(sector.id)}
          className={cn(
            "domain-tab",
            currentSector === sector.id && "domain-tab-active"
          )}
        >
          {sector.label}
        </button>
      ))}
    </nav>
  );
}

// =============================================================================
// Profile Dropdown - Updated with McLeuker green accents
// =============================================================================

function ProfileDropdown() {
  const router = useRouter();
  const { user, signOut } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [creditBalance, setCreditBalance] = useState(50);
  const [plan, setPlan] = useState('free');
  const [userProfile, setUserProfile] = useState<{ name: string | null; profile_image: string | null } | null>(null);
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

  // Fetch user profile and credits
  useEffect(() => {
    const fetchUserData = async () => {
      if (!user) return;
      
      const { data } = await supabase
        .from("users")
        .select("name, profile_image, credit_balance, subscription_plan")
        .eq("id", user.id)
        .single();
      
      if (data) {
        setUserProfile({ name: data.name, profile_image: data.profile_image });
        setCreditBalance(data.credit_balance || 50);
        setPlan(data.subscription_plan || 'free');
      }
    };
    
    fetchUserData();
  }, [user]);

  const handleSignOut = async () => {
    await signOut();
    router.push('/login');
  };

  const getInitials = (name: string | null | undefined, email: string | undefined) => {
    if (name) {
      return name.split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2);
    }
    if (email) {
      return email.slice(0, 2).toUpperCase();
    }
    return 'U';
  };

  const initials = getInitials(userProfile?.name || user?.user_metadata?.full_name, user?.email);
  const avatarUrl = userProfile?.profile_image || user?.user_metadata?.avatar_url;

  if (!user) return null;

  return (
    <div className="flex items-center gap-3">
      {/* Credits Display - Updated with green accent */}
      <Link
        href="/billing"
        className="hidden sm:flex items-center gap-1.5 px-2.5 py-1.5 rounded-md bg-white/5 hover:bg-[#177b57]/10 border border-white/[0.08] hover:border-[#177b57]/30 transition-colors"
      >
        <Coins className="h-3.5 w-3.5 text-[#4ade80]" />
        <span className="text-xs font-medium text-white/80">{creditBalance} credits</span>
      </Link>

      {/* Profile Button */}
      <div ref={menuRef} className="relative">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className={cn(
            'w-8 h-8 rounded-full flex items-center justify-center overflow-hidden',
            'border border-white/[0.12] hover:border-[#177b57]/50 hover:bg-[#177b57]/10',
            'transition-all duration-200',
            isOpen && 'ring-2 ring-[#177b57]/30'
          )}
        >
          {avatarUrl ? (
            <img src={avatarUrl} alt="Profile" className="w-full h-full object-cover" />
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-[#177b57] to-[#266a2e] flex items-center justify-center">
              <span className="text-xs font-medium text-white">{initials}</span>
            </div>
          )}
        </button>

        {isOpen && (
          <div className="absolute top-full right-0 mt-2 w-56 bg-[#141414] border border-white/10 rounded-lg shadow-xl overflow-hidden z-50">
            {/* User Info Header */}
            <div className="px-3 py-2 border-b border-white/10">
              {(userProfile?.name || user?.user_metadata?.full_name) && (
                <p className="text-sm font-medium text-white truncate">
                  {userProfile?.name || user?.user_metadata?.full_name}
                </p>
              )}
              <p className={cn(
                "text-sm truncate",
                (userProfile?.name || user?.user_metadata?.full_name) ? "text-white/60" : "font-medium text-white"
              )}>
                {user?.email}
              </p>
              <p className="text-xs text-white/50 capitalize mt-0.5">{plan} plan</p>
              <div className="text-xs text-white/50 mt-1">
                <span className="font-medium text-[#4ade80]">{creditBalance}</span> credits available
              </div>
            </div>
            
            {/* Menu Items */}
            <div className="py-1">
              <Link
                href="/settings"
                onClick={() => setIsOpen(false)}
                className="flex items-center gap-3 px-3 py-2.5 text-sm text-white/80 hover:bg-[#177b57]/10 hover:text-white transition-colors"
              >
                <User className="h-4 w-4" />
                Profile
              </Link>
              <Link
                href="/billing"
                onClick={() => setIsOpen(false)}
                className="flex items-center gap-3 px-3 py-2.5 text-sm text-white/80 hover:bg-[#177b57]/10 hover:text-white transition-colors"
              >
                <CreditCard className="h-4 w-4" />
                Billing & Credits
              </Link>
              <Link
                href="/preferences"
                onClick={() => setIsOpen(false)}
                className="flex items-center gap-3 px-3 py-2.5 text-sm text-white/80 hover:bg-[#177b57]/10 hover:text-white transition-colors"
              >
                <Settings className="h-4 w-4" />
                Workspace Preferences
              </Link>
            </div>
            
            <div className="border-t border-white/10 py-1">
              <Link
                href="/contact"
                onClick={() => setIsOpen(false)}
                className="flex items-center gap-3 px-3 py-2.5 text-sm text-white/80 hover:bg-[#177b57]/10 hover:text-white transition-colors"
              >
                <HelpCircle className="h-4 w-4" />
                Support / Help
              </Link>
            </div>
            
            <div className="border-t border-white/10 py-1">
              <button
                onClick={handleSignOut}
                className="w-full flex items-center gap-3 px-3 py-2.5 text-sm text-red-400 hover:bg-red-500/10 hover:text-red-300 transition-colors"
              >
                <LogOut className="h-4 w-4" />
                Sign out
              </button>
            </div>
          </div>
        )}
      </div>
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
          "h-10 w-10 rounded-xl flex items-center justify-center transition-all",
          "bg-white/[0.05] text-white/50 hover:text-white hover:bg-[#177b57]/10 hover:border-[#177b57]/30",
          "border border-white/[0.08]",
          isOpen && "bg-[#177b57]/10 text-white border-[#177b57]/30"
        )}
      >
        <Plus className="w-5 h-5" />
      </button>

      {isOpen && (
        <div className="absolute bottom-full left-0 mb-2 w-48 bg-[#1A1A1A] border border-white/[0.08] rounded-lg shadow-xl overflow-hidden z-50">
          <button
            onClick={() => fileInputRef.current?.click()}
            className="w-full flex items-center gap-3 px-3 py-2.5 text-sm text-white/70 hover:text-white hover:bg-[#177b57]/10 transition-colors"
          >
            <Paperclip className="w-4 h-4" />
            Upload File
          </button>
          <button
            onClick={() => {
              alert('Image generation coming soon!');
              setIsOpen(false);
            }}
            className="w-full flex items-center gap-3 px-3 py-2.5 text-sm text-white/70 hover:text-white hover:bg-[#177b57]/10 transition-colors"
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

  // Load conversations on mount
  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

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
    if (conversationId && user) {
      try {
        await supabase.from('chat_messages').insert({
          conversation_id: conversationId,
          user_id: user.id,
          role: 'user',
          content: messageText,
          credits_used: 0,
        });
      } catch (e) {
        console.error('Error saving user message:', e);
      }
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
    let finalFollowUp: string[] = [];

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
                finalFollowUp = eventData.questions || [];
                setMessages(prev => prev.map(m =>
                  m.id === assistantId
                    ? { ...m, follow_up_questions: finalFollowUp }
                    : m
                ));
              } else if (eventType === 'complete') {
                const finalContent = eventData.content || currentContent;
                const creditsUsed = eventData.credits_used || (searchMode === 'quick' ? 2 : 5);
                const followUpQuestions = eventData.follow_up_questions || finalFollowUp;

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
                if (conversationId && user) {
                  try {
                    await supabase.from('chat_messages').insert({
                      conversation_id: conversationId,
                      user_id: user.id,
                      role: 'assistant',
                      content: finalContent,
                      model_used: 'grok-3',
                      credits_used: creditsUsed,
                      sources: eventData.sources || currentSources,
                      follow_up_questions: followUpQuestions,
                    });
                    
                    // Update conversation title if it's a new conversation
                    if (messages.length === 0) {
                      await updateConversationTitle(conversationId, messageText.slice(0, 50));
                    }
                  } catch (e) {
                    console.error('Error saving assistant message:', e);
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
    // Load messages for this conversation
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
        sources: msg.sources || [],
        follow_up_questions: msg.follow_up_questions || [],
        timestamp: new Date(msg.created_at),
        isStreaming: false,
        is_favorite: msg.is_favorite,
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
      {/* Header - Fixed at top, full width */}
      <header className="h-[60px] border-b border-white/[0.08] flex items-center justify-between px-4 bg-[#0A0A0A] fixed top-0 left-0 right-0 z-40">
        {/* Left: McLeuker Logo */}
        <div className="flex items-center gap-4 w-48">
          <Link href="/" className="font-editorial text-xl text-white tracking-wide">
            McLeuker
          </Link>
        </div>
        
        {/* Center: Domain Tabs - Centered relative to chat area */}
        <div className={cn(
          "hidden lg:flex items-center justify-center flex-1",
          sidebarOpen ? "ml-64" : "ml-14"
        )}>
          <DomainTabs />
        </div>
        
        {/* Right: Credits & Profile */}
        <div className="w-48 flex justify-end">
          <ProfileDropdown />
        </div>
      </header>

      {/* Chat Sidebar - Below header */}
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
        "flex-1 flex flex-col min-h-screen transition-all duration-200 pt-[60px]",
        sidebarOpen ? "lg:ml-64" : "lg:ml-14"
      )}>
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto">
          <div className="max-w-3xl mx-auto px-4 py-6">
            {messages.length === 0 ? (
              /* STATE A: Empty State - "Where is my mind?" */
              <div className="flex flex-col items-center justify-center min-h-[60vh]">
                <div className="text-center mb-8">
                  {/* Brain Icon with McLeuker green ombre */}
                  <div className="w-16 h-16 rounded-2xl mcleuker-brain-gradient flex items-center justify-center mx-auto mb-4 shadow-lg shadow-[#177b57]/20">
                    <Brain className="h-8 w-8 text-white" />
                  </div>
                  {/* New Title */}
                  <h1 className="text-2xl font-bold text-white mb-2">
                    Where is my mind?
                  </h1>
                  {/* New Subtitle */}
                  <p className="text-white/50 max-w-md">
                    Give me chaos — I'll return a map.
                  </p>
                </div>
                
                {/* Suggestion Cards with bubble gradient variation */}
                <div className="grid gap-3 w-full max-w-xl mb-8">
                  {starterQuestions.map((question, i) => (
                    <button
                      key={i}
                      onClick={() => handleSendMessage(question)}
                      className={cn(
                        "text-left p-4 rounded-xl transition-all",
                        "mcleuker-bubble",
                        i % 4 === 0 && "mcleuker-bubble-v1",
                        i % 4 === 1 && "mcleuker-bubble-v2",
                        i % 4 === 2 && "mcleuker-bubble-v3",
                        i % 4 === 3 && "mcleuker-bubble-v4",
                        "text-white/70 hover:text-white/90"
                      )}
                    >
                      <span className="relative z-10">{question}</span>
                    </button>
                  ))}
                </div>

                {/* Input Area for State A - Green ombre, centered */}
                <div className="w-full max-w-xl space-y-3">
                  {/* Quick/Deep Toggle - Centered */}
                  <div className="flex items-center justify-center gap-2">
                    <button
                      onClick={() => setSearchMode('quick')}
                      disabled={isStreaming}
                      className={cn(
                        "flex items-center gap-1.5 px-4 py-2 rounded-full text-xs font-medium transition-all",
                        searchMode === 'quick'
                          ? "bg-gradient-to-r from-[#177b57] to-[#266a2e] text-white"
                          : "text-white/60 hover:text-white bg-white/5 hover:bg-[#177b57]/10"
                      )}
                    >
                      <Zap className="h-3.5 w-3.5" />
                      Quick
                      <span className="text-white/50 ml-1">2</span>
                    </button>
                    <button
                      onClick={() => setSearchMode('deep')}
                      disabled={isStreaming}
                      className={cn(
                        "flex items-center gap-1.5 px-4 py-2 rounded-full text-xs font-medium transition-all",
                        searchMode === 'deep'
                          ? "bg-gradient-to-r from-[#177b57] to-[#266a2e] text-white"
                          : "text-white/60 hover:text-white bg-white/5 hover:bg-[#177b57]/10"
                      )}
                    >
                      <Brain className="h-3.5 w-3.5" />
                      Deep
                      <span className="text-white/50 ml-1">5</span>
                    </button>
                  </div>

                  {/* Input with Plus button left, Send inside right */}
                  <div className="relative flex items-center gap-3">
                    {/* Plus Button - Left of input */}
                    <FileUploadButton onFileSelect={handleFileSelect} />
                    
                    {/* Input Bubble - Green ombre for State A */}
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
                          "rounded-xl mcleuker-green-input",
                          "text-white placeholder:text-white/40",
                          "focus:outline-none",
                          "resize-none transition-all",
                          isStreaming && "opacity-50 cursor-not-allowed"
                        )}
                        rows={1}
                      />
                      {/* Send Button - Inside right */}
                      <button
                        onClick={() => handleSendMessage()}
                        disabled={!input.trim() || isStreaming}
                        className={cn(
                          "absolute right-2 top-1/2 -translate-y-1/2 h-8 w-8 rounded-lg flex items-center justify-center transition-all",
                          input.trim() && !isStreaming
                            ? "bg-gradient-to-r from-[#177b57] to-[#266a2e] text-white hover:from-[#1a8a62] hover:to-[#2d7a35]"
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
                  
                  {/* Credits Badge - Centered */}
                  <div className="flex items-center justify-center">
                    <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/5 border border-white/[0.08]">
                      <Coins className="h-3.5 w-3.5 text-[#4ade80]" />
                      <span className="text-xs font-medium text-white/80">{creditBalance}</span>
                    </div>
                  </div>
                  
                  <p className="text-xs text-white/30 text-center">
                    Press Enter to send • Shift + Enter for new line
                  </p>
                </div>
              </div>
            ) : (
              /* STATE B: Active Chat - Messages */
              <div className="space-y-6">
                {messages.map(message => (
                  <div key={message.id} className={cn(
                    "flex",
                    message.role === 'user' ? "justify-end" : "justify-start"
                  )}>
                    <div className={cn(
                      "max-w-[85%]",
                      message.role === 'user'
                        ? "mcleuker-user-bubble px-4 py-3 rounded-2xl mr-2"
                        : "bg-[#111111] border border-white/[0.08] p-4 rounded-xl ml-2"
                    )}>
                      {message.role === 'user' ? (
                        <p className="text-white">{message.content}</p>
                      ) : (
                        <div className="space-y-4">
                          {/* Multi-Layer Reasoning - Expandable */}
                          {message.reasoning_layers.length > 0 && (
                            <div className="space-y-1 pb-4 border-b border-white/[0.08]">
                              <div className="flex items-center gap-2 mb-3">
                                <Brain className="h-4 w-4 text-[#177b57]" />
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
                              <Loader2 className="h-4 w-4 animate-spin text-[#177b57]" />
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

        {/* STATE B: Input Area - Black input after first message */}
        {messages.length > 0 && (
          <div className="border-t border-white/[0.08] p-4 bg-[#0A0A0A]">
            <div className="max-w-3xl mx-auto space-y-3">
              {/* Mode Toggle & Credits - Centered */}
              <div className="flex items-center justify-center gap-4">
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setSearchMode('quick')}
                    disabled={isStreaming}
                    className={cn(
                      "flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all",
                      searchMode === 'quick'
                        ? "bg-gradient-to-r from-[#177b57] to-[#266a2e] text-white"
                        : "text-white/60 hover:text-white bg-white/5 hover:bg-[#177b57]/10"
                    )}
                  >
                    <Zap className="h-3.5 w-3.5" />
                    Quick
                    <span className="text-white/50 ml-1">2</span>
                  </button>
                  <button
                    onClick={() => setSearchMode('deep')}
                    disabled={isStreaming}
                    className={cn(
                      "flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all",
                      searchMode === 'deep'
                        ? "bg-gradient-to-r from-[#177b57] to-[#266a2e] text-white"
                        : "text-white/60 hover:text-white bg-white/5 hover:bg-[#177b57]/10"
                    )}
                  >
                    <Brain className="h-3.5 w-3.5" />
                    Deep
                    <span className="text-white/50 ml-1">5</span>
                  </button>
                </div>
                
                <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/5 border border-white/[0.08]">
                  <Coins className="h-3.5 w-3.5 text-[#4ade80]" />
                  <span className="text-xs font-medium text-white/80">{creditBalance}</span>
                </div>
              </div>

              {/* Input with File Upload - Black input for State B */}
              <div className="relative flex items-center gap-3">
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
                      "focus:border-[#177b57]/40 focus:outline-none focus:ring-1 focus:ring-[#177b57]/20",
                      "resize-none transition-all",
                      isStreaming && "opacity-50 cursor-not-allowed"
                    )}
                    rows={1}
                  />
                  <button
                    onClick={() => handleSendMessage()}
                    disabled={!input.trim() || isStreaming}
                    className={cn(
                      "absolute right-2 top-1/2 -translate-y-1/2 h-8 w-8 rounded-lg flex items-center justify-center transition-all",
                      input.trim() && !isStreaming
                        ? "bg-gradient-to-r from-[#177b57] to-[#266a2e] text-white hover:from-[#1a8a62] hover:to-[#2d7a35]"
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
        )}
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
