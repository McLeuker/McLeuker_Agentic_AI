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
  Star,
  Download,
  File,
  FileDown,
  FileSpreadsheet,
  Presentation
} from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useSector, SECTORS, Sector } from "@/contexts/SectorContext";
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

interface AttachedFile {
  name: string;
  type: string;
  size: number;
  url?: string;
  base64?: string;
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
  attachedFiles?: AttachedFile[];
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://web-production-29f3c.up.railway.app';

// Global AbortController for streaming - allows cancellation when switching chats
let globalAbortController: AbortController | null = null;

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
      case 'understanding': return 'text-[#3d655c]';
      case 'planning': return 'text-[#3d665c]';
      case 'research': return 'text-[#3d665c]';
      case 'analysis': return 'text-[#4c7748]';
      case 'synthesis': return 'text-[#457556]';
      case 'writing': return 'text-emerald-400';
      default: return 'text-white/60';
    }
  };

  return (
    <div className="border-l-2 border-[#3d655c]/30 pl-3 py-1">
      <button
        onClick={onToggleExpand}
        className={cn(
          "flex items-center gap-2 w-full text-left py-1.5 px-2 rounded-lg transition-all",
          isLatest && layer.status === 'active' ? "bg-[#3d655c]/10" : "hover:bg-[#3d655c]/5"
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
          <Loader2 className="h-3 w-3 animate-spin text-[#3d655c] flex-shrink-0" />
        )}
      </button>
      
      {/* Sub-steps - Expandable */}
      {layer.expanded && layer.sub_steps.length > 0 && (
        <div className="ml-6 mt-1 space-y-1">
          {layer.sub_steps.map((subStep, i) => (
            <div key={i} className="flex items-start gap-2 py-1">
              <div className={cn(
                "mt-1 w-1.5 h-1.5 rounded-full flex-shrink-0",
                subStep.status === 'complete' ? "bg-green-400" : "bg-[#3d655c]/50"
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
        <div className="ml-6 mt-2 p-2 rounded bg-[#3d655c]/5 border border-[#3d655c]/20">
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
  const [exporting, setExporting] = useState<string | null>(null);
  const [showExportMenu, setShowExportMenu] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Export document function
  const handleExport = async (format: string) => {
    setExporting(format);
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://web-production-29f3c.up.railway.app';
      const response = await fetch(`${API_URL}/api/document/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: content,
          format: format,
          title: 'McLeuker AI Report'
        })
      });

      if (!response.ok) {
        throw new Error('Export failed');
      }

      // Get the blob and download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      
      // Get filename from Content-Disposition header or use default
      const disposition = response.headers.get('Content-Disposition');
      let filename = `mcleuker-report.${format}`;
      if (disposition) {
        const match = disposition.match(/filename="(.+)"/);
        if (match) filename = match[1];
      }
      
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      setShowExportMenu(false);
    } catch (error) {
      console.error('Export error:', error);
      alert('Failed to export document. Please try again.');
    } finally {
      setExporting(null);
    }
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
            className="flex items-center gap-1 text-xs text-[#3d655c] hover:text-[#3d665c] mt-2"
          >
            {expanded ? (
              <>Show less <ChevronUp className="h-3 w-3" /></>
            ) : (
              <>Show more <ChevronDown className="h-3 w-3" /></>
            )}
          </button>
        )}
        
        {/* Action Buttons */}
        <div className="absolute top-0 right-0 flex items-center gap-1">
          {/* Copy Button */}
          <button
            onClick={handleCopy}
            className="p-2 text-white/40 hover:text-white/70 transition-colors"
            title="Copy to clipboard"
          >
            {copied ? <Check className="h-4 w-4 text-green-400" /> : <Copy className="h-4 w-4" />}
          </button>
          
          {/* Export Menu */}
          <div className="relative">
            <button
              onClick={() => setShowExportMenu(!showExportMenu)}
              className="p-2 text-white/40 hover:text-white/70 transition-colors"
              title="Export document"
            >
              <FileDown className="h-4 w-4" />
            </button>
            
            {showExportMenu && (
              <div className="absolute right-0 top-full mt-1 bg-[#1a1a1a] border border-white/10 rounded-lg shadow-xl z-50 min-w-[160px] py-1">
                <button
                  onClick={() => handleExport('pdf')}
                  disabled={!!exporting}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm text-white/70 hover:text-white hover:bg-white/5 transition-colors disabled:opacity-50"
                >
                  {exporting === 'pdf' ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileText className="h-4 w-4 text-red-400" />}
                  Export as PDF
                </button>
                <button
                  onClick={() => handleExport('docx')}
                  disabled={!!exporting}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm text-white/70 hover:text-white hover:bg-white/5 transition-colors disabled:opacity-50"
                >
                  {exporting === 'docx' ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileText className="h-4 w-4 text-blue-400" />}
                  Export as Word
                </button>
                <button
                  onClick={() => handleExport('xlsx')}
                  disabled={!!exporting}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm text-white/70 hover:text-white hover:bg-white/5 transition-colors disabled:opacity-50"
                >
                  {exporting === 'xlsx' ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileSpreadsheet className="h-4 w-4 text-green-400" />}
                  Export as Excel
                </button>
                <button
                  onClick={() => handleExport('pptx')}
                  disabled={!!exporting}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm text-white/70 hover:text-white hover:bg-white/5 transition-colors disabled:opacity-50"
                >
                  {exporting === 'pptx' ? <Loader2 className="h-4 w-4 animate-spin" /> : <Presentation className="h-4 w-4 text-orange-400" />}
                  Export as PowerPoint
                </button>
                <button
                  onClick={() => handleExport('markdown')}
                  disabled={!!exporting}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm text-white/70 hover:text-white hover:bg-white/5 transition-colors disabled:opacity-50"
                >
                  {exporting === 'markdown' ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileText className="h-4 w-4 text-white/60" />}
                  Export as Markdown
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Sources */}
      {sources.length > 0 && (
        <div className="mt-4 pt-4 border-t border-white/10">
          <p className="text-xs font-medium text-white/50 mb-2">Sources ({sources.length})</p>
          <div className="flex flex-wrap gap-2">
            {sources.map((source, i) => (
              <a
                key={i}
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1.5 px-2.5 py-1.5 bg-white/5 hover:bg-[#3d655c]/10 border border-white/10 hover:border-[#3d655c]/30 rounded-lg text-xs text-white/70 hover:text-white transition-all"
              >
                <Globe className="h-3 w-3" />
                <span className="truncate max-w-[150px]">{source.title}</span>
                <ExternalLink className="h-3 w-3 flex-shrink-0" />
              </a>
            ))}
          </div>
        </div>
      )}

      {/* Follow-up Questions */}
      {followUpQuestions.length > 0 && (
        <div className="mt-4 pt-4 border-t border-white/10">
          <p className="text-xs font-medium text-white/50 mb-2">Continue exploring</p>
          <div className="flex flex-wrap gap-2">
            {followUpQuestions.map((question, i) => (
              <button
                key={i}
                onClick={() => onFollowUpClick(question)}
                className="px-3 py-1.5 bg-white/5 hover:bg-[#3d655c]/10 border border-white/10 hover:border-[#3d655c]/30 rounded-lg text-xs text-white/70 hover:text-white transition-all text-left"
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
// Chat Sidebar Component - Premium bubble styling
// =============================================================================

interface ChatSidebarProps {
  conversations: Conversation[];
  currentConversation: Conversation | null;
  isOpen: boolean;
  onToggle: () => void;
  onSelectConversation: (conv: Conversation) => void;
  onDeleteConversation: (id: string) => void;
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
            className="w-10 h-10 flex items-center justify-center text-white/60 hover:text-white hover:bg-[#3d655c]/10 rounded-lg transition-colors"
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
            className="h-8 w-8 flex items-center justify-center text-white/50 hover:text-white hover:bg-[#3d655c]/10 rounded-lg transition-colors"
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
              "bg-gradient-to-r from-[#3d655c] to-[#3d665c] text-white hover:from-[#1a8a62] hover:to-[#2d7a35]",
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
                "focus:border-[#3d655c]/40 focus:outline-none focus:ring-1 focus:ring-[#3d655c]/20",
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
  const router = useRouter();
  
  const handleDomainClick = (sectorId: Sector) => {
    setSector(sectorId);
    // Navigate to domain page (except for 'all' which stays on dashboard)
    if (sectorId !== 'all') {
      router.push(`/domain/${sectorId}`);
    }
  };

  return (
    <div className="flex items-center gap-1 overflow-x-auto scrollbar-hide">
      {SECTORS.map((sector) => (
        <button
          key={sector.id}
          onClick={() => handleDomainClick(sector.id)}
          className={cn(
            "px-3 py-1.5 text-[13px] font-medium rounded-lg transition-all whitespace-nowrap",
            currentSector === sector.id
              ? "text-white bg-[#3d655c]/20 shadow-[0_0_10px_rgba(23,123,87,0.3)]"
              : "text-white/60 hover:text-white hover:bg-white/[0.05]"
          )}
        >
          {sector.label}
        </button>
      ))}
    </div>
  );
}

// =============================================================================
// Profile Dropdown Component
// =============================================================================

function ProfileDropdown() {
  const { user, signOut } = useAuth();
  const router = useRouter();
  const [isOpen, setIsOpen] = useState(false);
  const [userProfile, setUserProfile] = useState<{ name: string | null; profile_image: string | null } | null>(null);
  const [creditBalance, setCreditBalance] = useState(50);
  const [plan, setPlan] = useState('free');
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

  useEffect(() => {
    if (!user) return;
    
    const fetchUserData = async () => {
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
      {/* Profile Button */}
      <div ref={menuRef} className="relative">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className={cn(
            'w-8 h-8 rounded-full flex items-center justify-center overflow-hidden',
            'border border-white/[0.12] hover:border-[#3d655c]/50 hover:bg-[#3d655c]/10',
            'transition-all duration-200',
            isOpen && 'ring-2 ring-[#3d655c]/30'
          )}
        >
          {avatarUrl ? (
            <img src={avatarUrl} alt="Profile" className="w-full h-full object-cover" />
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-[#3d655c] to-[#3d665c] flex items-center justify-center">
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
                <span className="font-medium text-[#6b9b8a]">{creditBalance}</span> credits available
              </div>
            </div>
            
            {/* Menu Items */}
            <div className="py-1">
              <Link
                href="/settings"
                onClick={() => setIsOpen(false)}
                className="flex items-center gap-3 px-3 py-2.5 text-sm text-white/80 hover:bg-[#3d655c]/10 hover:text-white transition-colors"
              >
                <User className="h-4 w-4" />
                Profile
              </Link>
              <Link
                href="/billing"
                onClick={() => setIsOpen(false)}
                className="flex items-center gap-3 px-3 py-2.5 text-sm text-white/80 hover:bg-[#3d655c]/10 hover:text-white transition-colors"
              >
                <CreditCard className="h-4 w-4" />
                Billing & Credits
              </Link>
              <Link
                href="/preferences"
                onClick={() => setIsOpen(false)}
                className="flex items-center gap-3 px-3 py-2.5 text-sm text-white/80 hover:bg-[#3d655c]/10 hover:text-white transition-colors"
              >
                <Settings className="h-4 w-4" />
                Workspace Preferences
              </Link>
            </div>
            
            <div className="border-t border-white/10 py-1">
              <Link
                href="/contact"
                onClick={() => setIsOpen(false)}
                className="flex items-center gap-3 px-3 py-2.5 text-sm text-white/80 hover:bg-[#3d655c]/10 hover:text-white transition-colors"
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
// File Upload Button Component - FIXED: Actually uploads files
// =============================================================================

function FileUploadButton({ 
  onFileSelect,
  onOpenImageGenerator,
  attachedFiles,
  onRemoveFile
}: { 
  onFileSelect: (file: File) => void;
  onOpenImageGenerator: () => void;
  attachedFiles: AttachedFile[];
  onRemoveFile: (index: number) => void;
}) {
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
      // Reset input so same file can be selected again
      e.target.value = '';
    }
  };

  return (
    <div ref={menuRef} className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "h-10 w-10 rounded-xl flex items-center justify-center transition-all",
          "bg-white/[0.05] text-white/50 hover:text-white hover:bg-[#3d655c]/10 hover:border-[#3d655c]/30",
          "border border-white/[0.08]",
          isOpen && "bg-[#3d655c]/10 text-white border-[#3d655c]/30",
          attachedFiles.length > 0 && "bg-[#3d655c]/20 border-[#3d655c]/40"
        )}
      >
        <Plus className="w-5 h-5" />
        {attachedFiles.length > 0 && (
          <span className="absolute -top-1 -right-1 w-4 h-4 bg-[#3d655c] text-white text-[10px] rounded-full flex items-center justify-center">
            {attachedFiles.length}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute bottom-full left-0 mb-2 w-48 bg-[#1A1A1A] border border-white/[0.08] rounded-lg shadow-xl overflow-hidden z-50">
          <button
            onClick={() => fileInputRef.current?.click()}
            className="w-full flex items-center gap-3 px-3 py-2.5 text-sm text-white/70 hover:text-white hover:bg-[#3d655c]/10 transition-colors"
          >
            <Paperclip className="w-4 h-4" />
            Upload File
          </button>
          <button
            onClick={() => {
              onOpenImageGenerator();
              setIsOpen(false);
            }}
            className="w-full flex items-center gap-3 px-3 py-2.5 text-sm text-white/70 hover:text-white hover:bg-[#3d655c]/10 transition-colors"
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
        accept="image/*,.pdf,.doc,.docx,.txt,.xlsx,.xls,.pptx,.ppt,.csv"
      />
    </div>
  );
}

// =============================================================================
// Attached Files Display Component
// =============================================================================

function AttachedFilesDisplay({ 
  files, 
  onRemove 
}: { 
  files: AttachedFile[]; 
  onRemove: (index: number) => void;
}) {
  if (files.length === 0) return null;

  const getFileIcon = (type: string) => {
    if (type.startsWith('image/')) return <ImageIcon className="w-4 h-4" />;
    if (type.includes('pdf')) return <FileText className="w-4 h-4 text-red-400" />;
    if (type.includes('word') || type.includes('doc')) return <FileText className="w-4 h-4 text-blue-400" />;
    if (type.includes('excel') || type.includes('sheet') || type.includes('csv')) return <FileText className="w-4 h-4 text-green-400" />;
    if (type.includes('presentation') || type.includes('powerpoint')) return <FileText className="w-4 h-4 text-orange-400" />;
    return <File className="w-4 h-4" />;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="flex flex-wrap gap-2 mb-2">
      {files.map((file, index) => (
        <div
          key={index}
          className="flex items-center gap-2 px-3 py-1.5 bg-white/5 border border-white/10 rounded-lg group"
        >
          {getFileIcon(file.type)}
          <span className="text-xs text-white/70 max-w-[120px] truncate">{file.name}</span>
          <span className="text-xs text-white/40">{formatFileSize(file.size)}</span>
          <button
            onClick={() => onRemove(index)}
            className="text-white/40 hover:text-red-400 transition-colors"
          >
            <X className="w-3 h-3" />
          </button>
        </div>
      ))}
    </div>
  );
}

// =============================================================================
// Image Generation Modal Component
// =============================================================================

function ImageGenerationModal({
  isOpen,
  onClose,
  onImageGenerated
}: {
  isOpen: boolean;
  onClose: () => void;
  onImageGenerated: (imageUrl: string) => void;
}) {
  const [prompt, setPrompt] = useState('');
  const [style, setStyle] = useState('fashion');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedImage, setGeneratedImage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const styles = [
    { id: 'fashion', label: 'Fashion' },
    { id: 'streetwear', label: 'Streetwear' },
    { id: 'minimalist', label: 'Minimalist' },
    { id: 'luxury', label: 'Luxury' },
    { id: 'sustainable', label: 'Sustainable' },
    { id: 'avant-garde', label: 'Avant-Garde' },
  ];

  const handleGenerate = async () => {
    if (!prompt.trim() || isGenerating) return;
    
    setIsGenerating(true);
    setError(null);
    setGeneratedImage(null);
    
    try {
      const response = await fetch(`${API_URL}/api/image/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: prompt,
          style: style,
          width: 1024,
          height: 1024
        })
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || data.error || 'Image generation failed');
      }
      
      if (data.success && data.image_url) {
        setGeneratedImage(data.image_url);
      } else {
        throw new Error('No image generated');
      }
    } catch (err) {
      console.error('Image generation error:', err);
      setError(err instanceof Error ? err.message : 'Failed to generate image');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleUseImage = () => {
    if (generatedImage) {
      onImageGenerated(generatedImage);
      onClose();
      setPrompt('');
      setGeneratedImage(null);
    }
  };

  const handleDownload = async () => {
    if (!generatedImage) return;
    
    try {
      const response = await fetch(generatedImage);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `mcleuker-ai-${Date.now()}.png`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Download error:', err);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-[#1A1A1A] border border-white/[0.08] rounded-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[#3d655c] to-[#3d665c] flex items-center justify-center">
              <ImageIcon className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">Generate Image</h3>
              <p className="text-xs text-white/50">Powered by AI</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-white/50 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 space-y-4">
          {/* Style Selection */}
          <div>
            <label className="text-sm text-white/70 mb-2 block">Style</label>
            <div className="flex flex-wrap gap-2">
              {styles.map((s) => (
                <button
                  key={s.id}
                  onClick={() => setStyle(s.id)}
                  className={cn(
                    "px-3 py-1.5 text-sm rounded-lg border transition-all",
                    style === s.id
                      ? "bg-[#3d655c]/20 border-[#3d655c] text-white"
                      : "bg-white/5 border-white/10 text-white/60 hover:text-white hover:border-white/20"
                  )}
                >
                  {s.label}
                </button>
              ))}
            </div>
          </div>

          {/* Prompt Input */}
          <div>
            <label className="text-sm text-white/70 mb-2 block">Prompt</label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe the image you want to generate..."
              className="w-full h-24 px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder:text-white/30 focus:border-[#3d655c]/50 focus:outline-none resize-none"
            />
          </div>

          {/* Error Display */}
          {error && (
            <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
              <p className="text-sm text-red-400">{error}</p>
            </div>
          )}

          {/* Generated Image Preview */}
          {generatedImage && (
            <div className="space-y-3">
              <img
                src={generatedImage}
                alt="Generated"
                className="w-full rounded-lg border border-white/10"
              />
              <div className="flex gap-2">
                <button
                  onClick={handleDownload}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-white/70 hover:text-white transition-colors"
                >
                  <Download className="w-4 h-4" />
                  Download
                </button>
                <button
                  onClick={handleUseImage}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-[#3d655c] hover:bg-[#1a8a62] text-white rounded-lg transition-colors"
                >
                  <Check className="w-4 h-4" />
                  Use Image
                </button>
              </div>
            </div>
          )}

          {/* Generate Button */}
          {!generatedImage && (
            <button
              onClick={handleGenerate}
              disabled={!prompt.trim() || isGenerating}
              className={cn(
                "w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-medium transition-all",
                prompt.trim() && !isGenerating
                  ? "bg-gradient-to-r from-[#3d655c] to-[#3d665c] text-white hover:from-[#1a8a62] hover:to-[#2d7a35]"
                  : "bg-white/5 text-white/30 cursor-not-allowed"
              )}
            >
              {isGenerating ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Generate Image (3 credits)
                </>
              )}
            </button>
          )}
        </div>
      </div>
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
  const [showImageGenerator, setShowImageGenerator] = useState(false);
  const [attachedFiles, setAttachedFiles] = useState<AttachedFile[]>([]);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const currentConversationIdRef = useRef<string | null>(null);

  // Track current conversation ID for abort handling
  useEffect(() => {
    currentConversationIdRef.current = currentConversation?.id || null;
  }, [currentConversation]);

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

  // Handle file upload - FIXED: Actually reads and stores file
  const handleFileSelect = async (file: File) => {
    try {
      // Read file as base64 for sending to backend
      const reader = new FileReader();
      reader.onload = () => {
        const base64 = reader.result as string;
        const newFile: AttachedFile = {
          name: file.name,
          type: file.type,
          size: file.size,
          base64: base64
        };
        setAttachedFiles(prev => [...prev, newFile]);
      };
      reader.readAsDataURL(file);
    } catch (error) {
      console.error('Error reading file:', error);
      alert('Failed to attach file. Please try again.');
    }
  };

  // Remove attached file
  const handleRemoveFile = (index: number) => {
    setAttachedFiles(prev => prev.filter((_, i) => i !== index));
  };

  // Handle image generated from modal
  const handleImageGenerated = (imageUrl: string) => {
    // Add the generated image as an attached file
    const newFile: AttachedFile = {
      name: 'generated-image.png',
      type: 'image/png',
      size: 0,
      url: imageUrl
    };
    setAttachedFiles(prev => [...prev, newFile]);
  };

  // Send message with chat history saving - FIXED: Proper abort handling
  const handleSendMessage = async (overrideMessage?: string) => {
    const messageText = overrideMessage || input.trim();
    if (!messageText || isStreaming) return;

    // Cancel any existing stream
    if (globalAbortController) {
      globalAbortController.abort();
    }
    globalAbortController = new AbortController();
    const currentAbortController = globalAbortController;

    setInput('');
    setIsStreaming(true);
    const currentFiles = [...attachedFiles];
    setAttachedFiles([]);

    // Create or get conversation
    let conversationId = currentConversation?.id;
    if (!conversationId) {
      const newConv = await createConversation(messageText.slice(0, 50));
      if (newConv) {
        conversationId = newConv.id;
      }
    }

    // Store conversation ID for this request
    const requestConversationId = conversationId;

    // Add user message with attached files
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: messageText,
      reasoning_layers: [],
      sources: [],
      follow_up_questions: [],
      timestamp: new Date(),
      isStreaming: false,
      attachedFiles: currentFiles.length > 0 ? currentFiles : undefined,
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
          files: currentFiles.length > 0 ? currentFiles.map(f => ({
            name: f.name,
            type: f.type,
            base64: f.base64,
            url: f.url
          })) : undefined,
        }),
        signal: currentAbortController.signal,
      });

      if (!response.ok) throw new Error('API error');

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (reader) {
        while (true) {
          // Check if aborted
          if (currentAbortController.signal.aborted) {
            break;
          }

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

                // Save assistant message to database with full metadata
                if (requestConversationId && user) {
                  try {
                    // Store complete metadata including sources, reasoning, and suggestions
                    // Convert to JSON-serializable format
                    const messageMetadata = JSON.stringify({
                      sources: eventData.sources || currentSources,
                      reasoning_layers: currentLayers.map(l => ({
                        id: l.id,
                        layer_num: l.layer_num,
                        type: l.type,
                        title: l.title,
                        content: l.content,
                        sub_steps: l.sub_steps || [],
                        status: l.status,
                      })),
                      follow_up_questions: followUpQuestions,
                      search_mode: searchMode,
                    });
                    
                    await supabase.from('chat_messages').insert({
                      conversation_id: requestConversationId,
                      user_id: user.id,
                      role: 'assistant',
                      content: finalContent,
                      model_used: 'grok-4',
                      credits_used: creditsUsed,
                      metadata: JSON.parse(messageMetadata),
                    });
                    
                    // Update conversation title if it's a new conversation
                    if (messages.length === 0) {
                      await updateConversationTitle(requestConversationId, messageText.slice(0, 50));
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
      // Don't show error if aborted intentionally
      if (error instanceof Error && error.name === 'AbortError') {
        console.log('Request aborted');
        return;
      }
      
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
      if (globalAbortController === currentAbortController) {
        globalAbortController = null;
      }
    }
  };

  const handleNewChat = () => {
    // Abort any ongoing stream
    if (globalAbortController) {
      globalAbortController.abort();
      globalAbortController = null;
    }
    setMessages([]);
    setIsStreaming(false);
    startNewChat();
  };

  const handleSelectConversation = async (conv: Conversation) => {
    // Warn user if streaming is in progress
    if (isStreaming) {
      const confirmed = window.confirm(
        'A response is currently being generated. Switching conversations will stop the generation. Continue?'
      );
      if (!confirmed) return;
      
      // Abort the stream if user confirms
      if (globalAbortController) {
        globalAbortController.abort();
        globalAbortController = null;
      }
      setIsStreaming(false);
    }
    
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

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement | HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Dynamic starter questions - randomized from a larger pool each time
  const allStarterQuestions = [
    // Fashion
    "What are the latest trends in sustainable fashion?",
    "How is Gen Z reshaping fashion consumption?",
    "Which emerging designers should I watch in 2026?",
    "What's driving the resale and secondhand market boom?",
    // Beauty
    "How is AI transforming the beauty industry?",
    "What are the top skincare innovations this year?",
    "How are beauty brands adapting to clean beauty demands?",
    "What's the future of personalized beauty?",
    // Luxury
    "Analyze the luxury market outlook for 2026",
    "How are luxury brands embracing digital experiences?",
    "What's driving luxury consumer behavior changes?",
    "Which luxury brands are leading in sustainability?",
    // Textile & Manufacturing
    "What innovations are shaping textile manufacturing?",
    "How is 3D printing changing fashion production?",
    "What are the most sustainable fabric alternatives?",
    "How are supply chains becoming more transparent?",
    // Sustainability
    "What are the biggest sustainability challenges in fashion?",
    "How are brands measuring their environmental impact?",
    "What's the future of circular fashion?",
    "Which certifications matter most for sustainable fashion?",
    // Tech & Innovation
    "How is blockchain being used in fashion?",
    "What role does AI play in trend forecasting?",
    "How are virtual try-ons changing e-commerce?",
    "What's the impact of the metaverse on fashion?",
  ];
  
  // Randomly select 4 questions on each render
  const [starterQuestions] = useState(() => {
    const shuffled = [...allStarterQuestions].sort(() => Math.random() - 0.5);
    return shuffled.slice(0, 4);
  });

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
              /* STATE A: Empty State - "Where is my mind?" with search bar and suggestions */
              <div className="flex flex-col items-center justify-center min-h-[60vh]">
                {/* Title */}
                <h1 className="text-2xl md:text-3xl font-bold text-white mb-2 text-center">
                  Where is my mind?
                </h1>
                {/* Subtitle */}
                <p className="text-white/50 max-w-md text-center mb-6">
                  Give me chaos — I'll return a map.
                </p>
                
                {/* Search Bar - Directly under title */}
                <div className="w-full max-w-xl mb-6">
                  <div className="flex items-center gap-2 p-3 rounded-2xl bg-[#141414] border border-white/[0.08] hover:border-[#3d655c]/30 transition-all">
                    <FileUploadButton
                      onFileSelect={handleFileSelect}
                      onOpenImageGenerator={() => setShowImageGenerator(true)}
                      attachedFiles={attachedFiles}
                      onRemoveFile={handleRemoveFile}
                    />
                    <input
                      type="text"
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyDown={handleKeyDown}
                      placeholder="Ask me anything..."
                      className="flex-1 bg-transparent text-white placeholder:text-white/30 focus:outline-none text-sm"
                    />
                    <button
                      onClick={() => handleSendMessage()}
                      disabled={!input.trim() || isStreaming}
                      className={cn(
                        "h-9 w-9 rounded-xl flex items-center justify-center transition-all flex-shrink-0",
                        input.trim() && !isStreaming
                          ? "bg-[#3d655c] text-white hover:bg-[#4a7a6d]"
                          : "bg-white/[0.05] text-white/30"
                      )}
                    >
                      {isStreaming ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Send className="h-4 w-4" />
                      )}
                    </button>
                  </div>
                  
                  {/* Quick/Deep Mode Toggle - Under search bar */}
                  <div className="flex justify-center mt-3">
                    <div className="flex items-center gap-1 p-1 bg-white/[0.03] rounded-full border border-white/[0.08]">
                      <button
                        onClick={() => setSearchMode('quick')}
                        className={cn(
                          "flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all",
                          searchMode === 'quick'
                            ? "bg-[#3d655c]/20 text-white"
                            : "text-white/50 hover:text-white/70"
                        )}
                      >
                        <Zap className="h-3 w-3" />
                        Quick
                      </button>
                      <button
                        onClick={() => setSearchMode('deep')}
                        className={cn(
                          "flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all",
                          searchMode === 'deep'
                            ? "bg-[#3d655c]/20 text-white"
                            : "text-white/50 hover:text-white/70"
                        )}
                      >
                        <Brain className="h-3 w-3" />
                        Deep
                      </button>
                    </div>
                  </div>
                </div>
                
                {/* Suggestion Cards - Under search bar */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-xl">
                  {starterQuestions.map((question, i) => (
                    <button
                      key={i}
                      onClick={() => handleSendMessage(question)}
                      className={cn(
                        "text-left p-3 rounded-xl transition-all",
                        "mcleuker-bubble",
                        i % 4 === 0 && "mcleuker-bubble-v1",
                        i % 4 === 1 && "mcleuker-bubble-v2",
                        i % 4 === 2 && "mcleuker-bubble-v3",
                        i % 4 === 3 && "mcleuker-bubble-v4"
                      )}
                    >
                      <p className="text-xs sm:text-sm text-white/80 line-clamp-2">{question}</p>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              /* STATE B: Chat Messages */
              <div className="space-y-6">
                {messages.map((message, index) => (
                  <div
                    key={message.id}
                    className={cn(
                      "flex",
                      message.role === 'user' ? "justify-end" : "justify-start"
                    )}
                  >
                    <div className={cn(
                      "max-w-[85%]",
                      message.role === 'user' 
                        ? "mcleuker-user-bubble rounded-2xl rounded-tr-md px-4 py-3"
                        : "bg-[#141414] rounded-xl rounded-tl-md px-4 py-3"
                    )}>
                      {/* User message with attached files */}
                      {message.role === 'user' && (
                        <div>
                          {message.attachedFiles && message.attachedFiles.length > 0 && (
                            <div className="mb-2 flex flex-wrap gap-2">
                              {message.attachedFiles.map((file, i) => (
                                <div key={i} className="flex items-center gap-1.5 px-2 py-1 bg-white/10 rounded text-xs text-white/70">
                                  <Paperclip className="w-3 h-3" />
                                  {file.name}
                                </div>
                              ))}
                            </div>
                          )}
                          <p className="text-white text-sm leading-relaxed">{message.content}</p>
                        </div>
                      )}
                      
                      {/* Assistant message */}
                      {message.role === 'assistant' && (
                        <div className="space-y-3">
                          {/* Reasoning Layers */}
                          {message.reasoning_layers.length > 0 && (
                            <div className="space-y-1 mb-4">
                              <p className="text-xs text-white/40 mb-2">Reasoning...</p>
                              {message.reasoning_layers.map((layer, layerIndex) => (
                                <ReasoningLayerItem
                                  key={layer.id}
                                  layer={layer}
                                  isLatest={layerIndex === message.reasoning_layers.length - 1}
                                  onToggleExpand={() => toggleLayerExpand(message.id, layer.id)}
                                />
                              ))}
                            </div>
                          )}
                          
                          {/* Streaming indicator */}
                          {message.isStreaming && !message.content && (
                            <div className="flex items-center gap-2 text-white/50">
                              <Loader2 className="h-4 w-4 animate-spin" />
                              <span className="text-sm">Thinking...</span>
                            </div>
                          )}
                          
                          {/* Content */}
                          {message.content && (
                            <MessageContent
                              content={message.content}
                              sources={message.sources}
                              followUpQuestions={message.follow_up_questions}
                              onFollowUpClick={handleSendMessage}
                            />
                          )}
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

        {/* Input Area - Fixed at bottom (only show when there are messages) */}
        {messages.length > 0 && (
          <div className="sticky bottom-0 bg-gradient-to-t from-[#070707] via-[#070707] to-transparent pt-6 pb-4">
            <div className="max-w-3xl mx-auto px-4">
              {/* Attached Files Display */}
              <AttachedFilesDisplay 
                files={attachedFiles} 
                onRemove={handleRemoveFile} 
              />
              
              {/* Quick/Deep Mode Toggle - Centered (no credit numbers) */}
              <div className="flex justify-center mb-3">
                <div className="flex items-center gap-1 p-1 bg-white/[0.03] rounded-full border border-white/[0.08]">
                  <button
                    onClick={() => setSearchMode('quick')}
                    className={cn(
                      "flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all",
                      searchMode === 'quick'
                        ? "bg-[#3d655c]/20 text-white"
                        : "text-white/50 hover:text-white/70"
                    )}
                  >
                    <Zap className="h-3 w-3" />
                    Quick
                  </button>
                  <button
                    onClick={() => setSearchMode('deep')}
                    className={cn(
                      "flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all",
                      searchMode === 'deep'
                        ? "bg-[#3d655c]/20 text-white"
                        : "text-white/50 hover:text-white/70"
                    )}
                  >
                    <Brain className="h-3 w-3" />
                    Deep
                  </button>
                </div>
              </div>
              
              {/* Input Container */}
              <div className="flex items-end gap-2 p-2 rounded-2xl border transition-all bg-[#141414] border-white/[0.08]">
                {/* Plus Button */}
                <FileUploadButton
                  onFileSelect={handleFileSelect}
                  onOpenImageGenerator={() => setShowImageGenerator(true)}
                  attachedFiles={attachedFiles}
                  onRemoveFile={handleRemoveFile}
                />
                
                {/* Text Input */}
                <textarea
                  ref={textareaRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask me anything..."
                  rows={1}
                  className={cn(
                    "flex-1 bg-transparent text-white placeholder:text-white/30 resize-none",
                    "focus:outline-none text-sm leading-relaxed py-2.5 px-2",
                    "max-h-[200px]"
                  )}
                />
                
                {/* Send Button */}
                <button
                  onClick={() => handleSendMessage()}
                  disabled={!input.trim() || isStreaming}
                  className={cn(
                    "h-10 w-10 rounded-xl flex items-center justify-center transition-all flex-shrink-0",
                    input.trim() && !isStreaming
                      ? "bg-[#3d655c] text-white hover:bg-[#4a7a6d]"
                      : "bg-white/[0.05] text-white/30"
                  )}
                >
                  {isStreaming ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </button>
              </div>
              
              {/* Helper Text */}
              <div className="flex items-center justify-center gap-4 mt-2">
                <p className="text-[10px] text-white/30">
                  Press Enter to send • Shift + Enter for new line
                </p>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Image Generation Modal */}
      <ImageGenerationModal
        isOpen={showImageGenerator}
        onClose={() => setShowImageGenerator(false)}
        onImageGenerated={handleImageGenerated}
      />
    </div>
  );
}

// =============================================================================
// Protected Dashboard Page
// =============================================================================

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}
