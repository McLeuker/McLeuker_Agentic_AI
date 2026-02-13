'use client';

import React, { useState, useRef, useCallback, useEffect } from 'react';
import { api, handleChatResponse, DownloadableFile, ChatMode, ChatMessage, SearchSource, detectFileRequest, formatTokenCount, formatLatency } from '@/lib/api';
import { ModeSelector } from './ModeSelector';
import { MessageList } from './MessageList';
import { InputArea } from './InputArea';
import { ToolIndicator } from './ToolIndicator';
import { DownloadPanel } from './DownloadPanel';
import { SearchSourcesPanel } from './SearchSourcesPanel';

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  reasoning?: string;
  toolStatus?: string;
  isStreaming?: boolean;
  downloads?: DownloadableFile[];
  searchSources?: SearchSource[];
  followUpQuestions?: string[];
  conclusion?: string;
  metadata?: {
    tokens?: { prompt_tokens: number; completion_tokens: number; total_tokens: number };
    latency_ms?: number;
    tool_calls?: number;
  };
  timestamp: Date;
}

interface ChatInterfaceProps {
  conversationId?: string;
  onConversationUpdate?: (id: string, title: string) => void;
}

// ============================================================================
// LOCAL STORAGE PERSISTENCE
// ============================================================================

const STORAGE_KEY = 'mcleuker_chat_messages';
const CONVERSATION_ID_KEY = 'mcleuker_conversation_id';

function saveMessagesToStorage(messages: Message[]) {
  try {
    // Only save the last 100 messages to avoid storage limits
    const toSave = messages.slice(-100).map(m => ({
      ...m,
      timestamp: m.timestamp.toISOString(),
    }));
    localStorage.setItem(STORAGE_KEY, JSON.stringify(toSave));
  } catch (e) {
    console.warn('Failed to save messages to localStorage:', e);
  }
}

function loadMessagesFromStorage(): Message[] {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return [];
    const parsed = JSON.parse(stored);
    return parsed.map((m: any) => ({
      ...m,
      timestamp: new Date(m.timestamp),
      isStreaming: false, // Never restore as streaming
    }));
  } catch (e) {
    console.warn('Failed to load messages from localStorage:', e);
    return [];
  }
}

function saveConversationId(id: string) {
  try {
    localStorage.setItem(CONVERSATION_ID_KEY, id);
  } catch (e) { /* ignore */ }
}

function loadConversationId(): string | null {
  try {
    return localStorage.getItem(CONVERSATION_ID_KEY);
  } catch (e) {
    return null;
  }
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function ChatInterface({ conversationId: propConversationId, onConversationUpdate }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [mode, setMode] = useState<ChatMode>('research'); // Default to research (recommended)
  const [isLoading, setIsLoading] = useState(false);
  const [currentStatus, setCurrentStatus] = useState<string | null>(null);
  const [statusStep, setStatusStep] = useState<{ step: number; total: number } | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(propConversationId || null);
  const [activeTools, setActiveTools] = useState<{ search: boolean; fileGen: boolean; code: boolean }>({ 
    search: false, 
    fileGen: false, 
    code: false 
  });
  const [showDownloads, setShowDownloads] = useState(false);
  const [showSources, setShowSources] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const generateId = () => Math.random().toString(36).substring(2, 9);

  // Load messages from localStorage on mount
  useEffect(() => {
    const stored = loadMessagesFromStorage();
    if (stored.length > 0) {
      setMessages(stored);
    }
    const storedConvId = loadConversationId();
    if (storedConvId && !propConversationId) {
      setConversationId(storedConvId);
    }
  }, [propConversationId]);

  // Save messages to localStorage whenever they change
  useEffect(() => {
    if (messages.length > 0) {
      saveMessagesToStorage(messages);
    }
  }, [messages]);

  // Auto-scroll when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages, currentStatus]);

  // ============================================================================
  // UNIFIED STREAMING HANDLER - All modes use streaming now
  // ============================================================================

  const handleSend = useCallback(async () => {
    if (!input.trim() || isLoading) return;

    // Cancel any ongoing request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();

    const userMessage: Message = {
      id: generateId(),
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    const assistantMessage: Message = {
      id: generateId(),
      role: 'assistant',
      content: '',
      isStreaming: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage, assistantMessage]);
    setInput('');
    setIsLoading(true);
    setCurrentStatus('Initializing...');
    setStatusStep(null);

    // Detect what tools might be needed
    const fileRequest = detectFileRequest(input);
    const needsSearch = mode === 'agent' || mode === 'research' || mode === 'swarm' ||
      /\b(what's happening|latest|recent|news|today|current|now|202[4-6]|market|trend|brand|company|price|stock)\b/i.test(input);
    
    setActiveTools({
      search: needsSearch,
      fileGen: fileRequest.type !== null,
      code: mode === 'code' || /\b(code|script|function|program)\b/i.test(input)
    });

    try {
      // ALL modes now use streaming for consistent UX
      let fullContent = '';
      let fullReasoning = '';
      let streamDownloads: DownloadableFile[] = [];
      let streamSources: SearchSource[] = [];
      let followUps: string[] = [];
      let conclusionText = '';
      let toolCallCount = 0;
      const enableTools = mode === 'agent' || mode === 'code';
      
      // Build message history for context
      const chatHistory = [...messages, userMessage].map(m => ({ 
        role: m.role, 
        content: m.content 
      }));
      
      for await (const event of api.chatStream(chatHistory, { mode, enable_tools: enableTools })) {
        // event = { type: string, data: any, timestamp: string }
        const eventType = event.type;
        const eventData = event.data;

        switch (eventType) {
          case 'start':
            // Capture conversation_id from backend
            if (eventData?.conversation_id) {
              setConversationId(eventData.conversation_id);
              saveConversationId(eventData.conversation_id);
            }
            setCurrentStatus('Connected. Processing...');
            break;

          case 'status':
            // Progress status events from backend
            const statusMsg = eventData?.message || 'Processing...';
            setCurrentStatus(statusMsg);
            if (eventData?.step && eventData?.total_steps) {
              setStatusStep({ step: eventData.step, total: eventData.total_steps });
            }
            // Update tool status on the message
            setMessages(prev => prev.map(msg => 
              msg.id === assistantMessage.id
                ? { ...msg, toolStatus: statusMsg }
                : msg
            ));
            break;

          case 'content':
            // CRITICAL FIX: eventData is { chunk: "text" }, not a string
            const textChunk = typeof eventData === 'string' ? eventData : (eventData?.chunk || eventData?.text || '');
            fullContent += textChunk;
            setCurrentStatus(null); // Clear status when content starts flowing
            setStatusStep(null);
            setMessages(prev => prev.map(msg => 
              msg.id === assistantMessage.id
                ? { ...msg, content: fullContent, toolStatus: undefined }
                : msg
            ));
            break;

          case 'reasoning':
            // CRITICAL FIX: same as content - extract the chunk
            const reasonChunk = typeof eventData === 'string' ? eventData : (eventData?.chunk || eventData?.text || '');
            fullReasoning += reasonChunk;
            setMessages(prev => prev.map(msg => 
              msg.id === assistantMessage.id
                ? { ...msg, reasoning: fullReasoning }
                : msg
            ));
            break;

          case 'tool_call':
            toolCallCount++;
            const toolMsg = eventData?.message || 'Executing tool...';
            setCurrentStatus(toolMsg);
            setMessages(prev => prev.map(msg => 
              msg.id === assistantMessage.id
                ? { ...msg, toolStatus: toolMsg }
                : msg
            ));
            if (toolMsg.toLowerCase().includes('search') || toolMsg.toLowerCase().includes('source')) {
              setActiveTools(prev => ({ ...prev, search: true }));
            }
            if (toolMsg.toLowerCase().includes('generat') || toolMsg.toLowerCase().includes('build') || toolMsg.toLowerCase().includes('file')) {
              setActiveTools(prev => ({ ...prev, fileGen: true }));
            }
            break;

          case 'search_sources':
            // Sources found during search
            const sources = eventData?.sources || [];
            streamSources = [...streamSources, ...sources];
            setMessages(prev => prev.map(msg => 
              msg.id === assistantMessage.id
                ? { ...msg, searchSources: streamSources }
                : msg
            ));
            setShowSources(true);
            break;

          case 'download':
            // File generated and ready for download
            const dl: DownloadableFile = {
              filename: eventData?.filename || 'file',
              download_url: eventData?.download_url || '',
              file_id: eventData?.file_id || '',
              file_type: eventData?.file_type || 'unknown',
            };
            streamDownloads.push(dl);
            setMessages(prev => prev.map(msg => 
              msg.id === assistantMessage.id
                ? { ...msg, downloads: [...streamDownloads] }
                : msg
            ));
            setShowDownloads(true);
            setCurrentStatus(`Generated ${dl.filename}`);
            break;

          case 'file_error':
            console.error('File generation error:', eventData);
            setCurrentStatus(`File error: ${eventData?.error || 'Unknown error'}`);
            break;

          case 'conclusion':
            // Manus-style conclusion
            conclusionText = eventData?.content || '';
            if (conclusionText) {
              fullContent += '\n\n---\n\n' + conclusionText;
              setMessages(prev => prev.map(msg => 
                msg.id === assistantMessage.id
                  ? { ...msg, content: fullContent, conclusion: conclusionText }
                  : msg
              ));
            }
            break;

          case 'follow_up':
            // Follow-up question suggestions
            followUps = eventData?.questions || [];
            setMessages(prev => prev.map(msg => 
              msg.id === assistantMessage.id
                ? { ...msg, followUpQuestions: followUps }
                : msg
            ));
            break;

          case 'complete':
            // Final event - use as fallback if content was missed
            if (eventData?.content && !fullContent) {
              fullContent = eventData.content;
            }
            if (eventData?.reasoning && !fullReasoning) {
              fullReasoning = eventData.reasoning;
            }
            if (eventData?.downloads?.length) {
              const newDls = eventData.downloads.filter(
                (d: DownloadableFile) => !streamDownloads.some(sd => sd.file_id === d.file_id)
              );
              streamDownloads = [...streamDownloads, ...newDls];
            }
            if (eventData?.follow_up_questions?.length && followUps.length === 0) {
              followUps = eventData.follow_up_questions;
            }
            break;

          case 'error':
            const errorMsg = eventData?.message || 'An error occurred';
            fullContent += `\n\n**Error:** ${errorMsg}`;
            setCurrentStatus(null);
            break;

          default:
            console.log('Unhandled SSE event type:', eventType, eventData);
            break;
        }
      }

      // Final message update after stream ends
      setMessages(prev => prev.map(msg => 
        msg.id === assistantMessage.id
          ? {
              ...msg,
              content: fullContent || 'No response received. Please try again.',
              reasoning: fullReasoning || undefined,
              downloads: streamDownloads.length > 0 ? streamDownloads : undefined,
              searchSources: streamSources.length > 0 ? streamSources : undefined,
              followUpQuestions: followUps.length > 0 ? followUps : undefined,
              conclusion: conclusionText || undefined,
              toolStatus: undefined,
              isStreaming: false,
              metadata: {
                tool_calls: toolCallCount > 0 ? toolCallCount : undefined
              }
            }
          : msg
      ));

    } catch (error) {
      if ((error as Error).name !== 'AbortError') {
        console.error('Chat error:', error);
        setMessages(prev => prev.map(msg => 
          msg.id === assistantMessage.id
            ? { ...msg, content: 'Sorry, an error occurred. Please try again.', isStreaming: false }
            : msg
        ));
      }
    } finally {
      setIsLoading(false);
      setCurrentStatus(null);
      setStatusStep(null);
      setActiveTools({ search: false, fileGen: false, code: false });
      abortControllerRef.current = null;
    }
  }, [input, messages, mode, isLoading]);

  // ============================================================================
  // FILE UPLOAD HANDLERS
  // ============================================================================

  const handleFileUpload = async (file: File) => {
    const userMessage: Message = {
      id: generateId(),
      role: 'user',
      content: `[File: ${file.name}]`,
      timestamp: new Date()
    };

    const assistantMessage: Message = {
      id: generateId(),
      role: 'assistant',
      content: '',
      isStreaming: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage, assistantMessage]);
    setIsLoading(true);
    setCurrentStatus('Uploading and analyzing file...');

    try {
      const result = await api.multimodal('Analyze this file in detail', file, mode);
      
      setMessages(prev => prev.map(msg => 
        msg.id === assistantMessage.id
          ? {
              ...msg,
              content: result.response?.answer || result.response?.content || 'Analysis complete',
              isStreaming: false
            }
          : msg
      ));
    } catch (error) {
      setMessages(prev => prev.map(msg => 
        msg.id === assistantMessage.id
          ? { ...msg, content: 'Error analyzing file. Please try again.', isStreaming: false }
          : msg
      ));
    } finally {
      setIsLoading(false);
      setCurrentStatus(null);
    }
  };

  const handleVisionToCode = async (file: File) => {
    const userMessage: Message = {
      id: generateId(),
      role: 'user',
      content: `[UI Mockup: ${file.name}] - Convert to code`,
      timestamp: new Date()
    };

    const assistantMessage: Message = {
      id: generateId(),
      role: 'assistant',
      content: 'Analyzing UI and generating code...',
      isStreaming: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage, assistantMessage]);
    setIsLoading(true);
    setCurrentStatus('Analyzing UI mockup...');

    try {
      const base64 = await fileToBase64(file);
      const result = await api.visionToCode(base64, 'Convert this UI to production code', 'react');
      
      if (result.success) {
        const codeBlocks = result.response.code_blocks;
        const codeContent = codeBlocks.map((b: any) => `\`\`\`${b.language}\n${b.code}\n\`\`\``).join('\n\n');
        
        setMessages(prev => prev.map(msg => 
          msg.id === assistantMessage.id
            ? {
                ...msg,
                content: `I've analyzed the UI and generated the code:\n\n${codeContent}`,
                isStreaming: false
              }
            : msg
        ));
      }
    } catch (error) {
      setMessages(prev => prev.map(msg => 
        msg.id === assistantMessage.id
          ? { ...msg, content: 'Error generating code.', isStreaming: false }
          : msg
      ));
    } finally {
      setIsLoading(false);
      setCurrentStatus(null);
    }
  };

  const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve((reader.result as string).split(',')[1]);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  };

  // Handle follow-up question click
  const handleFollowUp = (question: string) => {
    setInput(question);
  };

  // Clear chat
  const handleClearChat = () => {
    setMessages([]);
    setConversationId(null);
    try {
      localStorage.removeItem(STORAGE_KEY);
      localStorage.removeItem(CONVERSATION_ID_KEY);
    } catch (e) { /* ignore */ }
  };

  // Collect all downloads and sources from messages
  const allDownloads = messages.flatMap(m => m.downloads || []);
  const allSearchSources = messages.flatMap(m => m.searchSources || []);

  // Get the last message's follow-up questions
  const lastAssistantMsg = [...messages].reverse().find(m => m.role === 'assistant' && !m.isStreaming);
  const followUpQuestions = lastAssistantMsg?.followUpQuestions || [];

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b px-4 py-3 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center">
            <span className="text-white font-bold text-sm">AI</span>
          </div>
          <div>
            <h1 className="font-semibold text-gray-900">McLeuker AI</h1>
            <p className="text-xs text-gray-500">Powered by Kimi 2.5</p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          {/* Clear Chat Button */}
          {messages.length > 0 && (
            <button
              onClick={handleClearChat}
              className="flex items-center gap-1 px-3 py-1.5 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition"
              title="Clear chat"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          )}

          {allDownloads.length > 0 && (
            <button
              onClick={() => setShowDownloads(!showDownloads)}
              className="flex items-center gap-1 px-3 py-1.5 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span className="text-sm font-medium">{allDownloads.length}</span>
            </button>
          )}
          
          {allSearchSources.length > 0 && (
            <button
              onClick={() => setShowSources(!showSources)}
              className="flex items-center gap-1 px-3 py-1.5 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <span className="text-sm font-medium">{allSearchSources.length} Sources</span>
            </button>
          )}
          
          <ModeSelector mode={mode} onChange={setMode} disabled={isLoading} />
        </div>
      </header>

      {/* Progress Bar */}
      {currentStatus && (
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 border-b px-4 py-2.5">
          <div className="flex items-center gap-3">
            {/* Animated spinner */}
            <div className="relative w-5 h-5 flex-shrink-0">
              <div className="absolute inset-0 rounded-full border-2 border-blue-200"></div>
              <div className="absolute inset-0 rounded-full border-2 border-blue-600 border-t-transparent animate-spin"></div>
            </div>
            
            <div className="flex-1 min-w-0">
              <p className="text-sm text-blue-800 font-medium truncate">{currentStatus}</p>
              {statusStep && (
                <div className="mt-1 flex items-center gap-2">
                  <div className="flex-1 h-1.5 bg-blue-100 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full transition-all duration-500 ease-out"
                      style={{ width: `${(statusStep.step / statusStep.total) * 100}%` }}
                    />
                  </div>
                  <span className="text-xs text-blue-600 font-mono flex-shrink-0">
                    {statusStep.step}/{statusStep.total}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Tool Indicators */}
      {!currentStatus && (activeTools.search || activeTools.fileGen || activeTools.code) && (
        <ToolIndicator 
          isSearching={activeTools.search}
          isGeneratingFile={activeTools.fileGen}
          isExecutingCode={activeTools.code}
        />
      )}

      {/* Side Panels */}
      {showDownloads && allDownloads.length > 0 && (
        <DownloadPanel 
          downloads={allDownloads} 
          onClose={() => setShowDownloads(false)}
        />
      )}
      
      {showSources && allSearchSources.length > 0 && (
        <SearchSourcesPanel 
          sources={allSearchSources}
          onClose={() => setShowSources(false)}
        />
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <WelcomeScreen onPromptClick={setInput} />
        )}
        <MessageList messages={messages} />
        
        {/* Follow-up Questions */}
        {followUpQuestions.length > 0 && !isLoading && (
          <div className="max-w-3xl mx-auto">
            <p className="text-xs text-gray-500 mb-2 font-medium">Suggested follow-ups:</p>
            <div className="flex flex-wrap gap-2">
              {followUpQuestions.map((q, i) => (
                <button
                  key={i}
                  onClick={() => handleFollowUp(q)}
                  className="text-sm text-blue-700 bg-blue-50 hover:bg-blue-100 px-3 py-1.5 rounded-full border border-blue-200 transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <InputArea
        input={input}
        onInputChange={setInput}
        onSend={handleSend}
        onFileUpload={handleFileUpload}
        onVisionToCode={handleVisionToCode}
        isLoading={isLoading}
        mode={mode}
      />
    </div>
  );
}

// ============================================================================
// WELCOME SCREEN
// ============================================================================

function WelcomeScreen({ onPromptClick }: { onPromptClick: (prompt: string) => void }) {
  const categories = [
    {
      title: 'Real-time Information',
      icon: '🔍',
      prompts: [
        "What's happening at Paris Fashion Week 2026?",
        "Latest AI breakthroughs this week",
        "Current stock market trends"
      ]
    },
    {
      title: 'File Generation',
      icon: '📊',
      prompts: [
        "Generate Excel of top 10 European fashion brands",
        "Create a PDF report on renewable energy",
        "Make a presentation about AI in healthcare"
      ]
    },
    {
      title: 'Research & Analysis',
      icon: '📚',
      prompts: [
        "Deep research on quantum computing applications",
        "Analyze the future of electric vehicles",
        "Compare different cloud providers"
      ]
    },
    {
      title: 'Code & Development',
      icon: '💻',
      prompts: [
        "Write a Python script to analyze CSV data",
        "Create a React component for a dashboard",
        "Build a SQL query for sales reporting"
      ]
    }
  ];

  return (
    <div className="max-w-4xl mx-auto py-8">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">What can I help you with?</h2>
        <p className="text-gray-500">Ask questions, generate files, analyze data, or upload images</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {categories.map((cat, i) => (
          <div key={i} className="bg-white rounded-xl p-4 shadow-sm border hover:shadow-md transition">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-2xl">{cat.icon}</span>
              <h3 className="font-semibold text-gray-900">{cat.title}</h3>
            </div>
            <div className="space-y-2">
              {cat.prompts.map((prompt, j) => (
                <button
                  key={j}
                  onClick={() => onPromptClick(prompt)}
                  className="w-full text-left text-sm text-gray-600 hover:text-blue-600 hover:bg-blue-50 p-2 rounded-lg transition"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
