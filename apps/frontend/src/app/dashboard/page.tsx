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

interface DownloadFile {
  filename: string;
  download_url: string;
  file_id: string;
  file_type: string;
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
  downloads?: DownloadFile[];
  toolStatus?: string;
  toolProgress?: { message: string; tools: string[] }[];
  searchSources?: { title: string; url: string; source: string }[];
  taskSteps?: { step: string; title: string; status: 'active' | 'complete' | 'pending'; detail?: string }[];
  _taskExpanded?: boolean;
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
    if (layer.status === 'complete') return 'text-[#5c6652]';
    switch (layer.type) {
      case 'understanding': return 'text-[#2E3524]';
      case 'planning': return 'text-[#2A3021]';
      case 'research': return 'text-[#2A3021]';
      case 'analysis': return 'text-[#4c7748]';
      case 'synthesis': return 'text-[#457556]';
      case 'writing': return 'text-emerald-400';
      default: return 'text-white/60';
    }
  };

  return (
    <div className="border-l-2 border-[#2E3524]/30 pl-3 py-1">
      <button
        onClick={onToggleExpand}
        className={cn(
          "flex items-center gap-2 w-full text-left py-1.5 px-2 rounded-lg transition-all",
          isLatest && layer.status === 'active' ? "bg-[#2E3524]/10" : "hover:bg-[#2E3524]/5"
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
          <Loader2 className="h-3 w-3 animate-spin text-[#2E3524] flex-shrink-0" />
        )}
      </button>
      
      {/* Sub-steps - Expandable */}
      {layer.expanded && layer.sub_steps.length > 0 && (
        <div className="ml-6 mt-1 space-y-1">
          {layer.sub_steps.map((subStep, i) => (
            <div key={i} className="flex items-start gap-2 py-1">
              <div className={cn(
                "mt-1 w-1.5 h-1.5 rounded-full flex-shrink-0",
                subStep.status === 'complete' ? "bg-green-400" : "bg-[#2E3524]/50"
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
        <div className="ml-6 mt-2 p-2 rounded bg-[#2E3524]/5 border border-[#2E3524]/20">
          <p className="text-xs text-white/60 leading-relaxed line-clamp-3">
            {layer.content}
          </p>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Sources Section Component - Expandable with clickable "+N more"
// =============================================================================

function SourcesSection({ 
  sources, 
  ensureValidUrl 
}: { 
  sources: Source[]; 
  ensureValidUrl: (url: string) => string;
}) {
  const [showAll, setShowAll] = useState(false);
  const INITIAL_COUNT = 8;
  const displayedSources = showAll ? sources : sources.slice(0, INITIAL_COUNT);
  const hiddenCount = sources.length - INITIAL_COUNT;

  return (
    <div className="mt-3 pt-3 border-t border-white/[0.04]">
      <p className="text-[10px] text-white/30 uppercase tracking-wider mb-2">Sources ({sources.length})</p>
      <div className="flex flex-wrap gap-1.5">
        {displayedSources.map((source, i) => {
          const validUrl = ensureValidUrl(source.url);
          const isClickable = validUrl !== '#';
          let favicon = '';
          try {
            favicon = isClickable ? `https://www.google.com/s2/favicons?domain=${new URL(validUrl).hostname}&sz=16` : '';
          } catch { /* ignore */ }
          return isClickable ? (
            <a
              key={i}
              href={validUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 px-2 py-1 bg-white/[0.03] hover:bg-white/[0.06] border border-white/[0.06] hover:border-white/[0.12] rounded-lg text-[11px] text-white/50 hover:text-white/80 transition-all"
            >
              {favicon && <img src={favicon} alt="" className="w-3 h-3 rounded-sm" onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }} />}
              <span className="truncate max-w-[140px]">{source.title || 'Source'}</span>
            </a>
          ) : null; // Skip sources without valid URLs
        })}
        {!showAll && hiddenCount > 0 && (
          <button
            onClick={() => setShowAll(true)}
            className="flex items-center gap-1 px-2.5 py-1 bg-white/[0.03] hover:bg-white/[0.08] border border-white/[0.06] hover:border-[#5c6652]/40 rounded-lg text-[11px] text-[#8a9a7e] hover:text-[#aabaa0] transition-all cursor-pointer"
          >
            <span>+{hiddenCount} more</span>
            <ChevronDown className="h-3 w-3" />
          </button>
        )}
        {showAll && hiddenCount > 0 && (
          <button
            onClick={() => setShowAll(false)}
            className="flex items-center gap-1 px-2.5 py-1 bg-white/[0.03] hover:bg-white/[0.08] border border-white/[0.06] hover:border-[#5c6652]/40 rounded-lg text-[11px] text-[#8a9a7e] hover:text-[#aabaa0] transition-all cursor-pointer"
          >
            <span>Show less</span>
            <ChevronUp className="h-3 w-3" />
          </button>
        )}
      </div>
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
  onFollowUpClick,
  searchQuery = ''
}: { 
  content: string; 
  sources: Source[]; 
  followUpQuestions: string[];
  onFollowUpClick: (question: string) => void;
  searchQuery?: string;
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

  // Export document function - Fixed to handle two-step download
  const handleExport = async (format: string) => {
    setExporting(format);
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://web-production-29f3c.up.railway.app';
      
      // Step 1: Generate the document and get the download URL
      // Map frontend format names to backend FileType enum values
      const formatMap: Record<string, string> = {
        'pdf': 'pdf',
        'docx': 'word',
        'xlsx': 'excel',
        'pptx': 'pptx',
        'markdown': 'markdown',
        'csv': 'csv',
      };
      const backendFileType = formatMap[format] || format;
      
      const generateResponse = await fetch(`${API_URL}/api/v1/generate-file`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: content,
          file_type: backendFileType,
          prompt: searchQuery || 'McLeuker AI Report',
          title: 'McLeuker AI Report'
        })
      });

      if (!generateResponse.ok) {
        const errorData = await generateResponse.json().catch(() => ({}));
        throw new Error(errorData.error || 'Failed to generate document');
      }

      const result = await generateResponse.json();
      
      if (!result.success || !result.download_url) {
        throw new Error(result.error || 'Failed to generate document');
      }

      // Step 2: Download the actual file using the returned URL
      const fileResponse = await fetch(`${API_URL}${result.download_url}`);
      
      if (!fileResponse.ok) {
        throw new Error('Failed to download file');
      }

      // Get the blob and trigger download
      const blob = await fileResponse.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = result.filename || `mcleuker-report.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      setShowExportMenu(false);
    } catch (error) {
      console.error('Export error:', error);
      alert(error instanceof Error ? error.message : 'Failed to export document. Please try again.');
    } finally {
      setExporting(null);
    }
  };

  // Helper to validate and fix URLs
  const ensureValidUrl = (url: string): string => {
    if (!url || typeof url !== 'string') return '#';
    const trimmed = url.trim();
    // Already a valid absolute URL
    if (/^https?:\/\//i.test(trimmed)) return trimmed;
    // Protocol-relative URL
    if (trimmed.startsWith('//')) return `https:${trimmed}`;
    // Looks like a domain (e.g. "example.com/path")
    if (/^[a-zA-Z0-9][a-zA-Z0-9-]*\.[a-zA-Z]{2,}/.test(trimmed)) return `https://${trimmed}`;
    // Relative path or malformed - return as-is with hash fallback
    return trimmed.startsWith('/') ? trimmed : '#';
  };

  // Helper: highlight search matches in a text string
  const highlightSearchInText = (text: string, query: string): React.ReactNode[] => {
    if (!query || !query.trim()) return [text];
    const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`(${escaped})`, 'gi');
    const parts = text.split(regex);
    return parts.map((part, i) =>
      regex.test(part)
        ? <mark key={`hl-${i}`} className="bg-[#2E3524]/60 text-white rounded-sm px-0.5">{part}</mark>
        : part
    );
  };

  // Enhanced markdown rendering with bullet points, numbered lists, links, and emojis
  const renderContent = (text: string) => {
    const lines = text.split('\n');
    const elements: React.ReactNode[] = [];
    let listItems: string[] = [];
    let listType: 'ul' | 'ol' | null = null;
    let inCodeBlock = false;
    
    const processInlineFormatting = (line: string) => {
      // Process markdown links [text](url) and bold **text** together
      const combinedRegex = /\[([^\]]+)\]\(([^)]+)\)|\*\*(.*?)\*\*/g;
      const result: React.ReactNode[] = [];
      let lastIndex = 0;
      let match;
      let keyIdx = 0;

      while ((match = combinedRegex.exec(line)) !== null) {
        // Add text before this match (apply search highlighting to plain text)
        if (match.index > lastIndex) {
          const plainText = line.slice(lastIndex, match.index);
          result.push(...highlightSearchInText(plainText, searchQuery));
        }

        if (match[1] && match[2]) {
          // Markdown link: [text](url) - highlight inside link text
          const href = ensureValidUrl(match[2]);
          result.push(
            <a
              key={`link-${keyIdx++}`}
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className="text-[#7a8a6e] hover:text-[#9aaa8e] underline underline-offset-2 inline-flex items-center gap-0.5"
            >
              {highlightSearchInText(match[1], searchQuery)}
              <ExternalLink className="h-3 w-3 inline-block" />
            </a>
          );
        } else if (match[3]) {
          // Bold text: **text** - highlight inside bold
          result.push(<strong key={`bold-${keyIdx++}`} className="text-white font-medium">{highlightSearchInText(match[3], searchQuery)}</strong>);
        }

        lastIndex = match.index + match[0].length;
      }

      // Add remaining text (apply search highlighting)
      if (lastIndex < line.length) {
        const remaining = line.slice(lastIndex);
        result.push(...highlightSearchInText(remaining, searchQuery));
      }

      return result.length > 0 ? result : highlightSearchInText(line, searchQuery);
    };
    
    const flushList = () => {
      if (listItems.length > 0 && listType) {
        const ListTag = listType === 'ul' ? 'ul' : 'ol';
        elements.push(
          <ListTag key={`list-${elements.length}`} className={`${listType === 'ul' ? 'list-disc' : 'list-decimal'} list-inside space-y-0.5 my-1.5 ml-2`}>
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
      // Code block toggle (``` fences) - skip highlighting inside code blocks
      if (line.trim().startsWith('```')) {
        flushList();
        if (!inCodeBlock) {
          // Opening code block
          inCodeBlock = true;
          const lang = line.trim().slice(3).trim();
          elements.push(
            <div key={`cb-start-${i}`} className="mt-3 rounded-t-lg bg-white/[0.04] border border-white/[0.06] border-b-0 px-3 py-1.5 flex items-center gap-2">
              <div className="flex gap-1">
                <span className="w-2 h-2 rounded-full bg-white/10" />
                <span className="w-2 h-2 rounded-full bg-white/10" />
                <span className="w-2 h-2 rounded-full bg-white/10" />
              </div>
              {lang && <span className="text-[10px] text-white/30 uppercase tracking-wider">{lang}</span>}
            </div>
          );
        } else {
          // Closing code block
          inCodeBlock = false;
          elements.push(
            <div key={`cb-end-${i}`} className="rounded-b-lg bg-[#111] border border-white/[0.06] border-t-0 h-2" />
          );
        }
        return;
      }

      // Inside code block - render as-is without search highlighting
      if (inCodeBlock) {
        elements.push(
          <pre key={i} className="text-[13px] text-white/70 font-mono bg-[#111] border-x border-white/[0.06] px-4 py-0.5 leading-relaxed overflow-x-auto">{line}</pre>
        );
        return;
      }

      // Empty line
      if (!line.trim()) {
        flushList();
        elements.push(<br key={i} />);
        return;
      }
      
      // Markdown table row
      if (line.trim().startsWith('|') && line.trim().endsWith('|')) {
        // Check if this is a separator row (|---|---|)
        if (/^\|[\s\-:|]+\|$/.test(line.trim())) return;
        
        // Collect table rows
        if (!elements.length || !(elements[elements.length - 1] as any)?._tableRows) {
          // Start new table collection
          const tableRows: string[][] = [];
          const cells = line.trim().split('|').filter((_, idx, arr) => idx > 0 && idx < arr.length - 1).map(c => c.trim());
          tableRows.push(cells);
          
          // Look ahead for more table rows
          let j = i + 1;
          while (j < lines.length && lines[j].trim().startsWith('|') && lines[j].trim().endsWith('|')) {
            if (!/^\|[\s\-:|]+\|$/.test(lines[j].trim())) {
              const rowCells = lines[j].trim().split('|').filter((_, idx, arr) => idx > 0 && idx < arr.length - 1).map(c => c.trim());
              tableRows.push(rowCells);
            }
            j++;
          }
          
          if (tableRows.length > 0) {
            elements.push(
              <div key={`table-${i}`} className="my-2 overflow-x-auto rounded-lg border border-white/[0.08]">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="bg-white/[0.06]">
                      {tableRows[0].map((cell, ci) => (
                        <th key={ci} className="px-3 py-2 text-left text-white/70 font-semibold border-b border-white/[0.08]">
                          {processInlineFormatting(cell)}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {tableRows.slice(1).map((row, ri) => (
                      <tr key={ri} className={ri % 2 === 0 ? 'bg-white/[0.02]' : 'bg-transparent'}>
                        {row.map((cell, ci) => (
                          <td key={ci} className="px-3 py-1.5 text-white/60 border-b border-white/[0.04]">
                            {processInlineFormatting(cell)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            );
            // Skip the rows we already processed (they'll be skipped by forEach)
            // Mark them to skip
            for (let k = i + 1; k < j; k++) {
              lines[k] = ''; // Clear already-processed table rows
            }
          }
        }
        return;
      }
      
      // Headers (apply search highlighting)
      if (line.startsWith('### ')) {
        flushList();
        elements.push(<h3 key={i} className="text-base font-semibold text-white mt-3 mb-1">{highlightSearchInText(line.slice(4), searchQuery)}</h3>);
        return;
      }
      if (line.startsWith('## ')) {
        flushList();
        elements.push(<h2 key={i} className="text-lg font-semibold text-white mt-3 mb-1.5">{highlightSearchInText(line.slice(3), searchQuery)}</h2>);
        return;
      }
      if (line.startsWith('# ')) {
        flushList();
        elements.push(<h1 key={i} className="text-xl font-bold text-white mt-4 mb-2">{highlightSearchInText(line.slice(2), searchQuery)}</h1>);
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
        <p key={i} className="text-white/80 leading-relaxed mb-1">
          {processInlineFormatting(line)}
        </p>
      );
    });
    
    flushList();
    return elements;
  };

  return (
    <div className="space-y-0">
      {/* Response Content */}
      <div className="relative">
        <div className={cn(
          "prose prose-invert prose-sm max-w-none",
          !expanded && "max-h-[400px] overflow-hidden"
        )}>
          {renderContent(content)}
        </div>
        
        {content.length > 1500 && (
          <div className={cn(
            "relative",
            !expanded && "mt-0"
          )}>
            {!expanded && (
              <div className="absolute -top-12 left-0 right-0 h-12 bg-gradient-to-t from-[#0a0a0a] to-transparent pointer-events-none" />
            )}
            <button
              onClick={() => setExpanded(!expanded)}
              className="flex items-center gap-1 text-xs text-[#7a8a6e] hover:text-[#9aaa8e] mt-2 transition-colors"
            >
              {expanded ? (
                <>Show less <ChevronUp className="h-3 w-3" /></>
              ) : (
                <>Continue reading <ChevronDown className="h-3 w-3" /></>
              )}
            </button>
          </div>
        )}
      </div>

      {/* Action Bar - Below content */}
      <div className="flex items-center gap-2 mt-2 pt-2 border-t border-white/[0.04]">
        <button
          onClick={handleCopy}
          className={cn(
            "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[11px] font-medium transition-all border",
            copied
              ? "bg-[#2E3524]/20 text-[#8a9a7e] border-[#2E3524]/30"
              : "text-white/40 hover:text-white/70 hover:bg-white/[0.04] border-transparent hover:border-white/[0.06]"
          )}
          title="Copy to clipboard"
        >
          {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
          {copied ? 'Copied' : 'Copy'}
        </button>
        
        <div
          className="relative"
          onMouseLeave={() => setShowExportMenu(false)}
        >
          <button
            onMouseEnter={() => setShowExportMenu(true)}
            onClick={() => setShowExportMenu(!showExportMenu)}
            className="flex items-center gap-1.5 px-3 py-1.5 text-white/40 hover:text-white/70 hover:bg-white/[0.04] transition-all rounded-lg text-[11px] font-medium border border-transparent hover:border-white/[0.06]"
            title="Export document"
          >
            <FileDown className="h-3 w-3" />
            Export
            <ChevronDown className="h-2.5 w-2.5 ml-0.5" />
          </button>
          
          {showExportMenu && (
            <div 
              className="absolute left-0 bottom-full mb-1 bg-[#161616] border border-white/[0.10] rounded-xl shadow-2xl z-50 min-w-[180px] py-1 backdrop-blur-xl"
              onMouseLeave={() => setShowExportMenu(false)}
            >
              {[
                { format: 'pdf', icon: <FileText className="h-3.5 w-3.5 text-red-400" />, label: 'PDF' },
                { format: 'docx', icon: <FileText className="h-3.5 w-3.5 text-blue-400" />, label: 'Word' },
                { format: 'xlsx', icon: <FileSpreadsheet className="h-3.5 w-3.5 text-[#5c6652]" />, label: 'Excel' },
                { format: 'pptx', icon: <Presentation className="h-3.5 w-3.5 text-orange-400" />, label: 'PowerPoint' },
                { format: 'markdown', icon: <FileText className="h-3.5 w-3.5 text-white/40" />, label: 'Markdown' },
                { format: 'csv', icon: <FileSpreadsheet className="h-3.5 w-3.5 text-yellow-400" />, label: 'CSV' },
              ].map(({ format, icon, label }) => (
                <button
                  key={format}
                  onClick={() => handleExport(format)}
                  disabled={!!exporting}
                  className="w-full flex items-center gap-2.5 px-3 py-2 text-[11px] text-white/60 hover:text-white hover:bg-white/[0.05] transition-colors disabled:opacity-40 first:rounded-t-lg last:rounded-b-lg"
                >
                  {exporting === format ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : icon}
                  {label}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Sources */}
      {sources.length > 0 && (
        <SourcesSection sources={sources} ensureValidUrl={ensureValidUrl} />
      )}

      {/* Follow-up Questions */}
      {followUpQuestions.length > 0 && (
        <div className="mt-3 pt-3 border-t border-white/[0.04]">
          <p className="text-[10px] text-white/30 uppercase tracking-wider mb-2">Continue exploring</p>
          <div className="flex flex-col gap-1.5">
            {followUpQuestions.map((question, i) => (
              <button
                key={i}
                onClick={() => onFollowUpClick(question)}
                className="flex items-center gap-2 px-3 py-2 bg-white/[0.02] hover:bg-white/[0.05] border border-white/[0.05] hover:border-white/[0.10] rounded-xl text-xs text-white/50 hover:text-white/80 transition-all text-left group"
              >
                <Search className="h-3 w-3 text-white/20 group-hover:text-[#5c6652] transition-colors flex-shrink-0" />
                <span className="line-clamp-1">{question}</span>
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
  searchQuery: string;
  onSearchQueryChange: (query: string) => void;
}

function ChatSidebar({
  conversations,
  currentConversation,
  isOpen,
  onToggle,
  onSelectConversation,
  onDeleteConversation,
  onNewConversation,
  searchQuery,
  onSearchQueryChange,
}: ChatSidebarProps) {
  const { user } = useAuth();
  const setSearchQuery = onSearchQueryChange;
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [conversationToDelete, setConversationToDelete] = useState<string | null>(null);
  const [messageMatchIds, setMessageMatchIds] = useState<Set<string>>(new Set());
  const [messageSnippets, setMessageSnippets] = useState<Record<string, string>>({});
  const [isSearching, setIsSearching] = useState(false);
  const searchTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Debounced search across chat_messages content
  useEffect(() => {
    if (searchTimerRef.current) clearTimeout(searchTimerRef.current);

    if (!searchQuery.trim() || !user) {
      setMessageMatchIds(new Set());
      setMessageSnippets({});
      setIsSearching(false);
      return;
    }

    setIsSearching(true);
    searchTimerRef.current = setTimeout(async () => {
      try {
        const { data, error } = await supabase
          .from('chat_messages')
          .select('conversation_id, content, role')
          .eq('user_id', user.id)
          .ilike('content', `%${searchQuery.trim()}%`)
          .limit(200);

        if (!error && data) {
          const ids = new Set<string>();
          const snippets: Record<string, string> = {};
          data.forEach((msg: any) => {
            ids.add(msg.conversation_id);
            // Keep first matching snippet per conversation
            if (!snippets[msg.conversation_id]) {
              const idx = msg.content.toLowerCase().indexOf(searchQuery.toLowerCase());
              const start = Math.max(0, idx - 30);
              const end = Math.min(msg.content.length, idx + searchQuery.length + 30);
              snippets[msg.conversation_id] = (start > 0 ? '...' : '') + msg.content.slice(start, end) + (end < msg.content.length ? '...' : '');
            }
          });
          setMessageMatchIds(ids);
          setMessageSnippets(snippets);
        }
      } catch (e) {
        console.error('Search error:', e);
      } finally {
        setIsSearching(false);
      }
    }, 300);

    return () => {
      if (searchTimerRef.current) clearTimeout(searchTimerRef.current);
    };
  }, [searchQuery, user]);

  // Filter conversations by title match OR message content match
  const filteredConversations = conversations.filter((conv) => {
    if (!searchQuery.trim()) return true;
    const titleMatch = conv.title.toLowerCase().includes(searchQuery.toLowerCase());
    const messageMatch = messageMatchIds.has(conv.id);
    return titleMatch || messageMatch;
  });

  // Helper to highlight matching text
  const highlightMatch = (text: string, query: string) => {
    if (!query.trim()) return text;
    const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    const parts = text.split(regex);
    return parts.map((part, i) =>
      regex.test(part)
        ? <span key={i} className="bg-[#2E3524]/60 text-white rounded-sm px-0.5">{part}</span>
        : part
    );
  };

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
            className="w-10 h-10 flex items-center justify-center text-white/60 hover:text-white hover:bg-[#2E3524]/10 rounded-lg transition-colors"
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
            className="h-8 w-8 flex items-center justify-center text-white/50 hover:text-white hover:bg-[#2E3524]/10 rounded-lg transition-colors"
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
              "bg-gradient-to-r from-[#2E3524] to-[#2A3021] text-white hover:from-[#3a4530] hover:to-[#353d2a]",
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
                "focus:border-[#2E3524]/40 focus:outline-none focus:ring-1 focus:ring-[#2E3524]/20",
                "transition-all"
              )}
            />
            {isSearching && (
              <Loader2 className="absolute right-10 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-white/40 animate-spin" />
            )}
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
                      {searchQuery ? highlightMatch(conv.title, searchQuery) : conv.title}
                    </p>
                    {searchQuery && messageSnippets[conv.id] && (
                      <p className="text-[10px] text-white/50 mt-1 line-clamp-2 leading-relaxed">
                        {highlightMatch(messageSnippets[conv.id], searchQuery)}
                      </p>
                    )}
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
// Domain Tabs Component - Non-scrollable, centered with olive glow underline
// =============================================================================

function DomainTabs() {
  const { currentSector, setSector } = useSector();
  const router = useRouter();
  
  const handleDomainClick = (sectorId: Sector) => {
    setSector(sectorId);
    // Navigate to domain page for all tabs
    router.push(`/domain/${sectorId}`);
  };

  return (
    <div className="flex items-center justify-center gap-1">
      {SECTORS.map((sector) => (
        <button
          key={sector.id}
          onClick={() => handleDomainClick(sector.id)}
          className={cn(
            "domain-tab relative px-3 py-1.5 text-[13px] font-medium transition-all whitespace-nowrap",
            currentSector === sector.id
              ? "domain-tab-active text-white"
              : "text-white/50 hover:text-white/80"
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

  const fetchUserData = useCallback(async () => {
    if (!user) return;
    const { data } = await supabase
      .from("users")
      .select("name, profile_image, credits_balance, subscription_tier")
      .eq("id", user.id)
      .single();
    
    if (data) {
      setUserProfile({ name: data.name, profile_image: data.profile_image });
      setCreditBalance(data.credits_balance || 50);
      setPlan(data.subscription_tier || 'free');
    }
  }, [user]);

  useEffect(() => {
    fetchUserData();
    
    // Listen for profile updates from AccountOverview
    const handleProfileUpdate = () => {
      fetchUserData();
    };
    window.addEventListener('profile-updated', handleProfileUpdate);
    return () => window.removeEventListener('profile-updated', handleProfileUpdate);
  }, [fetchUserData]);

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
            'border border-white/[0.12] hover:border-[#2E3524]/50 hover:bg-[#2E3524]/10',
            'transition-all duration-200',
            isOpen && 'ring-2 ring-[#2E3524]/30'
          )}
        >
          {avatarUrl ? (
            <img src={avatarUrl} alt="Profile" className="w-full h-full object-cover" />
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-[#2E3524] to-[#2A3021] flex items-center justify-center">
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
                <span className="font-medium text-[#5c6652]">{creditBalance}</span> credits available
              </div>
            </div>
            
            {/* Menu Items */}
            <div className="py-1">
              <Link
                href="/settings"
                onClick={() => setIsOpen(false)}
                className="flex items-center gap-3 px-3 py-2.5 text-sm text-white/80 hover:bg-[#2E3524]/10 hover:text-white transition-colors"
              >
                <User className="h-4 w-4" />
                Profile
              </Link>
              <Link
                href="/billing"
                onClick={() => setIsOpen(false)}
                className="flex items-center gap-3 px-3 py-2.5 text-sm text-white/80 hover:bg-[#2E3524]/10 hover:text-white transition-colors"
              >
                <CreditCard className="h-4 w-4" />
                Billing & Credits
              </Link>
              <Link
                href="/preferences"
                onClick={() => setIsOpen(false)}
                className="flex items-center gap-3 px-3 py-2.5 text-sm text-white/80 hover:bg-[#2E3524]/10 hover:text-white transition-colors"
              >
                <Settings className="h-4 w-4" />
                Workspace Preferences
              </Link>
            </div>
            
            <div className="border-t border-white/10 py-1">
              <Link
                href="/contact"
                onClick={() => setIsOpen(false)}
                className="flex items-center gap-3 px-3 py-2.5 text-sm text-white/80 hover:bg-[#2E3524]/10 hover:text-white transition-colors"
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
          "bg-white/[0.05] text-white/50 hover:text-white hover:bg-[#2E3524]/10 hover:border-[#2E3524]/30",
          "border border-white/[0.08]",
          isOpen && "bg-[#2E3524]/10 text-white border-[#2E3524]/30",
          attachedFiles.length > 0 && "bg-[#2E3524]/20 border-[#2E3524]/40"
        )}
      >
        <Plus className="w-5 h-5" />
        {attachedFiles.length > 0 && (
          <span className="absolute -top-1 -right-1 w-4 h-4 bg-[#2E3524] text-white text-[10px] rounded-full flex items-center justify-center">
            {attachedFiles.length}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute bottom-full left-0 mb-2 w-48 bg-[#1A1A1A] border border-white/[0.08] rounded-lg shadow-xl overflow-hidden z-50">
          <button
            onClick={() => fileInputRef.current?.click()}
            className="w-full flex items-center gap-3 px-3 py-2.5 text-sm text-white/70 hover:text-white hover:bg-[#2E3524]/10 transition-colors"
          >
            <Paperclip className="w-4 h-4" />
            Upload File
          </button>
          <button
            onClick={() => {
              onOpenImageGenerator();
              setIsOpen(false);
            }}
            className="w-full flex items-center gap-3 px-3 py-2.5 text-sm text-white/70 hover:text-white hover:bg-[#2E3524]/10 transition-colors"
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
    if (type.includes('excel') || type.includes('sheet') || type.includes('csv')) return <FileText className="w-4 h-4 text-[#5c6652]" />;
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
      const response = await fetch(`${API_URL}/api/v1/generate-file`, {
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
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[#2E3524] to-[#2A3021] flex items-center justify-center">
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
                      ? "bg-[#2E3524]/20 border-[#2E3524] text-white"
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
              className="w-full h-24 px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder:text-white/30 focus:border-[#2E3524]/50 focus:outline-none resize-none"
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
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-[#2E3524] hover:bg-[#3a4530] text-white rounded-lg transition-colors"
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
                  ? "bg-gradient-to-r from-[#2E3524] to-[#2A3021] text-white hover:from-[#3a4530] hover:to-[#353d2a]"
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
  const [sidebarSearchQuery, setSidebarSearchQuery] = useState('');
  
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

  // Auto-restore last conversation on page load (skip if auto-execute pending or reset requested)
  useEffect(() => {
    if (conversations.length > 0 && !currentConversation && messages.length === 0) {
      try {
        // Don't restore old conversation if we're about to auto-execute a new prompt
        const pendingAutoExecute = sessionStorage.getItem('autoExecute') === 'true' && sessionStorage.getItem('domainPrompt');
        if (pendingAutoExecute) return;

        // If Global button was clicked, reset to landing state (no conversation)
        const shouldReset = sessionStorage.getItem('resetDashboard');
        if (shouldReset) {
          sessionStorage.removeItem('resetDashboard');
          startNewChat();
          return;
        }

        const lastConvId = localStorage.getItem('mcleuker_last_conversation_id');
        if (lastConvId) {
          const conv = conversations.find(c => c.id === lastConvId);
          if (conv) {
            handleSelectConversation(conv);
          }
        }
      } catch (e) {
        // localStorage not available
      }
    }
  }, [conversations]); // eslint-disable-line react-hooks/exhaustive-deps

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

  // Auto-execute prompt from landing page / domain pages
  const hasAutoExecuted = useRef(false);
  useEffect(() => {
    if (hasAutoExecuted.current) return;
    try {
      const pendingPrompt = sessionStorage.getItem('domainPrompt');
      const shouldAutoExecute = sessionStorage.getItem('autoExecute');
      const domainContext = sessionStorage.getItem('domainContext');

      if (pendingPrompt && shouldAutoExecute === 'true' && user) {
        // Clear immediately to prevent re-execution on re-render
        sessionStorage.removeItem('domainPrompt');
        sessionStorage.removeItem('autoExecute');
        sessionStorage.removeItem('domainContext');
        hasAutoExecuted.current = true;

        // Start a fresh new chat, then auto-send the prompt
        startNewChat();
        setTimeout(() => {
          handleSendMessage(pendingPrompt);
        }, 400);
      } else if (pendingPrompt && !shouldAutoExecute) {
        // Legacy: just pre-fill the input without auto-executing
        setInput(pendingPrompt);
        sessionStorage.removeItem('domainPrompt');
        sessionStorage.removeItem('domainContext');
      }
    } catch (e) {
      // sessionStorage not available
    }
  }, [user]); // eslint-disable-line react-hooks/exhaustive-deps

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
        try { localStorage.setItem('mcleuker_last_conversation_id', newConv.id); } catch (e) {}
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
    let currentDownloads: DownloadFile[] = [];
    let currentToolProgress: { message: string; tools: string[] }[] = [];
    let currentSearchSources: { title: string; url: string; source: string }[] = [];
    let currentTaskSteps: { step: string; title: string; status: 'active' | 'complete' | 'pending'; detail?: string }[] = [];

    try {
      // Map frontend mode names to backend mode names
      const modeMap: Record<string, string> = { 'quick': 'instant', 'deep': 'thinking' };
      const backendMode = modeMap[searchMode] || 'thinking';
      
      // Build messages array with optional sector context
      const chatMessages: Array<{role: string; content: string | Array<Record<string, unknown>>}> = [];
      if (currentSector !== 'all') {
        chatMessages.push({ role: 'system', content: `Focus on the ${currentSector} sector.` });
      }
      
      // Handle multimodal content (files)
      if (currentFiles.length > 0) {
        const contentParts: Array<Record<string, unknown>> = [
          { type: 'text', text: messageText }
        ];
        for (const f of currentFiles) {
          if (f.base64) {
            contentParts.push({ type: 'image_url', image_url: { url: `data:${f.type};base64,${f.base64}` } });
          } else if (f.url) {
            contentParts.push({ type: 'image_url', image_url: { url: f.url } });
          }
        }
        chatMessages.push({ role: 'user', content: contentParts });
      } else {
        chatMessages.push({ role: 'user', content: messageText });
      }
      
      const response = await fetch(`${API_URL}/api/v1/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: chatMessages,
          mode: backendMode,
          stream: true,
          enable_tools: true,
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
              } else if (eventType === 'download') {
                // Handle file download events from tool execution
                const downloadInfo: DownloadFile = {
                  filename: eventData.filename || 'file',
                  download_url: eventData.download_url || '',
                  file_id: eventData.file_id || '',
                  file_type: eventData.file_type || 'unknown',
                };
                currentDownloads.push(downloadInfo);
                setMessages(prev => prev.map(m =>
                  m.id === assistantId
                    ? { ...m, downloads: [...currentDownloads] }
                    : m
                ));
              } else if (eventType === 'tool_call') {
                // Handle tool execution progress from backend
                const toolMsg = eventData.message || 'Processing...';
                const toolNames = eventData.tools || [];
                currentToolProgress.push({ message: toolMsg, tools: toolNames });
                setMessages(prev => prev.map(m =>
                  m.id === assistantId
                    ? { ...m, toolStatus: toolMsg, toolProgress: [...currentToolProgress] }
                    : m
                ));
              } else if (eventType === 'search_sources') {
                // Handle search sources from backend real-time search
                const sources = Array.isArray(eventData.sources) ? eventData.sources : (Array.isArray(eventData) ? eventData : []);
                currentSearchSources = [...currentSearchSources, ...sources];
                // Also add to currentSources for the existing source display
                for (const src of sources) {
                  if (src.title && src.url && !currentSources.some(s => s.url === src.url)) {
                    currentSources.push({
                      title: src.title,
                      url: src.url,
                      snippet: src.source || '',
                    });
                  }
                }
                setMessages(prev => prev.map(m =>
                  m.id === assistantId
                    ? { ...m, sources: [...currentSources], searchSources: [...currentSearchSources] }
                    : m
                ));
              } else if (eventType === 'task_progress') {
                // Manus AI-style task progress tracking
                const stepData = {
                  step: eventData.step || 'unknown',
                  title: eventData.title || 'Processing...',
                  status: eventData.status || 'active' as const,
                  detail: eventData.detail,
                };
                // Update existing step or add new one
                const existingIdx = currentTaskSteps.findIndex(s => s.step === stepData.step);
                if (existingIdx >= 0) {
                  currentTaskSteps[existingIdx] = stepData;
                } else {
                  // Mark all previous active steps as complete
                  currentTaskSteps = currentTaskSteps.map(s => 
                    s.status === 'active' ? { ...s, status: 'complete' as const } : s
                  );
                  currentTaskSteps.push(stepData);
                }
                setMessages(prev => prev.map(m =>
                  m.id === assistantId
                    ? { ...m, taskSteps: [...currentTaskSteps] }
                    : m
                ));
              } else if (eventType === 'reasoning') {
                // Handle reasoning_content from thinking mode
                const reasoningChunk = eventData.chunk || eventData || '';
                if (typeof reasoningChunk === 'string' && reasoningChunk) {
                  // Create or update a reasoning layer for thinking content
                  if (currentLayers.length === 0) {
                    currentLayers.push({
                      id: 'thinking-1',
                      layer_num: 1,
                      type: 'analysis',
                      title: 'Thinking',
                      content: reasoningChunk,
                      sub_steps: [],
                      status: 'active',
                      expanded: true,
                    });
                  } else {
                    currentLayers[currentLayers.length - 1].content += reasoningChunk;
                  }
                  setMessages(prev => prev.map(m =>
                    m.id === assistantId
                      ? { ...m, reasoning_layers: [...currentLayers] }
                      : m
                  ));
                }
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
                currentTaskSteps = currentTaskSteps.map(s => ({ ...s, status: 'complete' as const }));

                // Merge downloads from complete event and from stream
                const completeDownloads = eventData.downloads || [];
                const allDownloads = [...currentDownloads, ...completeDownloads.filter(
                  (d: DownloadFile) => !currentDownloads.some(cd => cd.file_id === d.file_id)
                )];

                // Filter sources to only include those with valid URLs
                const finalSources = (eventData.sources || currentSources).filter(
                  (s: Source) => s.url && s.url.startsWith('http')
                );

                setMessages(prev => prev.map(m =>
                  m.id === assistantId
                    ? {
                        ...m,
                        content: finalContent,
                        reasoning_layers: currentLayers,
                        sources: finalSources,
                        follow_up_questions: followUpQuestions,
                        downloads: allDownloads.length > 0 ? allDownloads : undefined,
                        searchSources: currentSearchSources.length > 0 ? currentSearchSources : undefined,
                        toolStatus: undefined,
                        toolProgress: currentToolProgress.length > 0 ? currentToolProgress : undefined,
                        taskSteps: currentTaskSteps.length > 0 ? currentTaskSteps : undefined,
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
                      downloads: allDownloads.length > 0 ? allDownloads : undefined,
                    });
                    
                    await supabase.from('chat_messages').insert({
                      conversation_id: requestConversationId,
                      user_id: user.id,
                      role: 'assistant',
                      content: finalContent,
                      model_used: 'kimi-k2.5',
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
      
      // Restore the user's input so they can retry
      setInput(messageText);
      
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      setMessages(prev => prev.map(m =>
        m.id === assistantId
          ? {
              ...m,
              content: `Something went wrong: ${errorMessage}. Your message has been restored — you can try again.`,
              isStreaming: false,
              taskSteps: currentTaskSteps.length > 0 
                ? [...currentTaskSteps.map(s => ({...s, status: 'complete' as const})), { step: 'error', title: 'Error occurred', status: 'complete' as const, detail: errorMessage }]
                : undefined,
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
    try { localStorage.removeItem('mcleuker_last_conversation_id'); } catch (e) {}
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
    try { localStorage.setItem('mcleuker_last_conversation_id', conv.id); } catch (e) {}
    // Load messages for this conversation
    const { data, error } = await supabase
      .from("chat_messages")
      .select("*")
      .eq("conversation_id", conv.id)
      .order("created_at", { ascending: true });
    
    if (!error && data) {
      const loadedMessages: Message[] = data.map((msg: any) => {
        // Parse metadata if it exists (contains sources, reasoning_layers, follow_up_questions)
        let metadata: any = {};
        if (msg.metadata) {
          try {
            metadata = typeof msg.metadata === 'string' 
              ? JSON.parse(msg.metadata) 
              : msg.metadata;
          } catch (e) {
            console.error('Error parsing message metadata:', e);
          }
        }
        
        // Parse reasoning layers with proper structure
        const reasoningLayers: ReasoningLayer[] = (metadata.reasoning_layers || []).map((layer: any, index: number) => ({
          id: layer.id || `layer-${index}`,
          layer_num: layer.layer_num || index + 1,
          type: layer.type || 'analysis',
          title: layer.title || `Layer ${index + 1}`,
          content: layer.content || '',
          sub_steps: layer.sub_steps || [],
          status: 'complete' as const,
          expanded: false,
        }));
        
        // Parse downloads from metadata
        const downloads: DownloadFile[] = (metadata.downloads || []).map((dl: any) => ({
          filename: dl.filename || '',
          download_url: dl.download_url || '',
          file_id: dl.file_id || '',
          file_type: dl.file_type || '',
        }));

        return {
          id: msg.id,
          role: msg.role as 'user' | 'assistant',
          content: msg.content,
          reasoning_layers: reasoningLayers,
          sources: metadata.sources || msg.sources || [],
          follow_up_questions: metadata.follow_up_questions || msg.follow_up_questions || [],
          timestamp: new Date(msg.created_at),
          isStreaming: false,
          is_favorite: msg.is_favorite,
          downloads: downloads.length > 0 ? downloads : undefined,
        };
      });
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
        {/* Left: McLeuker.ai Logo */}
        <div className="flex items-center gap-4 w-48">
          <Link href="/" className="flex items-center">
            <span className="font-editorial text-xl lg:text-[22px] text-white tracking-[0.02em]">
              McLeuker<span className="text-white/30">.ai</span>
            </span>
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
        searchQuery={sidebarSearchQuery}
        onSearchQueryChange={setSidebarSearchQuery}
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
                {/* Title - Elegant, centered */}
                <h1 className="text-2xl md:text-3xl lg:text-4xl font-editorial text-white/80 mb-6 text-center tracking-tight">
                  Where is my mind?
                </h1>
                
                {/* Search Bar - Directly under title */}
                <div className="w-full max-w-xl mb-6">
                  <div className="flex items-center gap-2 p-3 rounded-2xl bg-[#141414] border border-white/[0.08] hover:border-[#2E3524]/30 transition-all">
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
                          ? "bg-[#2E3524] text-white hover:bg-[#3a4530]"
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
                  
                  {/* Instant/Thinking Mode Toggle - Under search bar */}
                  <div className="flex justify-center mt-3">
                    <div className="flex items-center gap-0.5 p-1 bg-white/[0.03] rounded-xl border border-white/[0.06]">
                      <button
                        onClick={() => setSearchMode('quick')}
                        className={cn(
                          "flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-medium transition-all",
                          searchMode === 'quick'
                            ? "bg-[#2E3524] text-white shadow-lg shadow-[#2E3524]/20"
                            : "text-white/40 hover:text-white/60 hover:bg-white/[0.03]"
                        )}
                      >
                        <Zap className="h-3.5 w-3.5" />
                        <div className="text-left">
                          <span className="block">Instant</span>
                          <span className="block text-[9px] opacity-60 font-normal">Search + fast answer</span>
                        </div>
                      </button>
                      <button
                        onClick={() => setSearchMode('deep')}
                        className={cn(
                          "flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-medium transition-all",
                          searchMode === 'deep'
                            ? "bg-[#2E3524] text-white shadow-lg shadow-[#2E3524]/20"
                            : "text-white/40 hover:text-white/60 hover:bg-white/[0.03]"
                        )}
                      >
                        <Brain className="h-3.5 w-3.5" />
                        <div className="text-left">
                          <span className="block">Thinking</span>
                          <span className="block text-[9px] opacity-60 font-normal">Deep reasoning + search</span>
                        </div>
                      </button>
                    </div>
                  </div>
                  <p className="text-white/20 text-[11px] text-center mt-2">McLeukerAI can be wrong. Please verify important details.</p>
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
                        : "" // AI messages have no bubble - plain text
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
                          <p className="text-white text-sm leading-relaxed">{sidebarSearchQuery ? (() => {
                            const escaped = sidebarSearchQuery.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
                            const regex = new RegExp(`(${escaped})`, 'gi');
                            const parts = message.content.split(regex);
                            return parts.map((part: string, idx: number) =>
                              regex.test(part)
                                ? <mark key={idx} className="bg-[#2E3524]/60 text-white rounded-sm px-0.5">{part}</mark>
                                : part
                            );
                          })() : message.content}</p>
                        </div>
                      )}
                      
                      {/* Assistant message */}
                      {message.role === 'assistant' && (
                        <div className="space-y-0">
                          {/* ===== TASK PROGRESS TIMELINE (Collapsible) ===== */}
                          {(message.taskSteps && message.taskSteps.length > 0) && (() => {
                            const completedCount = message.taskSteps.filter(s => s.status === 'complete').length;
                            const totalCount = message.taskSteps.length;
                            const lastActiveStep = [...message.taskSteps].reverse().find(s => s.status === 'active');
                            const isExpanded = message.isStreaming || message._taskExpanded !== false;
                            const toggleExpanded = () => {
                              setMessages(prev => prev.map(m => m.id === message.id ? { ...m, _taskExpanded: !isExpanded } : m));
                            };
                            
                            const getStepIcon = (stepName: string, status: string) => {
                              const iconClass = status === 'active' ? 'text-[#8a9a7e]' : status === 'complete' ? 'text-white/40' : 'text-white/15';
                              if (stepName.includes('understand') || stepName.includes('analyze') || stepName.includes('pars')) return <Brain className={`h-3.5 w-3.5 ${iconClass}`} />;
                              if (stepName.includes('plan') || stepName.includes('break') || stepName.includes('identif')) return <FileText className={`h-3.5 w-3.5 ${iconClass}`} />;
                              if (stepName.includes('search') || stepName.includes('collect') || stepName.includes('found') || stepName.includes('query')) return <Globe className={`h-3.5 w-3.5 ${iconClass}`} />;
                              if (stepName.includes('verify') || stepName.includes('cross') || stepName.includes('validat')) return <CheckCircle2 className={`h-3.5 w-3.5 ${iconClass}`} />;
                              if (stepName.includes('reason') || stepName.includes('synthe') || stepName.includes('think')) return <Sparkles className={`h-3.5 w-3.5 ${iconClass}`} />;
                              if (stepName.includes('write') || stepName.includes('compos') || stepName.includes('generat')) return <MessageSquare className={`h-3.5 w-3.5 ${iconClass}`} />;
                              if (stepName.includes('structure') || stepName.includes('format') || stepName.includes('organiz')) return <FileSpreadsheet className={`h-3.5 w-3.5 ${iconClass}`} />;
                              if (stepName.includes('review') || stepName.includes('conclude') || stepName.includes('final') || stepName.includes('complet')) return <Star className={`h-3.5 w-3.5 ${iconClass}`} />;
                              if (stepName.includes('retry') || stepName.includes('fallback')) return <Zap className={`h-3.5 w-3.5 ${iconClass}`} />;
                              if (stepName.includes('error') || stepName.includes('fail')) return <X className={`h-3.5 w-3.5 ${iconClass}`} />;
                              return <Circle className={`h-3.5 w-3.5 ${iconClass}`} />;
                            };
                            
                            return (
                              <div className="mb-3">
                                {/* Clickable Header - Manus/ChatGPT thinking style */}
                                <button
                                  onClick={toggleExpanded}
                                  className="flex items-center gap-2 w-full text-left group"
                                >
                                  {message.isStreaming ? (
                                    <Loader2 className="h-4 w-4 text-[#8a9a7e] animate-spin flex-shrink-0" />
                                  ) : (
                                    <CheckCircle2 className="h-4 w-4 text-[#5c6652] flex-shrink-0" />
                                  )}
                                  <span className="text-[13px] text-white/50 group-hover:text-white/70 transition-colors">
                                    {message.isStreaming
                                      ? (lastActiveStep?.detail || lastActiveStep?.title || 'Thinking...')
                                      : `Completed ${completedCount} steps`
                                    }
                                  </span>
                                  <ChevronDown className={cn(
                                    "h-3 w-3 text-white/20 transition-transform ml-auto",
                                    isExpanded && "rotate-180"
                                  )} />
                                </button>
                                
                                {/* Expandable Steps - line by line like Manus */}
                                {isExpanded && (
                                  <div className="mt-2 ml-2 pl-4 border-l border-white/[0.06]">
                                    {message.taskSteps.map((step, stepIdx) => (
                                      <div key={`${step.step}-${stepIdx}`} className="flex items-start gap-2.5 py-1">
                                        {step.status === 'active' && message.isStreaming ? (
                                          <Loader2 className="h-3.5 w-3.5 text-[#8a9a7e] animate-spin flex-shrink-0 mt-[1px]" />
                                        ) : step.status === 'complete' ? (
                                          getStepIcon(step.step, step.status)
                                        ) : (
                                          <Circle className="h-3.5 w-3.5 text-white/10 flex-shrink-0 mt-[1px]" />
                                        )}
                                        <div className="flex-1 min-w-0">
                                          <p className={cn(
                                            "text-[12px] leading-snug",
                                            step.status === 'active' ? "text-white/80" : step.status === 'complete' ? "text-white/40" : "text-white/20"
                                          )}>
                                            {step.title}
                                          </p>
                                          {step.detail && step.status === 'active' && (
                                            <p className="text-[10px] text-white/30 mt-0.5 leading-snug">
                                              {step.detail}
                                            </p>
                                          )}
                                        </div>
                                        {step.status === 'active' && message.isStreaming && (
                                          <span className="flex gap-0.5 mt-1">
                                            <span className="w-1 h-1 rounded-full bg-[#5c6652] animate-bounce" style={{animationDelay: '0ms'}} />
                                            <span className="w-1 h-1 rounded-full bg-[#5c6652] animate-bounce" style={{animationDelay: '150ms'}} />
                                            <span className="w-1 h-1 rounded-full bg-[#5c6652] animate-bounce" style={{animationDelay: '300ms'}} />
                                          </span>
                                        )}
                                      </div>
                                    ))}
                                  </div>
                                )}
                              </div>
                            );
                          })()}

                          {/* ===== REASONING LAYERS (Thinking mode) ===== */}
                          {message.reasoning_layers.length > 0 && (
                            <div className="mb-4">
                              <button
                                onClick={() => {
                                  setMessages(prev => prev.map(m => {
                                    if (m.id !== message.id) return m;
                                    const allExpanded = m.reasoning_layers.every(l => l.expanded);
                                    return { ...m, reasoning_layers: m.reasoning_layers.map(l => ({ ...l, expanded: !allExpanded })) };
                                  }));
                                }}
                                className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/[0.03] hover:bg-white/[0.06] border border-white/[0.06] transition-all w-full text-left group"
                              >
                                <Brain className="h-3.5 w-3.5 text-[#5c6652]" />
                                <span className="text-xs text-white/50 font-medium flex-1">
                                  {message.isStreaming ? 'Thinking...' : `Thought for ${Math.max(1, Math.round(message.reasoning_layers.reduce((a, l) => a + l.content.length, 0) / 200))}s`}
                                </span>
                                <ChevronDown className={cn(
                                  "h-3 w-3 text-white/30 transition-transform",
                                  message.reasoning_layers.some(l => l.expanded) && "rotate-180"
                                )} />
                              </button>
                              {message.reasoning_layers.some(l => l.expanded) && (
                                <div className="mt-2 px-3 py-2 rounded-lg bg-white/[0.02] border border-white/[0.04] max-h-[200px] overflow-y-auto">
                                  <p className="text-xs text-white/40 leading-relaxed whitespace-pre-wrap">
                                    {message.reasoning_layers.map(l => l.content).join('\n')}
                                  </p>
                                </div>
                              )}
                            </div>
                          )}

                          {/* ===== STREAMING INDICATOR ===== */}
                          {message.isStreaming && !message.content && !message.taskSteps?.length && !message.reasoning_layers.length && (
                            <div className="flex items-center gap-2 text-white/50 py-2">
                              <Loader2 className="h-4 w-4 animate-spin" />
                              <span className="text-sm">Connecting...</span>
                            </div>
                          )}
                          
                          {/* Streaming content indicator when task steps are showing but content is being generated */}
                          {message.isStreaming && message.content && (
                            <div className="flex items-center gap-1.5 mb-2">
                              <div className="w-1.5 h-1.5 rounded-full bg-[#5c6652] animate-pulse" />
                              <span className="text-[10px] text-white/30">Generating response...</span>
                            </div>
                          )}
                          
                          {/* ===== DOWNLOAD FILES (shown above content for file generation) ===== */}
                          {message.downloads && message.downloads.length > 0 && (
                            <div className="mt-4 space-y-2">
                              <p className="text-[10px] text-white/30 uppercase tracking-wider mb-2">Generated Files</p>
                              {message.downloads.map((dl, dlIdx) => {
                                const getFileIcon = (ft: string) => {
                                  if (ft.includes('excel') || ft.includes('xlsx') || ft.includes('csv')) return <FileSpreadsheet className="h-5 w-5 text-[#5c6652]" />;
                                  if (ft.includes('ppt') || ft.includes('presentation')) return <Presentation className="h-5 w-5 text-orange-400" />;
                                  if (ft.includes('pdf')) return <FileText className="h-5 w-5 text-red-400" />;
                                  return <File className="h-5 w-5 text-blue-400" />;
                                };
                                const getFileColor = (ft: string) => {
                                  if (ft.includes('excel') || ft.includes('xlsx')) return 'border-[#5c6652]/30 hover:border-[#5c6652]/60';
                                  if (ft.includes('ppt') || ft.includes('presentation')) return 'border-orange-400/30 hover:border-orange-400/60';
                                  if (ft.includes('pdf')) return 'border-red-400/30 hover:border-red-400/60';
                                  return 'border-blue-400/30 hover:border-blue-400/60';
                                };
                                return (
                                  <a
                                    key={dlIdx}
                                    href={`${API_URL}${dl.download_url}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className={cn(
                                      "flex items-center gap-3 px-4 py-3 bg-white/[0.03] hover:bg-white/[0.06] border rounded-xl transition-all group cursor-pointer",
                                      getFileColor(dl.file_type)
                                    )}
                                  >
                                    <div className="flex-shrink-0 p-2.5 bg-white/[0.04] rounded-lg">
                                      {getFileIcon(dl.file_type)}
                                    </div>
                                    <div className="flex-1 min-w-0">
                                      <p className="text-sm font-medium text-white/90 truncate">{dl.filename}</p>
                                      <p className="text-[10px] text-white/30 uppercase tracking-wider mt-0.5">{dl.file_type} document</p>
                                    </div>
                                    <div className="flex-shrink-0 p-2 rounded-lg bg-white/[0.04] group-hover:bg-white/[0.08] transition-colors">
                                      <Download className="h-4 w-4 text-white/40 group-hover:text-white/80 transition-colors" />
                                    </div>
                                  </a>
                                );
                              })}
                            </div>
                          )}
                          
                          {/* ===== MAIN CONTENT (conclusion/analysis) ===== */}
                          {message.content && (
                            <MessageContent
                              content={message.content}
                              sources={message.sources}
                              followUpQuestions={message.follow_up_questions}
                              onFollowUpClick={handleSendMessage}
                              searchQuery={sidebarSearchQuery}
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
              
              {/* Instant/Thinking Mode Toggle - Centered */}
              <div className="flex justify-center mb-3">
                <div className="flex items-center gap-0.5 p-0.5 bg-white/[0.03] rounded-lg border border-white/[0.06]">
                  <button
                    onClick={() => setSearchMode('quick')}
                    className={cn(
                      "flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all",
                      searchMode === 'quick'
                        ? "bg-[#2E3524] text-white shadow-sm"
                        : "text-white/40 hover:text-white/60"
                    )}
                  >
                    <Zap className="h-3 w-3" />
                    Instant
                  </button>
                  <button
                    onClick={() => setSearchMode('deep')}
                    className={cn(
                      "flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all",
                      searchMode === 'deep'
                        ? "bg-[#2E3524] text-white shadow-sm"
                        : "text-white/40 hover:text-white/60"
                    )}
                  >
                    <Brain className="h-3 w-3" />
                    Thinking
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
                      ? "bg-[#2E3524] text-white hover:bg-[#3a4530]"
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
              <div className="flex items-center justify-center gap-4 mt-1.5">
                <p className="text-[10px] text-white/30">
                  Press Enter to send • Shift + Enter for new line
                </p>
              </div>
              <p className="text-white/20 text-[11px] text-center mt-1">McLeukerAI can be wrong. Please verify important details.</p>
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
