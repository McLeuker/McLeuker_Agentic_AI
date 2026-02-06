'use client';

import React, { useState, useRef, useCallback } from 'react';
import { api, handleChatResponse, DownloadableFile } from '@/lib/api';
import { ModeSelector } from './ModeSelector';
import { MessageList } from './MessageList';
import { InputArea } from './InputArea';
import { ToolIndicator } from './ToolIndicator';
import { DownloadButton } from './DownloadButton';

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  reasoning?: string;
  isStreaming?: boolean;
  downloads?: DownloadableFile[];
  searchResults?: any;
  timestamp: Date;
}

export type ChatMode = 'instant' | 'thinking' | 'agent' | 'swarm' | 'research';

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [mode, setMode] = useState<ChatMode>('thinking');
  const [isLoading, setIsLoading] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [isGeneratingFile, setIsGeneratingFile] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const generateId = () => Math.random().toString(36).substring(2, 9);

  const handleSend = useCallback(async () => {
    if (!input.trim() || isLoading) return;

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
    setIsSearching(mode === 'agent' || mode === 'research' || mode === 'swarm');

    try {
      // Check if user is asking for a file
      const fileType = detectFileRequest(input);
      
      if (mode === 'swarm') {
        // Use swarm for complex tasks
        const result = await api.swarm(input, 5, true);
        if (result.success) {
          setMessages(prev => prev.map(msg => 
            msg.id === assistantMessage.id
              ? {
                  ...msg,
                  content: result.response.answer,
                  isStreaming: false,
                  metadata: result.response
                }
              : msg
          ));
        }
      } else if (fileType && mode === 'agent') {
        // Generate file directly
        setIsGeneratingFile(true);
        const chatResult = await api.chat(
          [...messages, userMessage].map(m => ({ role: m.role, content: m.content })),
          { mode: 'agent', enable_tools: true }
        );
        
        const handled = handleChatResponse(chatResult);
        setMessages(prev => prev.map(msg => 
          msg.id === assistantMessage.id
            ? {
                ...msg,
                content: handled.answer || '',
                downloads: handled.downloads,
                searchResults: handled.searchResults,
                isStreaming: false
              }
            : msg
        ));
        setIsGeneratingFile(false);
      } else {
        // Regular chat with streaming
        let fullContent = '';
        let fullReasoning = '';
        
        for await (const chunk of api.chatStream(
          [...messages, userMessage].map(m => ({ role: m.role, content: m.content })),
          { mode, enable_tools: true }
        )) {
          if (chunk.type === 'content') {
            fullContent += chunk.data;
            setMessages(prev => prev.map(msg => 
              msg.id === assistantMessage.id
                ? { ...msg, content: fullContent }
                : msg
            ));
          } else if (chunk.type === 'reasoning') {
            fullReasoning += chunk.data;
            setMessages(prev => prev.map(msg => 
              msg.id === assistantMessage.id
                ? { ...msg, reasoning: fullReasoning }
                : msg
            ));
          }
          scrollToBottom();
        }

        // Final update with any downloads
        const finalResult = await api.chat(
          [...messages, userMessage].map(m => ({ role: m.role, content: m.content })),
          { mode, enable_tools: true }
        );
        
        const handled = handleChatResponse(finalResult);
        setMessages(prev => prev.map(msg => 
          msg.id === assistantMessage.id
            ? {
                ...msg,
                content: handled.answer || fullContent,
                reasoning: handled.reasoning || fullReasoning,
                downloads: handled.downloads,
                searchResults: handled.searchResults,
                isStreaming: false
              }
            : msg
        ));
      }
    } catch (error) {
      setMessages(prev => prev.map(msg => 
        msg.id === assistantMessage.id
          ? { ...msg, content: 'Sorry, an error occurred. Please try again.', isStreaming: false }
          : msg
      ));
    } finally {
      setIsLoading(false);
      setIsSearching(false);
      setIsGeneratingFile(false);
    }
  }, [input, messages, mode, isLoading]);

  const detectFileRequest = (text: string): 'excel' | 'word' | 'pdf' | null => {
    const lower = text.toLowerCase();
    if (lower.includes('excel') || lower.includes('spreadsheet') || lower.includes('.xlsx')) return 'excel';
    if (lower.includes('word') || lower.includes('document') || lower.includes('.docx')) return 'word';
    if (lower.includes('pdf') || lower.includes('report') || lower.includes('.pdf')) return 'pdf';
    return null;
  };

  const handleFileUpload = async (file: File) => {
    // Handle image upload for multimodal
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
      const result = await api.multimodal('Analyze this image', file, mode);
      
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

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b px-4 py-3 flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold text-gray-900">McLeuker AI</h1>
          <p className="text-xs text-gray-500">Powered by Kimi 2.5</p>
        </div>
        <ModeSelector mode={mode} onChange={setMode} />
      </div>

      {/* Tool Indicators */}
      {(isSearching || isGeneratingFile) && (
        <ToolIndicator 
          isSearching={isSearching} 
          isGeneratingFile={isGeneratingFile} 
        />
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-12">
            <h2 className="text-2xl font-bold text-gray-800 mb-2">What can I help you with?</h2>
            <p className="text-gray-500 mb-6">Ask me anything, request files, or upload images</p>
            <div className="flex flex-wrap justify-center gap-2">
              {examplePrompts.map((prompt, i) => (
                <button
                  key={i}
                  onClick={() => setInput(prompt)}
                  className="px-4 py-2 bg-white border rounded-full text-sm text-gray-700 hover:bg-gray-100 transition"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
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
        isLoading={isLoading}
        mode={mode}
      />
    </div>
  );
}

const examplePrompts = [
  "What's happening at Paris Fashion Week 2026?",
  "Generate an Excel sheet of top 10 European fashion brands",
  "Research the latest AI trends and create a report",
  "Analyze this image and describe what you see"
];
