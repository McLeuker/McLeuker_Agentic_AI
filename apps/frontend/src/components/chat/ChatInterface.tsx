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

export default function ChatInterface({ conversationId, onConversationUpdate }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [mode, setMode] = useState<ChatMode>('agent'); // Default to agent for tool use
  const [isLoading, setIsLoading] = useState(false);
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

  // Auto-scroll when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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

    // Detect what tools might be needed
    const fileRequest = detectFileRequest(input);
    const needsSearch = mode === 'agent' || mode === 'research' || mode === 'swarm' ||
      /\b(what's happening|latest|recent|news|today|current|now|202[4-6])\b/i.test(input);
    
    setActiveTools({
      search: needsSearch,
      fileGen: fileRequest.type !== null,
      code: mode === 'code' || /\b(code|script|function|program)\b/i.test(input)
    });

    try {
      // For swarm mode, use the swarm endpoint
      if (mode === 'swarm') {
        const result = await api.swarm(input, 5, true, fileRequest.type !== null, 
          fileRequest.type === 'excel' ? 'spreadsheet' : fileRequest.type || undefined
        );
        
        if (result.success) {
          const deliverable = result.response.deliverable;
          setMessages(prev => prev.map(msg => 
            msg.id === assistantMessage.id
              ? {
                  ...msg,
                  content: result.response.answer,
                  downloads: deliverable ? [{
                    filename: deliverable.filename,
                    download_url: deliverable.download_url,
                    file_id: deliverable.file_id,
                    file_type: deliverable.type
                  }] : undefined,
                  isStreaming: false,
                  metadata: {
                    latency_ms: result.response.latency_ms,
                    tokens: result.response.metadata?.total_tokens
                  }
                }
              : msg
          ));
        }
      } 
      // For research mode
      else if (mode === 'research') {
        const result = await api.research(input, 'deep', fileRequest.type !== null);
        
        if (result.success) {
          const deliverable = result.response.deliverable;
          setMessages(prev => prev.map(msg => 
            msg.id === assistantMessage.id
              ? {
                  ...msg,
                  content: result.response.answer,
                  downloads: deliverable ? [{
                    filename: deliverable.filename,
                    download_url: deliverable.download_url,
                    file_id: deliverable.file_id,
                    file_type: deliverable.type
                  }] : undefined,
                  isStreaming: false
                }
              : msg
          ));
        }
      }
      // For streaming modes (thinking, instant, agent, code)
      else {
        let fullContent = '';
        let fullReasoning = '';
        let streamDownloads: DownloadableFile[] = [];
        let toolCallCount = 0;
        const enableTools = mode === 'agent' || mode === 'code';
        
        for await (const chunk of api.chatStream(
          [...messages, userMessage].map(m => ({ role: m.role, content: m.content })),
          { mode, enable_tools: enableTools }
        )) {
          if (chunk.type === 'content') {
            fullContent += chunk.data;
            setMessages(prev => prev.map(msg => 
              msg.id === assistantMessage.id
                ? { ...msg, content: fullContent, toolStatus: undefined }
                : msg
            ));
          } else if (chunk.type === 'reasoning') {
            fullReasoning += chunk.data;
            setMessages(prev => prev.map(msg => 
              msg.id === assistantMessage.id
                ? { ...msg, reasoning: fullReasoning }
                : msg
            ));
          } else if (chunk.type === 'tool_call') {
            toolCallCount++;
            const toolMsg = chunk.data?.message || 'Executing tool...';
            setMessages(prev => prev.map(msg => 
              msg.id === assistantMessage.id
                ? { ...msg, toolStatus: toolMsg }
                : msg
            ));
            // Update active tool indicators
            if (toolMsg.toLowerCase().includes('search') || toolMsg.toLowerCase().includes('source')) {
              setActiveTools(prev => ({ ...prev, search: true }));
            }
            if (toolMsg.toLowerCase().includes('generat') || toolMsg.toLowerCase().includes('build') || toolMsg.toLowerCase().includes('file')) {
              setActiveTools(prev => ({ ...prev, fileGen: true }));
            }
          } else if (chunk.type === 'download') {
            const dl = chunk.data as DownloadableFile;
            streamDownloads.push(dl);
            setMessages(prev => prev.map(msg => 
              msg.id === assistantMessage.id
                ? { ...msg, downloads: [...streamDownloads] }
                : msg
            ));
            setShowDownloads(true);
          } else if (chunk.type === 'complete') {
            // Final event with all data
            if (chunk.data?.content) fullContent = chunk.data.content;
            if (chunk.data?.reasoning) fullReasoning = chunk.data.reasoning;
            if (chunk.data?.downloads?.length) {
              streamDownloads = [...streamDownloads, ...chunk.data.downloads.filter(
                (d: DownloadableFile) => !streamDownloads.some(sd => sd.file_id === d.file_id)
              )];
            }
          }
        }

        setMessages(prev => prev.map(msg => 
          msg.id === assistantMessage.id
            ? {
                ...msg,
                content: fullContent,
                reasoning: fullReasoning,
                downloads: streamDownloads.length > 0 ? streamDownloads : undefined,
                toolStatus: undefined,
                isStreaming: false,
                metadata: {
                  tool_calls: toolCallCount > 0 ? toolCallCount : undefined
                }
              }
            : msg
        ));
      }
    } catch (error) {
      if ((error as Error).name !== 'AbortError') {
        setMessages(prev => prev.map(msg => 
          msg.id === assistantMessage.id
            ? { ...msg, content: 'Sorry, an error occurred. Please try again.', isStreaming: false }
            : msg
        ));
      }
    } finally {
      setIsLoading(false);
      setActiveTools({ search: false, fileGen: false, code: false });
      abortControllerRef.current = null;
    }
  }, [input, messages, mode, isLoading]);

  const handleFileUpload = async (file: File) => {
    const userMessage: Message = {
      id: generateId(),
      role: 'user',
      content: `[Image: ${file.name}]`,
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

    try {
      const result = await api.multimodal('Analyze this image in detail', file, mode);
      
      setMessages(prev => prev.map(msg => 
        msg.id === assistantMessage.id
          ? {
              ...msg,
              content: result.response?.answer || 'Analysis complete',
              isStreaming: false
            }
          : msg
      ));
    } catch (error) {
      setMessages(prev => prev.map(msg => 
        msg.id === assistantMessage.id
          ? { ...msg, content: 'Error analyzing image.', isStreaming: false }
          : msg
      ));
    } finally {
      setIsLoading(false);
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

  // Collect all downloads from messages
  const allDownloads = messages.flatMap(m => m.downloads || []);
  const allSearchSources = messages.flatMap(m => m.searchSources || []);

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
              <span className="text-sm font-medium">Sources</span>
            </button>
          )}
          
          <ModeSelector mode={mode} onChange={setMode} />
        </div>
      </header>

      {/* Tool Indicators */}
      {(activeTools.search || activeTools.fileGen || activeTools.code) && (
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
